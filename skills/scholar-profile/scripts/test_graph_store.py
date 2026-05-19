#!/usr/bin/env python3
"""Unit + integration tests for graph_store.py.

Pure functions are imported directly; stateful behavior is driven through the
CLI with an isolated SCHOLAR_PROFILE_DIR so the user's real
~/.config/scholar-profile is never touched and tests need no network.

Run:  pytest scripts/test_graph_store.py -v
  or:  python3 scripts/test_graph_store.py   (no-pytest fallback)
"""
import importlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("graph_store.py")


# --------------------------------------------------------------------------- #
# pure-function unit tests (import the module directly)
# --------------------------------------------------------------------------- #
def _mod():
    sys.path.insert(0, str(SCRIPT.parent))
    import graph_store
    return importlib.reload(graph_store)


def test_normalize_name_strips_accents_case_punct():
    """Accent/case/punctuation differences collapse to one key."""
    gs = _mod()
    assert gs.normalize_name("Yann LeCun") == gs.normalize_name("yann  lecun")
    assert gs.normalize_name("Léon Bottou") == "leon bottou"
    assert gs.normalize_name("Foo, J. (Jr.)") == "foo j jr"


def test_slugify_is_kebab():
    """slugify yields a filesystem-safe kebab id."""
    gs = _mod()
    assert gs.slugify("Yann LeCun") == "yann-lecun"
    assert gs.slugify("") == "unknown"


def test_canonical_edge_folds_mentorship():
    """advisor a->b and student b->a are the SAME canonical edge; collab sorted."""
    gs = _mod()
    assert gs.canonical_edge("a", "b", "advisor") == ("advisor", "a", "b")
    # student b->a means b is a's student => a advised b => advisor a->b
    assert gs.canonical_edge("b", "a", "student") == ("advisor", "a", "b")
    assert gs.canonical_edge("z", "a", "collaborator") == \
        gs.canonical_edge("a", "z", "collaborator")


# --------------------------------------------------------------------------- #
# CLI / stateful integration tests (isolated SCHOLAR_PROFILE_DIR)
# --------------------------------------------------------------------------- #
def _run(cfgdir, *args, stdin=None, expect_ok=True):
    env = dict(os.environ, SCHOLAR_PROFILE_DIR=str(cfgdir))
    p = subprocess.run([sys.executable, str(SCRIPT), *args], input=stdin,
                        capture_output=True, text=True, env=env)
    if expect_ok:
        assert p.returncode == 0, f"{args} failed: {p.stderr}"
    return p


def _graph(cfgdir):
    return json.loads((Path(cfgdir) / "graph.json").read_text())


def _tmp():
    return tempfile.mkdtemp(prefix="sp_test_")


def test_upsert_dedupes_and_merges_additively():
    """Same name upserted twice = one node; sources/relations unioned."""
    d = _tmp()
    _run(d, "upsert-node", "--json", "-",
         stdin='{"name":"Yann LeCun","sources":["http://a"],'
               '"relations":{"advisors":[{"name":"Geoffrey Hinton","source":"http://h"}]}}')
    _run(d, "upsert-node", "--json", "-",
         stdin='{"name":"yann  lecun","sources":["http://b"]}')
    g = _graph(d)
    assert len(g["nodes"]) == 1
    n = g["nodes"][0]
    assert set(n["sources"]) == {"http://a", "http://b"}
    assert n["relations"]["advisors"][0]["name"] == "Geoffrey Hinton"


def test_light_node_has_no_profile_md_full_node_does():
    """Placeholder nodes get empty profile_md (no 404 link); explicit one kept."""
    d = _tmp()
    _run(d, "upsert-node", "--json", "-", stdin='{"name":"Light Person","sources":["http://x"]}')
    _run(d, "upsert-node", "--json", "-",
         stdin='{"name":"Full Person","profile_md":"profiles/full-person.md","sources":["http://y"]}')
    by = {n["name"]: n for n in _graph(d)["nodes"]}
    assert by["Light Person"]["profile_md"] == ""
    assert by["Full Person"]["profile_md"] == "profiles/full-person.md"


def test_add_edge_refuses_unsourced():
    """Zero-hallucination: an unsourced solid edge is rejected."""
    d = _tmp()
    _run(d, "upsert-node", "--json", "-", stdin='{"name":"A","sources":["http://a"]}')
    _run(d, "upsert-node", "--json", "-", stdin='{"name":"B","sources":["http://b"]}')
    p = _run(d, "add-edge", "--src", "a", "--dst", "b", "--type", "advisor",
             expect_ok=False)
    assert p.returncode != 0
    assert _graph(d)["edges"] == []
    # with a source it succeeds
    _run(d, "add-edge", "--src", "a", "--dst", "b", "--type", "advisor",
         "--source", "http://src")
    assert len(_graph(d)["edges"]) == 1


def test_student_and_advisor_collapse_to_one_edge():
    """advisor A->B then student B->A must NOT create a duplicate."""
    d = _tmp()
    _run(d, "upsert-node", "--json", "-", stdin='{"name":"A","sources":["http://a"]}')
    _run(d, "upsert-node", "--json", "-", stdin='{"name":"B","sources":["http://b"]}')
    _run(d, "add-edge", "--src", "a", "--dst", "b", "--type", "advisor", "--source", "http://1")
    _run(d, "add-edge", "--src", "b", "--dst", "a", "--type", "student", "--source", "http://2")
    edges = _graph(d)["edges"]
    assert len(edges) == 1
    assert edges[0]["type"] == "advisor" and edges[0]["src"] == "a" and edges[0]["dst"] == "b"
    assert set(edges[0]["sources"]) == {"http://1", "http://2"}


def test_detect_connections_autolinks_only_sourced_and_dedupes():
    """The headline behavior: a later scholar auto-links to an earlier one via
    the source the earlier node declared, exactly once, and unsourced
    same-affiliation guesses are NOT auto-applied."""
    d = _tmp()
    _run(d, "upsert-node", "--json", "-",
         stdin='{"name":"Yann LeCun","affiliation":"NYU","sources":["http://l"],'
               '"relations":{"advisors":[{"name":"Geoffrey Hinton","source":"http://hl",'
               '"note":"postdoc"}]}}')
    _run(d, "upsert-node", "--json", "-",
         stdin='{"name":"Geoffrey Hinton","affiliation":"NYU","sources":["http://h"]}')
    out = _run(d, "detect-connections", "--node", "geoffrey-hinton", "--apply").stdout
    res = json.loads(out)
    assert res["applied"] == 1                       # only the sourced advisor edge
    edges = _graph(d)["edges"]
    advisor = [e for e in edges if e["type"] == "advisor"]
    assert len(advisor) == 1
    assert advisor[0]["src"] == "geoffrey-hinton" and advisor[0]["dst"] == "yann-lecun"
    assert advisor[0]["sources"] == ["http://hl"] and advisor[0]["inferred"] is False
    # same-affiliation NYU pair must remain only an inferred (un-applied) proposal
    assert not any(e["inferred"] for e in edges)
    # re-running on the other endpoint must not create a duplicate
    _run(d, "detect-connections", "--node", "yann-lecun", "--apply")
    assert len([e for e in _graph(d)["edges"] if e["type"] == "advisor"]) == 1


def test_render_viewer_is_zero_dependency_and_safe():
    """Viewer must be self-contained: no CDN/script src, embedded JSON valid,
    and '</' escaped so a source URL can't break out of the <script>."""
    d = _tmp()
    _run(d, "upsert-node", "--json", "-",
         stdin='{"name":"Test Scholar","scholar_url":"https://scholar.google.com/x",'
               '"profile_md":"profiles/test-scholar.md","sources":["http://x</script>y"]}')
    path = _run(d, "render-viewer").stdout.strip()
    html = Path(path).read_text()
    assert 'src="http' not in html and "unpkg" not in html and "vis-network" not in html
    start = html.index("const G=") + len("const G=")
    end = html.index(";\nconst NS=")
    data = json.loads(html[start:end].replace("<\\/", "</"))
    assert data["nodes"][0]["name"] == "Test Scholar"
    assert "</script" not in html[start:end]            # escaped, no breakout
    assert "打开画像文件" in html and "Google Scholar 搜索" in html  # panel links present


# --------------------------------------------------------------------------- #
def _main():
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {fn.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"ERROR {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    _main()

#!/usr/bin/env python3
"""graph_store.py — global scholar relationship graph store (stdlib only).

State lives OUTSIDE the skills repo at ~/.config/scholar-profile/ so the repo
stays free of personal data and hardcoded paths (resolved at runtime via
expanduser). One JSON file is the single source of truth; viewer.html is a
regenerated artifact.

Subcommands
-----------
  upsert-node        --json <file|->            add/merge a scholar node, prints node id
  add-edge           --src ID --dst ID --type T  add a sourced relationship edge
  detect-connections --node ID                   propose edges to existing nodes
  render-viewer                                  (re)write single-file viewer.html
  list-nodes                                     print id / name / affiliation

Design notes
------------
* Node dedup key = normalized name (accent-stripped, lowercase, punct-free).
  Merging is additive: sources / aliases / relations are unioned, never dropped.
* Edges are DIRECTED. type ∈ {advisor, student, collaborator}.
    advisor:       src is the advisor OF dst   (mentor -> mentee)
    student:       src is the student OF dst   (mentee -> mentor)
    collaborator:  undirected in meaning; stored src->dst, rendered dashed
  An edge with no `sources` is NEVER created as a solid fact. detect-connections
  only *proposes*; the caller decides what to commit (zero-hallucination rule).
* A node may carry researched relation hints under `relations`:
    {"advisors":[{"name","source","note"}], "students":[...], "collaborators":[...]}
  detect-connections matches those names against existing node names so that a
  later-added person auto-links to an earlier one — with the original source.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import unicodedata

# Default state dir is OUTSIDE the repo. SCHOLAR_PROFILE_DIR overrides it
# (used for isolated test runs / multiple separate graphs).
CONFIG_DIR = os.environ.get("SCHOLAR_PROFILE_DIR") or os.path.expanduser(
    "~/.config/scholar-profile"
)
GRAPH_PATH = os.path.join(CONFIG_DIR, "graph.json")
VIEWER_PATH = os.path.join(CONFIG_DIR, "viewer.html")
PROFILES_DIR = os.path.join(CONFIG_DIR, "profiles")

EDGE_TYPES = ("advisor", "student", "collaborator")


# --------------------------------------------------------------------------- #
# storage helpers
# --------------------------------------------------------------------------- #
def _now() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _ensure_dirs() -> None:
    os.makedirs(PROFILES_DIR, exist_ok=True)


def load_graph() -> dict:
    if not os.path.exists(GRAPH_PATH):
        return {"version": 1, "updated_at": _now(), "nodes": [], "edges": []}
    with open(GRAPH_PATH, encoding="utf-8") as fh:
        g = json.load(fh)
    g.setdefault("nodes", [])
    g.setdefault("edges", [])
    return g


def save_graph(g: dict) -> None:
    _ensure_dirs()
    g["updated_at"] = _now()
    tmp = GRAPH_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(g, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, GRAPH_PATH)  # atomic; never lose existing data on crash


def normalize_name(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9一-鿿]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def slugify(name: str) -> str:
    base = normalize_name(name).replace(" ", "-")
    return base or "unknown"


def find_node(g: dict, name: str) -> dict | None:
    key = normalize_name(name)
    for n in g["nodes"]:
        if normalize_name(n["name"]) == key:
            return n
        if any(normalize_name(a) == key for a in n.get("aliases", [])):
            return n
    return None


def get_node(g: dict, node_id: str) -> dict | None:
    for n in g["nodes"]:
        if n["id"] == node_id:
            return n
    return None


def _union(dst: list, src: list) -> list:
    seen = {json.dumps(x, sort_keys=True, ensure_ascii=False) for x in dst}
    for x in src or []:
        k = json.dumps(x, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            dst.append(x)
            seen.add(k)
    return dst


# --------------------------------------------------------------------------- #
# subcommands
# --------------------------------------------------------------------------- #
def cmd_upsert_node(args) -> None:
    raw = sys.stdin.read() if args.json == "-" else open(args.json, encoding="utf-8").read()
    payload = json.loads(raw)
    name = payload.get("name", "").strip()
    if not name:
        sys.exit("upsert-node: payload requires a non-empty 'name'")

    g = load_graph()
    node = find_node(g, name)
    if node is None:
        node = {
            "id": slugify(name),
            "name": name,
            "affiliation": "",
            "aliases": [],
            "scholar_url": "",
            # Only set once a real profile .md is written (caller passes it),
            # so the viewer's "打开画像文件" link never points at a 404 for a
            # placeholder relation-node.
            "profile_md": "",
            "sources": [],
            "relations": {"advisors": [], "students": [], "collaborators": []},
            "notes": "",
        }
        # guarantee id uniqueness if two different people share a slug
        existing = {n["id"] for n in g["nodes"]}
        if node["id"] in existing:
            i = 2
            while f"{node['id']}-{i}" in existing:
                i += 1
            node["id"] = f"{node['id']}-{i}"
        g["nodes"].append(node)

    for fld in ("affiliation", "scholar_url", "notes", "profile_md"):
        if payload.get(fld):
            node[fld] = payload[fld]
    node["aliases"] = _union(node.get("aliases", []), payload.get("aliases", []))
    node["sources"] = _union(node.get("sources", []), payload.get("sources", []))
    rel = node.setdefault("relations", {"advisors": [], "students": [], "collaborators": []})
    for bucket in ("advisors", "students", "collaborators"):
        rel[bucket] = _union(rel.get(bucket, []), payload.get("relations", {}).get(bucket, []))

    save_graph(g)
    print(node["id"])


def canonical_edge(src: str, dst: str, typ: str) -> tuple[str, str, str]:
    """Normalize an edge so the same relationship is never stored twice.

    Mentorship is stored ONLY as `advisor` with src=advisor, dst=advisee.
    A `student src->dst` (src is dst's student) is the SAME fact as
    `advisor dst->src`, so we fold it. Collaborator is undirected, so we
    store the node pair sorted. This is what kills the iter-1 bug where
    detect-connections emitted both `advisor H->L` and `student L->H`.
    """
    if typ in ("advisor", "student"):
        if typ == "student":
            src, dst = dst, src  # student a->b  ==  advisor b->a
        return ("advisor", src, dst)
    a, b = sorted((src, dst))
    return ("collaborator", a, b)


def _find_canon_edge(g: dict, key: tuple[str, str, str]):
    for e in g["edges"]:
        if canonical_edge(e["src"], e["dst"], e["type"]) == key:
            return e
    return None


def _add_or_merge_edge(g, src, dst, typ, sources, note, inferred) -> str:
    """Idempotent edge writer used by both add-edge and detect --apply."""
    etype, a, b = canonical_edge(src, dst, typ)
    existing = _find_canon_edge(g, (etype, a, b))
    if existing:
        existing["sources"] = _union(existing.get("sources", []), sources)
        if note:
            existing["note"] = note
        if sources:
            existing["inferred"] = False
        return f"updated {existing['id']}"
    eid = f"{etype}:{a}->{b}"
    g["edges"].append({
        "id": eid, "src": a, "dst": b, "type": etype,
        "sources": sources, "inferred": bool(inferred and not sources),
        "note": note or "",
    })
    return f"created {eid}"


def cmd_add_edge(args) -> None:
    if args.type not in EDGE_TYPES:
        sys.exit(f"add-edge: --type must be one of {EDGE_TYPES}")
    sources = [s for s in (args.source or []) if s.strip()]
    if not sources and not args.allow_unsourced:
        sys.exit(
            "add-edge: refusing to create an unsourced edge. Provide --source URL "
            "(zero-hallucination rule). Use --allow-unsourced ONLY for an edge you "
            "will visibly mark as inferred."
        )
    g = load_graph()
    if not get_node(g, args.src) or not get_node(g, args.dst):
        sys.exit("add-edge: --src / --dst must be existing node ids (see list-nodes)")
    msg = _add_or_merge_edge(g, args.src, args.dst, args.type, sources,
                             args.note, args.allow_unsourced)
    save_graph(g)
    print(msg)


def _existing_edge(g, src, dst, typ) -> bool:
    return _find_canon_edge(g, canonical_edge(src, dst, typ)) is not None


def cmd_detect_connections(args) -> None:
    """Propose edges between args.node and the rest of the graph.

    Only emits proposals; never writes (unless --apply, and then only the
    source-backed ones). This keeps the agent in control of every asserted fact.
    """
    g = load_graph()
    me = get_node(g, args.node)
    if me is None:
        sys.exit(f"detect-connections: no node with id {args.node!r}")

    proposals: list[dict] = []
    seen: set = set()  # canonical keys already proposed this run (dedupe batch)

    def emit(src, dst, typ, sources, note, inferred):
        etype, a, b = canonical_edge(src, dst, typ)
        key = (etype, a, b)
        if key in seen:
            return
        if not inferred and _existing_edge(g, src, dst, typ):
            return  # already a solid edge; nothing to propose
        seen.add(key)
        proposals.append({
            "src": a, "dst": b, "type": etype,
            "sources": sources, "note": note, "inferred": inferred,
        })

    others = [n for n in g["nodes"] if n["id"] != me["id"]]

    # 1. relation hints declared on ME pointing at someone already in the graph.
    #    Mentorship is normalized to `advisor` (advisor -> advisee).
    rel = me.get("relations", {})
    for entry in rel.get("advisors", []):  # T advised ME
        t = find_node(g, entry.get("name", ""))
        if t and t["id"] != me["id"]:
            src = [entry["source"]] if entry.get("source") else []
            emit(t["id"], me["id"], "advisor", src, entry.get("note", ""), not src)
    for entry in rel.get("students", []):  # ME advised T
        t = find_node(g, entry.get("name", ""))
        if t and t["id"] != me["id"]:
            src = [entry["source"]] if entry.get("source") else []
            emit(me["id"], t["id"], "advisor", src, entry.get("note", ""), not src)
    for entry in rel.get("collaborators", []):
        t = find_node(g, entry.get("name", ""))
        if t and t["id"] != me["id"]:
            src = [entry["source"]] if entry.get("source") else []
            emit(me["id"], t["id"], "collaborator", src, entry.get("note", ""), not src)

    # 2. relation hints declared on OTHERS pointing at ME
    for o in others:
        orel = o.get("relations", {})
        for entry in orel.get("advisors", []):  # O's advisor is ME -> ME advised O
            if find_node(g, entry.get("name", "")) is me:
                src = [entry["source"]] if entry.get("source") else []
                emit(me["id"], o["id"], "advisor", src, entry.get("note", ""), not src)
        for entry in orel.get("students", []):  # O's student is ME -> O advised ME
            if find_node(g, entry.get("name", "")) is me:
                src = [entry["source"]] if entry.get("source") else []
                emit(o["id"], me["id"], "advisor", src, entry.get("note", ""), not src)
        for entry in orel.get("collaborators", []):
            if find_node(g, entry.get("name", "")) is me:
                src = [entry["source"]] if entry.get("source") else []
                emit(o["id"], me["id"], "collaborator", src, entry.get("note", ""), not src)

    # 3. weak heuristic: same affiliation -> inferred candidate, NEVER auto-solid
    for o in others:
        if me.get("affiliation") and o.get("affiliation"):
            a, b = me["affiliation"].lower(), o["affiliation"].lower()
            if a and (a in b or b in a):
                emit(me["id"], o["id"], "collaborator", [],
                     f"弱关联：同机构（{me['affiliation']}）；断言前需另找来源核实", True)

    if args.apply:
        applied = 0
        for p in proposals:
            if p["sources"] and not p["inferred"]:
                _add_or_merge_edge(g, p["src"], p["dst"], p["type"],
                                   p["sources"], p["note"], False)
                applied += 1
        if applied:
            save_graph(g)
        print(json.dumps({"applied": applied, "proposals": proposals},
                          ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"proposals": proposals}, ensure_ascii=False, indent=2))


def cmd_list_nodes(args) -> None:
    g = load_graph()
    for n in g["nodes"]:
        print(f"{n['id']}\t{n['name']}\t{n.get('affiliation', '')}")
    print(f"({len(g['nodes'])} nodes, {len(g['edges'])} edges)", file=sys.stderr)


# --------------------------------------------------------------------------- #
# viewer
# --------------------------------------------------------------------------- #
_VIEWER_TMPL = r"""<!doctype html>
<html lang="zh"><head><meta charset="utf-8">
<title>学者关系图</title>
<style>
 html,body{margin:0;height:100%;font-family:-apple-system,"PingFang SC",Segoe UI,sans-serif;background:#fafaf8}
 #svg{width:100vw;height:100vh;display:block;cursor:grab}
 #svg.grab{cursor:grabbing}
 .edge{stroke-width:2;fill:none}
 .node circle{stroke:#fff;stroke-width:2;cursor:pointer}
 .node text{font-size:13px;fill:#222;pointer-events:none;text-anchor:middle}
 .node:hover circle{stroke:#333}
 #panel{position:fixed;top:0;right:0;width:340px;max-height:100vh;overflow:auto;
  background:#fff;border-left:1px solid #ddd;padding:16px 18px;
  box-shadow:-2px 0 10px rgba(0,0,0,.08);transform:translateX(370px);transition:.18s}
 #panel.open{transform:translateX(0)}
 #panel h2{font-size:16px;margin:.1em 0}
 #panel .aff{color:#666;font-size:13px;margin:4px 0 8px}
 #panel b{font-size:12px;color:#888;display:block;margin-top:10px}
 #panel a{display:block;font-size:12px;color:#1a73e8;word-break:break-all;margin:3px 0}
 #panel .x{float:right;cursor:pointer;color:#999;font-size:15px}
 .box{position:fixed;background:#fff;border:1px solid #ddd;border-radius:7px;
  padding:8px 12px;font-size:12px;color:#555}
 #hint{left:14px;top:14px}
 #legend{left:14px;bottom:14px;line-height:1.7}
 #legend i{display:inline-block;width:24px;height:0;border-top:3px solid;
  margin-right:6px;vertical-align:middle;font-style:normal}
</style></head><body>
<div class="box" id="hint">拖动节点摆位 · 拖空白处平移 · 滚轮缩放 · 点节点/连线看来源</div>
<svg id="svg"><g id="view">
 <defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7"
  markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#c0392b"/></marker>
 <marker id="arrg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7"
  markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#bbb"/></marker></defs>
 <g id="edges"></g><g id="nodes"></g>
</g></svg>
<div class="box" id="legend">
 <div><i style="border-color:#c0392b"></i>advisor 师承（导师→学生）</div>
 <div><i style="border-color:#888;border-top-style:dashed"></i>collaborator 合作者</div>
 <div style="color:#999;margin-top:2px">inferred 未证实（仅供核实，默认不自动连）</div>
</div>
<div id="panel"><span class="x" onclick="this.parentNode.classList.remove('open')">✕</span>
 <div id="pb"></div></div>
<script>
/* 零依赖：纯内联 SVG 渲染，无任何 CDN / 外部库，离线 / file:// 可用。 */
const G=__GRAPH_JSON__;
const NS="http://www.w3.org/2000/svg";
const esc=s=>(s||"").replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const links=a=>(a&&a.length)?a.map(u=>`<a href="${esc(u)}" target="_blank" rel="noopener">${esc(u)}</a>`).join(""):"<i>（无来源）</i>";
const byId={};G.nodes.forEach(n=>byId[n.id]=n);
const adv=G.edges.filter(e=>e.type==="advisor"&&!e.inferred);

/* 层级布局：advisor 边 a->b 让 b 比 a 低一层，形成"家谱"自上而下。*/
const lvl={};G.nodes.forEach(n=>lvl[n.id]=0);
for(let i=0;i<G.nodes.length;i++)for(const e of adv)
  if(byId[e.src]&&byId[e.dst])lvl[e.dst]=Math.max(lvl[e.dst],lvl[e.src]+1);
const rows={};G.nodes.forEach(n=>{(rows[lvl[n.id]]=rows[lvl[n.id]]||[]).push(n);});
const W=Math.max(900,window.innerWidth),GAPY=150;
Object.keys(rows).forEach(L=>{const r=rows[L],n=r.length;
  r.forEach((nd,i)=>{nd.x=W/(n+1)*(i+1)+(L%2?40:0);nd.y=80+L*GAPY;});});

const svg=document.getElementById("svg"),view=document.getElementById("view");
const eG=document.getElementById("edges"),nG=document.getElementById("nodes");
function edgeStyle(e){if(e.inferred)return{c:"#bbb",d:"3 4",m:""};
  if(e.type==="advisor")return{c:"#c0392b",d:"",m:"url(#arr)"};
  return{c:"#888",d:"6 4",m:""};}
const eEls=[];
G.edges.forEach(e=>{if(!byId[e.src]||!byId[e.dst])return;
  const ln=document.createElementNS(NS,"line");ln.setAttribute("class","edge");
  const st=edgeStyle(e);ln.setAttribute("stroke",st.c);
  if(st.d)ln.setAttribute("stroke-dasharray",st.d);
  if(st.m)ln.setAttribute("marker-end",st.m);
  ln.style.cursor="pointer";ln.addEventListener("click",ev=>{ev.stopPropagation();
   showEdge(e);});eG.appendChild(ln);eEls.push({e,ln});});
const nEls=[];
G.nodes.forEach(n=>{const g=document.createElementNS(NS,"g");g.setAttribute("class","node");
  const c=document.createElementNS(NS,"circle");c.setAttribute("r",22);
  c.setAttribute("fill", lvl[n.id]===0?"#2c6fbb":"#3a8f63");
  const t=document.createElementNS(NS,"text");t.setAttribute("dy",38);
  t.textContent=n.name;g.appendChild(c);g.appendChild(t);nG.appendChild(g);
  g.addEventListener("click",ev=>{ev.stopPropagation();showNode(n);});
  nEls.push({n,g,c,t});});
function place(){eEls.forEach(({e,ln})=>{const a=byId[e.src],b=byId[e.dst];
   ln.setAttribute("x1",a.x);ln.setAttribute("y1",a.y);
   ln.setAttribute("x2",b.x);ln.setAttribute("y2",b.y);});
  nEls.forEach(({n,g})=>g.setAttribute("transform",`translate(${n.x},${n.y})`));}
place();

/* 视图平移/缩放 + 节点拖拽 */
let vb={x:0,y:0,w:window.innerWidth,h:window.innerHeight,s:1};
function applyVB(){view.setAttribute("transform",
  `translate(${-vb.x},${-vb.y}) scale(${vb.s})`);}
applyVB();
let drag=null,pan=null;
svg.addEventListener("mousedown",ev=>{
  const t=ev.target.closest(".node");
  if(t){const nd=nEls.find(o=>o.g===t).n;drag={nd};svg.classList.add("grab");}
  else{pan={x:ev.clientX,y:ev.clientY};svg.classList.add("grab");}});
window.addEventListener("mousemove",ev=>{
  if(drag){drag.nd.x+=ev.movementX/vb.s;drag.nd.y+=ev.movementY/vb.s;place();}
  else if(pan){vb.x-=ev.movementX;vb.y-=ev.movementY;applyVB();}});
window.addEventListener("mouseup",()=>{drag=pan=null;svg.classList.remove("grab");});
svg.addEventListener("wheel",ev=>{ev.preventDefault();
  const f=ev.deltaY<0?1.12:0.89;vb.s=Math.min(3,Math.max(.3,vb.s*f));applyVB();},
  {passive:false});

const panel=document.getElementById("panel"),pb=document.getElementById("pb");
function open(h){pb.innerHTML=h;panel.classList.add("open");}
function showNode(n){
  const sch=n.scholar_url
    ?`<a href="${esc(n.scholar_url)}" target="_blank" rel="noopener">▸ Google Scholar 主页</a>`
    :`<a href="https://scholar.google.com/scholar?q=${encodeURIComponent(n.name+" "+(n.affiliation||""))}" target="_blank" rel="noopener">▸ Google Scholar 搜索（主页未确认）</a>`;
  const prof=n.profile_md
    ?`<a href="${esc(n.profile_md)}" target="_blank" rel="noopener">▸ 打开画像文件（${esc(n.profile_md)}）</a>`
    :"";
  open(`<h2>${esc(n.name)}</h2>
  <div class="aff">${esc(n.affiliation||"（机构未记录）")}</div>`+
  `<b>链接</b>${sch}${prof}`+
  `<b>来源</b>${links(n.sources)}`);}
function showEdge(e){const lbl=e.type==="advisor"?"师承（导师→学生）":
   e.type==="collaborator"?"合作者":e.type;
  open(`<h2>${esc(lbl)}${e.inferred?" · 未证实":""}</h2>
  <div class="aff">${esc((byId[e.src]||{}).name||e.src)} → ${esc((byId[e.dst]||{}).name||e.dst)}</div>
  <div class="aff">${esc(e.note||"")}</div><b>来源</b>${links(e.sources)}`);}
svg.addEventListener("click",e=>{if(e.target===svg||e.target===view)
  panel.classList.remove("open");});
</script></body></html>"""


def cmd_render_viewer(args) -> None:
    g = load_graph()
    _ensure_dirs()
    # Embed data as a JS literal. Escaping "</" prevents any source URL / note
    # from prematurely closing the <script> tag (iter-1 blank-page bug class).
    data = json.dumps(g, ensure_ascii=False).replace("</", "<\\/")
    html = _VIEWER_TMPL.replace("__GRAPH_JSON__", data)
    with open(VIEWER_PATH, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(VIEWER_PATH)


# --------------------------------------------------------------------------- #
def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="graph_store")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("upsert-node")
    s.add_argument("--json", required=True, help="path to node JSON, or - for stdin")
    s.set_defaults(func=cmd_upsert_node)

    s = sub.add_parser("add-edge")
    s.add_argument("--src", required=True)
    s.add_argument("--dst", required=True)
    s.add_argument("--type", required=True, choices=EDGE_TYPES)
    s.add_argument("--source", action="append", default=[], help="evidence URL (repeatable)")
    s.add_argument("--note", default="")
    s.add_argument("--allow-unsourced", action="store_true",
                   help="permit an inferred edge (will be rendered dotted/grey)")
    s.set_defaults(func=cmd_add_edge)

    s = sub.add_parser("detect-connections")
    s.add_argument("--node", required=True)
    s.add_argument("--apply", action="store_true",
                   help="auto-create only the source-backed proposals")
    s.set_defaults(func=cmd_detect_connections)

    s = sub.add_parser("render-viewer")
    s.set_defaults(func=cmd_render_viewer)

    s = sub.add_parser("list-nodes")
    s.set_defaults(func=cmd_list_nodes)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()

package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadMinimal(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "config.toml")
	os.WriteFile(path, []byte(`
default_node = "node1"
default_dir = "/home/user/project"
agent_path = "/shared/.agent/agent.py"
log_level = "info"
socket_path = "~/.config/rca/rca.sock"

[ssh]
alive_interval = 30
alive_count_max = 3
max_retries = 3
retry_backoff = [2, 4, 8]

[nodes.node1]
ssh = "ssh -p 10001 127.0.0.1"

[nodes.node2]
ssh = "ssh -p 10002 127.0.0.1"
`), 0644)

	c, err := Load(path)
	if err != nil {
		t.Fatal(err)
	}
	if c.DefaultNode != "node1" {
		t.Errorf("default_node=%s", c.DefaultNode)
	}
	if c.SSH.AliveInterval != 30 {
		t.Errorf("alive_interval=%d", c.SSH.AliveInterval)
	}
	if len(c.Nodes) != 2 {
		t.Errorf("nodes=%d, want 2", len(c.Nodes))
	}
	if c.Nodes["node1"].SSH != "ssh -p 10001 127.0.0.1" {
		t.Errorf("node1.ssh=%q", c.Nodes["node1"].SSH)
	}
	if len(c.SSH.RetryBackoff) != 3 || c.SSH.RetryBackoff[2] != 8 {
		t.Errorf("retry_backoff=%v", c.SSH.RetryBackoff)
	}
}

func TestExpandHome(t *testing.T) {
	home, _ := os.UserHomeDir()
	got := ExpandHome("~/foo/bar")
	want := filepath.Join(home, "foo/bar")
	if got != want {
		t.Errorf("ExpandHome=%q, want %q", got, want)
	}
}

func TestDefaultPath(t *testing.T) {
	p := DefaultPath()
	home, _ := os.UserHomeDir()
	want := filepath.Join(home, ".config/rca/config.toml")
	if p != want {
		t.Errorf("DefaultPath=%q, want %q", p, want)
	}
}

func TestCondaAndProjectFields(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "config.toml")
	os.WriteFile(path, []byte(`
default_node = "train"

[nodes.train]
ssh = "ssh gpu-train"
dir = "/home/user"
conda_sh = "~/miniconda3/etc/profile.d/conda.sh"
conda_env = "default-env"

[nodes.eval]
ssh = "ssh gpu-eval"

[projects.my-proj]
default_node = "train"
dir = "/home/user/my-proj"
conda_env = "my-proj-env"
mutagen_session = "my-proj"

[projects.no-conda-override]
default_node = "train"
dir = "/home/user/no-conda-override"
mutagen_session = "no-conda-override"
`), 0644)

	c, err := Load(path)
	if err != nil {
		t.Fatal(err)
	}

	train := c.Nodes["train"]
	if train.CondaSh != "~/miniconda3/etc/profile.d/conda.sh" {
		t.Errorf("nodes.train.conda_sh=%q", train.CondaSh)
	}
	if train.CondaEnv != "default-env" {
		t.Errorf("nodes.train.conda_env=%q", train.CondaEnv)
	}

	myProj := c.Projects["my-proj"]
	if myProj.DefaultNode != "train" {
		t.Errorf("projects.my-proj.default_node=%q", myProj.DefaultNode)
	}
	if myProj.CondaEnv != "my-proj-env" {
		t.Errorf("projects.my-proj.conda_env=%q", myProj.CondaEnv)
	}
	if myProj.MutagenSession != "my-proj" {
		t.Errorf("projects.my-proj.mutagen_session=%q", myProj.MutagenSession)
	}

	// Project override wins.
	if got := train.EffectiveCondaEnv(myProj.CondaEnv); got != "my-proj-env" {
		t.Errorf("EffectiveCondaEnv with project override=%q, want my-proj-env", got)
	}

	// No project override → fall back to node-level.
	noOverride := c.Projects["no-conda-override"]
	if got := train.EffectiveCondaEnv(noOverride.CondaEnv); got != "default-env" {
		t.Errorf("EffectiveCondaEnv without project override=%q, want default-env", got)
	}

	// Node with neither set → empty.
	eval := c.Nodes["eval"]
	if got := eval.EffectiveCondaEnv(""); got != "" {
		t.Errorf("EffectiveCondaEnv with no values=%q, want empty", got)
	}
}

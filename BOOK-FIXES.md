# Book fixes

## Chapter 6: /explain-arch can't use Glob

**What the book prints.** `.claude/skills/explain-arch/SKILL.md` with `context: fork`, `allowed-tools: Read Glob Grep` and `disallowed-tools: Edit Write Bash`. Its body says "Map every file under $ARGUMENTS with Glob."

**What happens when you run it.** The book's files, Claude Code 2.1.327 on macOS, `claude -p "/explain-arch src" --setting-sources project`:

- The session's tool list has no `Glob` and no `Grep`.
- The fork's first call is Bash, and it comes back `Permission to use Bash has been denied.`
- It finishes by starting an `Explore` subagent the skill never asks for: "I didn't have Glob or Bash, so an Explore agent did the listing."

Glob and Grep aren't in the default tool set on macOS, Linux and WSL; `allowed-tools` doesn't add them.

**What this repo does.** It adds [`ch06/.claude/agents/repo-mapper.md`](ch06/.claude/agents/repo-mapper.md), a subagent with `tools: Read, Glob, Grep`, and one line, under a `# repo:` comment, after `context: fork`:

```yaml
agent: repo-mapper
```

Everything else is as printed. With the fix, the fork calls `Glob {"pattern": "src/**/*"}` and then `Read`, nothing is denied, and it returns one line per file plus a note that `src/db.js` doesn't exist. `agent: Explore` doesn't work: still no Glob, Bash denied, and the answer is "I couldn't map the files under `src`."

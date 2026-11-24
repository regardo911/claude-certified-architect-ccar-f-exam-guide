# Changelog: the guide's wording vs today's product

The book targets `claude-agent-sdk` 0.2.187, `mcp` 2.3.0, `anthropic` 2.12.0, `pydantic` 2.14.4 and Claude Code 2.1.327. Each line: the exam's answer → what the product does today. On exam day, pick the exam's answer.

## Chapter 3

- `-p` runs Claude Code in a pipeline → still true; a run with redirected output also runs non-interactively.
- "Change the temperature" is never right → today's API has no `temperature` parameter.

## Chapter 4

- The spawning tool is `Task` → it's `Agent`; `Task` still shows in the startup list and works as an alias.
- `allowedTools` restricts an agent → `allowed_tools` only auto-approves; `tools` (on the options or the `AgentDefinition`) restricts.
- Parallel subagent calls return their results → subagents run in the background by default and the stream can carry several `ResultMessage`s; `support_agent.py` sets `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`.

## Chapter 5

- Return `errorCategory` and `isRetryable` as error metadata → `isError` is MCP's own flag; the other two are JSON you put inside the error text.
- (no SDK named) → `mcp` 2.x renamed `FastMCP` to `MCPServer`; `from mcp.server.fastmcp import FastMCP` fails.
- `tool_choice` `"any"` and forced choice → the newest Sonnet, Opus and Fable models reject both; Haiku accepts them. Elsewhere use `"auto"` with strict tool use, or structured outputs.
- Tools from every configured server are discovered at connection time → names load at startup; full definitions load on demand through tool search.
- A project `.mcp.json` is shared team tooling → still true, and each developer approves the server once before it connects.

## Chapter 6

- Commands and skills are separate → commands were merged into skills; `.claude/commands/` files still work, and a skill wins a name clash.
- `allowed-tools` restricts a skill's tools → it grants them without a prompt and leaves the rest callable; `disallowed-tools` removes tools.
- `CLAUDE.md` gives CI its project context → true for plain `claude -p`; `--bare` skips `CLAUDE.md`, so pass it with `--append-system-prompt-file CLAUDE.md`.
- Use the Explore subagent for verbose discovery → still true; it runs on your session's model and starts without your `CLAUDE.md`.

## Chapter 7

- (prefill not mentioned) → prefilling the assistant's reply returns an error on current models.

## Since the book was printed

- Chapters 5 and 6: Glob and Grep aren't in Claude Code's default tool set on macOS, Linux and WSL, and a skill's `allowed-tools` doesn't add them back. A forked skill gets them by running as a subagent whose `tools` lists them. `ch06/` does that with `repo-mapper` ([BOOK-FIXES.md](BOOK-FIXES.md)).

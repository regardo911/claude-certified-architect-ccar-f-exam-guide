# Chapter 5: the support MCP server

```bash
cd ch05
python test_client.py       # no key: every tool and error path, in memory
```

Look for `isError=False` with `"found": false` on 55555, `"isRetryable": true` on 99999, and `"isRetryable": false` on the $600 refund. Two `Tool ... failed` lines on stderr are the server's own log.

With a key, measure routing on the clear docstrings, then on the vague ones:

```bash
python route_test.py server.py "ana@example.com here. What's the status of 12345?" 10
python route_test.py server_vague.py "ana@example.com here. What's the status of 12345?" 10
```

Each prints your own tally of the first tool picked. It varies between runs. `server_vague.py` differs from `server.py` only in the `get_customer` and `lookup_order` docstrings.

For Claude Code, from this folder: `export SUPPORT_API_TOKEN=test-token`, `claude mcp list`, then `claude` once to approve the server. The chapter's `claude mcp add --scope user ...` writes to your own `~/.claude.json`.

## On your own system

Replace the three tool bodies with calls to your service and raise every failure through `fail()`. Rename `SUPPORT_API_TOKEN` in `.mcp.json` to your variable and keep it as `${VAR}`, so the file can go into git. Add each new error path to `CASES` in `test_client.py` and rerun it.

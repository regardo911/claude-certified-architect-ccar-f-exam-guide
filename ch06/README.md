# Chapter 6: the team repo and its CI review

This folder is a whole repo. Copy it out and work in the copy:

```bash
cp -R ch06 ~/orders-service && cd ~/orders-service && git init
```

Every command below runs from the root of that copy. Inside this companion repo, run them from `ch06/`.

## What's in it

The book's ten files, plus two: `.claude/agents/repo-mapper.md` gives `/explain-arch` its Glob and Grep ([BOOK-FIXES.md](../BOOK-FIXES.md)), and `src/api/refunds.test.js` holds todo cases so the testing rule has a file to match.

## Run it

These need Claude Code, and `review.sh` needs `jq`. `--setting-sources project` keeps your own `~/.claude` settings out.

```bash
claude -p "/review src/api/refunds.js" --setting-sources project
claude -p "/explain-arch src" --setting-sources project
bash ci/review.sh
```

- `/review` gives file, line, severity and a one-sentence message for each finding, with no style comments.
- `/explain-arch` gives one line per file under `src/`, and notes that `src/db.js` doesn't exist.
- `review.sh` writes `review.json` and `findings.json`, then prints lines shaped like `src/api/refunds.js:<line> [<severity>] <message>`. Severity is only ever `bug`, `security` or `validation`. The count and wording change from run to run. What the run cost is in `review.json` as `total_cost_usd`.

To check the testing rule, ask Claude about `src/api/refunds.test.js` in one session and about `src/api/refunds.js` in another; only the first loads `.claude/rules/testing.md`. `/memory` lists what loaded.

## Put the review in CI

In the copy, `.github/workflows/` already sits at the root, so GitHub will run it. Push the copy to a GitHub repo you own and add `ANTHROPIC_API_KEY` as a repository secret. Every pull request then runs `bash ci/review.sh` on GitHub's runners, on your key.

## On your team's code

1. Rewrite `CLAUDE.md` for your stack: language, test command, the three or four rules that always hold.
2. Edit `docs/review-standards.md` so it names what your team counts as a finding.
3. Change the `paths:` globs in the two rule files to where your API code and tests live.
4. Point the review at your own file: `bash ci/review.sh src/your/file.js`. With no argument it reviews `src/api/refunds.js`, as in the book.
5. Make the same change to the `run: bash ci/review.sh` line in the workflow, then delete `src/api/refunds.js` and its test.

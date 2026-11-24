---
name: explain-arch
description: Map the folder layout of this repo and summarise each part
context: fork
# repo: agent line added so the fork has Glob and Grep (BOOK-FIXES.md)
agent: repo-mapper
allowed-tools: Read Glob Grep
disallowed-tools: Edit Write Bash
argument-hint: [folder]
---
Map every file under $ARGUMENTS with Glob. Read the entry points.
Return one line per file: path, what it does, what it imports.

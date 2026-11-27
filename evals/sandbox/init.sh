#!/usr/bin/env bash
# Build the throwaway project a `skill` case runs in: a bare `origin.git` and a clone, `work/`, on
# `main` with one pushed commit and a clean tree. A case's `setup` shapes it from there.
set -eu
box="$1"

git init --quiet --bare --initial-branch main "$box/origin.git"
git init --quiet --initial-branch main "$box/work"
cd "$box/work"
git config user.name "Eval"
git config user.email "eval@example.invalid"
git remote add origin "$box/origin.git"

mkdir -p src tests
printf '# demo\n\nA tiny greeting library.\n' >README.md
printf 'def greet(name):\n    return f"Hello, {name}!"\n' >src/greet.py
printf 'from src.greet import greet\n\n\ndef test_greet():\n    assert greet("Ada") == "Hello, Ada!"\n' >tests/test_greet.py

git add --all
git commit --quiet --message "feat: add greet"
git push --quiet --set-upstream origin main

#!/usr/bin/env bash
# setup-github.sh
# Initializes a git repo here and pushes it to a new GitHub repository.
#
# Usage:
#   ./setup-github.sh <github-username> <repo-name> [public|private]
#
# Requires the GitHub CLI (`gh`) to be installed and authenticated
# (run `gh auth login` first if you haven't). If you don't have `gh`,
# see the manual steps printed at the bottom of this script instead.

set -e

USERNAME="$1"
REPO_NAME="${2:-prism-image-gen}"
VISIBILITY="${3:-public}"

if [ -z "$USERNAME" ]; then
  echo "Usage: ./setup-github.sh <github-username> <repo-name> [public|private]"
  exit 1
fi

git init
git add .
git commit -m "Initial commit: Prism AI image generator"
git branch -M main

if command -v gh &> /dev/null; then
  echo "Creating GitHub repo with gh CLI..."
  gh repo create "$USERNAME/$REPO_NAME" --"$VISIBILITY" --source=. --remote=origin --push
  echo "✅ Done! View it at https://github.com/$USERNAME/$REPO_NAME"
else
  echo "gh CLI not found. Do this manually instead:"
  echo "1. Create a new repo at https://github.com/new named '$REPO_NAME'"
  echo "2. Then run:"
  echo "   git remote add origin https://github.com/$USERNAME/$REPO_NAME.git"
  echo "   git push -u origin main"
fi

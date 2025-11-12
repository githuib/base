#!/bin/bash

old_version="$(uv version --short)"
uv version "$@"
new_version="$(uv version --short)"

if [[ "$old_version" == "$new_version" ]]; then
  echo "Version did not change: $new_version"
  exit 1
fi

git_push_pyproject () {
  git add pyproject.toml uv.lock
  git commit -m "Bump version: $1 -> $2"
  git push
}

git_push_tag () {
  tag="v$1"
  git tag "$tag"
  git push origin "$tag"
}

git_push_pyproject "$old_version" "$new_version" && git_push_tag "$new_version"

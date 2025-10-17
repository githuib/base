#!/bin/bash

version_or_rule="${1:-$RELEASE_VERSION}"

old_version="$(poetry version --short)"
poetry version "$version_or_rule"
new_version="$(poetry version --short)"

if [[ "$old_version" == "$new_version" ]]; then
  echo "Version did not change: $new_version"
  exit 1
fi

git_push_pyproject () {
  git add pyproject.toml
  git commit -m "Bump version: $1 -> $2"
  git push
}

git_push_tag () {
  tag="v$1"
  git tag "$tag"
  git push origin "$tag"
}

git_push_pyproject "$old_version" "$new_version" && git_push_tag "$new_version"

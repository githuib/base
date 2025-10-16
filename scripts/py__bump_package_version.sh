poetry version "$RELEASE_VERSION"

git add pyproject.toml
git commit -m "Bump version to $RELEASE_VERSION"
# git commit --allow-empty -m "Bump version to $RELEASE_VERSION"
git push

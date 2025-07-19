#!/bin/bash

# === Configuration ===
USERNAME="ajerbic"   # Docker Hub username
REPO="service2"      # Docker image repo
INCREMENT="minor"    # "minor" or "patch"

# === Fetch tags from Docker Hub ===
TAGS=$(curl -s "https://registry.hub.docker.com/v2/repositories/${USERNAME}/${REPO}/tags?page_size=100" \
  | grep -oE '"name":"v[0-9]+\.[0-9]+(\.[0-9]+)?"' \
  | sed -E 's/"name":"(v[0-9]+\.[0-9]+(\.[0-9]+)?)"/\1/' \
  | sort -V)

LATEST_TAG=$(echo "$TAGS" | tail -n 1)

if [[ -z "$LATEST_TAG" ]]; then
  echo "No version tags found."
  exit 1
fi

echo "Latest tag: $LATEST_TAG"

# === Extract version numbers ===
VERSION="${LATEST_TAG#v}"
IFS='.' read -ra PARTS <<< "$VERSION"
MAJOR="${PARTS[0]}"
MINOR="${PARTS[1]}"
HAS_PATCH="${#PARTS[@]}"
PATCH="${PARTS[2]:-0}"

# === Increment version ===
if [[ "$INCREMENT" == "patch" && "$HAS_PATCH" -eq 3 ]]; then
  PATCH=$((PATCH + 1))
elif [[ "$INCREMENT" == "minor" ]]; then
  MINOR=$((MINOR + 1))
  PATCH=0
fi

# === Construct next version with same format ===
if [[ "$HAS_PATCH" -eq 3 ]]; then
  NEXT_TAG="v$MAJOR.$MINOR.$PATCH"
else
  NEXT_TAG="v$MAJOR.$MINOR"
fi

echo "Suggested next version: $NEXT_TAG"

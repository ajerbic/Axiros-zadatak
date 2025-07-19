#!/bin/bash

set -e

# === CONFIGURATION ===
DOCKER_USER="ajerbic"
NETWORK="microservices-net"
SERVICE1_DIR="./service1"
SERVICE2_DIR="./service2"
TEST_SCRIPT="newtest.py"
RESULTS_FILE="test_results.txt"

# === FLAGS ===
UPDATE1=false
UPDATE2=false

# === Parse input arguments ===
for ARG in "$@"; do
  case $ARG in
    --update_service1)
      UPDATE1=true
      shift
      ;;
    --update_service2)
      UPDATE2=true
      shift
      ;;
    *)
      echo "Unknown argument: $ARG"
      exit 1
      ;;
  esac
done

# === Get latest and next version tags ===
get_latest_and_next_version() {
  local service=$1
  local latest_tag=$(curl -s "https://registry.hub.docker.com/v2/repositories/${DOCKER_USER}/${service}/tags?page_size=100" \
    | grep -oE '"name":"v[0-9]+\.[0-9]+(\.[0-9]+)?"' \
    | sed -E 's/"name":"(v[0-9]+\.[0-9]+(\.[0-9]+)?)"/\1/' \
    | sort -V | tail -n 1)

  if [[ -z "$latest_tag" ]]; then
    latest_tag="v1.0"
  fi

  VERSION="${latest_tag#v}"
  IFS='.' read -ra PARTS <<< "$VERSION"
  MAJOR="${PARTS[0]}"
  MINOR="${PARTS[1]}"
  PATCH="${PARTS[2]:-}"

  if [[ -z "$PATCH" ]]; then
    NEXT_TAG="v$MAJOR.$((MINOR + 1))"
  else
    NEXT_TAG="v$MAJOR.$MINOR.$((PATCH + 1))"
  fi

  echo "$latest_tag $NEXT_TAG"
}

# === Determine version tags ===
read LATEST1 NEXT1 <<< $(get_latest_and_next_version service1)
read LATEST2 NEXT2 <<< $(get_latest_and_next_version service2)

TAG1=$LATEST1
TAG2=$LATEST2

if $UPDATE1; then
  TAG1=$NEXT1
fi

if $UPDATE2; then
  TAG2=$NEXT2
fi

echo "🛠️  Building versions:"
echo " - Service1: $TAG1 (latest was $LATEST1)"
echo " - Service2: $TAG2 (latest was $LATEST2)"

# === Create network if not exists ===
docker network create $NETWORK 2>/dev/null || true

# === Build local images ===
docker build -t $DOCKER_USER/service1:$TAG1 "$SERVICE1_DIR"
docker build -t $DOCKER_USER/service2:$TAG2 "$SERVICE2_DIR"

# === Start containers (test script stops them later) ===
docker run -d --rm --name service1 --network $NETWORK -p 8081:8080 $DOCKER_USER/service1:$TAG1
docker run -d --rm --name service2 --network $NETWORK -p 8082:8080 $DOCKER_USER/service2:$TAG2

# === Run test suite ===
echo "🧪 Running test script..."
python3 "$TEST_SCRIPT"

# === Evaluate test results ===
if grep -q ': 0' "$RESULTS_FILE"; then
  echo "❌ Some tests failed. Not pushing to Docker Hub."
  exit 1
else
  echo "✅ All tests passed."
fi

# === Push updated services only ===
if $UPDATE1; then
  echo "📤 Pushing service1:$TAG1..."
  docker push $DOCKER_USER/service1:$TAG1
fi

if $UPDATE2; then
  echo "📤 Pushing service2:$TAG2..."
  docker push $DOCKER_USER/service2:$TAG2
fi

echo "🎉 Done. Services tested and pushed (if selected)."

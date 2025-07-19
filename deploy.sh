#!/bin/bash

set -e

# === CONFIG ===
DOCKER_USER="ajerbic"
VERSION1=""
VERSION2=""
ADDITIONAL_PARAM_1=""

# === Fetch latest tag for a service from Docker Hub ===
get_latest_version() {
  local service=$1
  local latest_tag=$(curl -s "https://registry.hub.docker.com/v2/repositories/${DOCKER_USER}/${service}/tags?page_size=100" \
    | grep -oE '"name":"v[0-9]+\.[0-9]+(\.[0-9]+)?"' \
    | sed -E 's/"name":"(v[0-9]+\.[0-9]+(\.[0-9]+)?)"/\1/' \
    | sort -V | tail -n 1)

  if [[ -z "$latest_tag" ]]; then
    echo "v1.0"
  else
    echo "$latest_tag"
  fi
}

# === Parse arguments ===
for ARG in "$@"; do
  case $ARG in
    --version_service1=*)
      VERSION1="${ARG#*=}"
      shift
      ;;
    --version_service2=*)
      VERSION2="${ARG#*=}"
      shift
      ;;
    --additional_param_1=*)
      ADDITIONAL_PARAM_1="${ARG#*=}"
      shift
      ;;
    *)
      echo "Unknown argument: $ARG"
      exit 1
      ;;
  esac
done

# === Fallback to latest if versions not specified ===
if [[ -z "$VERSION1" ]]; then
  VERSION1=$(get_latest_version service1)
fi

if [[ -z "$VERSION2" ]]; then
  VERSION2=$(get_latest_version service2)
fi

echo "Using versions:"
echo " - Service1: $VERSION1"
echo " - Service2: $VERSION2"
echo " - Additional param 1: $ADDITIONAL_PARAM_1"

# === Create network if not exists ===
docker network create microservices-net 2>/dev/null || true

# === Stop & remove existing containers (if any) ===
docker stop service1 service2 2>/dev/null || true

# === Pull images ===
echo "Pulling images..."
docker pull $DOCKER_USER/service1:$VERSION1
docker pull $DOCKER_USER/service2:$VERSION2

# === Run containers ===
echo "Starting service1..."
docker run -d --rm --name service1 --network microservices-net -p 8081:8080 \
  -e ADDITIONAL_PARAM_1=$ADDITIONAL_PARAM_1 \
  $DOCKER_USER/service1:$VERSION1

echo "Starting service2..."
docker run -d --rm --name service2 --network microservices-net -p 8082:8080 \
  -e ADDITIONAL_PARAM_1=$ADDITIONAL_PARAM_1 \
  $DOCKER_USER/service2:$VERSION2

echo ""
echo "Services are running:"
echo " - Service1: http://localhost:8081"
echo " - Service2: http://localhost:8082"

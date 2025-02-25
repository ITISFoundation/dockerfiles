#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -o errexit  # abort on nonzero exitstatus
set -o nounset  # abort on unbound variable
set -o pipefail # don't hide errors within pipes
IFS=$'\n\t'


build() {
  make devenv
  # shellcheck source=/dev/null
  pushd docker-registry-sync
  make build
  popd
}

tests() {
  # shellcheck source=/dev/null
  pushd docker-registry-sync
  make github-ci-tests
  popd
}

push() {
  # shellcheck source=/dev/null
  echo "to implment pushing"
}

# Check if the function exists (bash specific)
if declare -f "$1" >/dev/null; then
  # call arguments verbatim
  "$@"
else
  # Show a helpful error
  echo "'$1' is not a known function name" >&2
  exit 1
fi

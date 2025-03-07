#! /bin/bash

# Make script work regardless of where it is run from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/.." || exit

# Don't run as root user
if [ $(id -u) -eq 0 ]; then
  tput bold; echo "$(tput setaf 9)You do not need to run this script using sudo, it will handle sudo as required$(tput setaf 9)" ; tput sgr0
  exit 1
fi

tput bold; echo "$(tput setaf 2)Starting Tidbyt Renderer installation...$(tput setaf 9)" ; tput sgr0

# Run the initialization script that handles actual installation
scripts/tools/init

exit 0
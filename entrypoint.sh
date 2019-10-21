#!/bin/bash
echo "setting up ATLAS and running: [$@]"
source ${HOME}/.bashrc
env


cat ${HOME}/.bashrc
whoami
which jupyter
source /usr/local/bin/thisroot.sh
echo done
eval "$@"

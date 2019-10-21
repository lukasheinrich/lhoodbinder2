#!/bin/bash
echo "setting up ATLAS and running: [$@]"
source ${HOME}/.bashrc
env


cat ${HOME}/.bashrc
whoami
which jupyter
source /usr/local/bin/thisroot.sh
source ${HOME}/HistFitter/setup.sh
echo done
eval "$@"

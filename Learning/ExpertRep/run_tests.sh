#!/usr/bin/env bash

SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $SCRIPTPATH
docker run -it -v $SCRIPTPATH/..:/root/code backend_test bash /root/code/ExpertRep/run_on_start.sh
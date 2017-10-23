#!/usr/bin/env bash

SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $SCRIPTPATH
docker run -it -v $SCRIPTPATH:/root/code backend_test_container:0.1 bash /root/code/run_on_start.sh
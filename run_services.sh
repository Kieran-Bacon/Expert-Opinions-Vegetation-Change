#!/bin/bash 

docker run -p 6543:6543 -v group_proj_storage:/root/code group_proj_main bash /root/code/docker_run_on_start.sh&
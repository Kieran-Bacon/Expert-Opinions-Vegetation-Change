#!/bin/bash 

docker run -p 80:6543 -v group_proj_storage_data_3:/root/code/Server/ExpertWebtool/data group_proj_main bash /root/code/docker_run_on_start.sh&

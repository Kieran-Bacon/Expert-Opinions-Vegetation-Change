#!/bin/bash

docker build . -t expertclimatesystem:latest
docker run -p 80:6543 -v group_proj_storage_data:/root/code/Server/ExpertWebtool/data expertclimatesystem
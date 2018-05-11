#!/bin/bash

name="expertclimatesystem"
port=80
volume="group_proj_storage_data"

while [ $# -ge 2 ]
    do
        if [ "$1" = "-t" ]
            then 
                name=$2
        fi

        if [ "$1" = "-p" ]
            then
                port=$2
        fi

        if [ "$1" = "-v" ]
            then
                volume=$2
        fi
    shift
    shift
done

echo $name
echo $port 
echo $volume

docker build . -t "$name":latest
docker run -p "$port":6543 -v "$volume":/root/code/Server/ExpertWebtool/data "$name"
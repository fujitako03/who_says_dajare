#!/bin/bash

PROJ_PATH=$(cd ../../ && pwd)
docker run --rm -it -v $PROJ_PATH:/root/user -p 8888:8888 --name dajarepg_container dajarepg_image
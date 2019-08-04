#!/bin/bashcase 

PROJ_PATH=$(cd ../../ && pwd)
docker run -m 16g --runtime nvidia -e NVIDIA_VISIBLE_DEVICES=all --rm -it -v $PROJ_PATH:/root/user -p 8888:8888 --name dajarepg_container yusan1871/dajarepj_image:word2vec

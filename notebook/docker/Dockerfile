FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu16.04

# install basic dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    sudo git wget cmake nano vim gcc g++ build-essential ca-certificates software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# install python
RUN add-apt-repository ppa:deadsnakes/ppa \
&& apt-get update \
&& apt-get install -y python3.6 \
&& wget -O ./get-pip.py https://bootstrap.pypa.io/get-pip.py \
&& python3.6 ./get-pip.py \
&& ln -s /usr/bin/python3.6 /usr/local/bin/python3 \
&& ln -s /usr/bin/python3.6 /usr/local/bin/python

# install common python packages
RUN pip install pip setuptools -U && pip install pip==18.1 \
setuptools==39.1.0 \
wheel==0.30.0 \
jupyter==1.0.0 \
matplotlib==2.2.2 \
seaborn==0.8.1 \
scikit_learn==0.20.3 \
scipy==1.1.0 \
numpy==1.15.2 \
pandas==0.23.4 \
gensim==3.6.0 \
kaggle==1.4.7.1

# install pytorch
RUN pip install https://download.pytorch.org/whl/cu100/torch-1.0.0-cp36-cp36m-linux_x86_64.whl \
    torchvision

# install tensorflow and keras
RUN pip install tensorflow
RUN pip install keras

# install nltk
RUN pip install nltk

# install Spacy
RUN pip install spacy
RUN pip install "https://github.com/megagonlabs/ginza/releases/download/latest/ginza-latest.tar.gz"

# set working directory
WORKDIR /root/user

# copy jupyter config file
RUN mkdir /root/.jupyter
COPY .jupyter/jupyter_notebook_config.py /root/.jupyter

# config and clean up
RUN ldconfig \
&& apt-get clean \
&& apt-get autoremove

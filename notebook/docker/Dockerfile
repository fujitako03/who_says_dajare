FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu16.04

# set working directory
WORKDIR /root/user

# Locale setting
ENV LANG ja_JP.UTF-8

RUN set -ex && apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa

# Install dependencies
RUN set -ex && apt-get update && apt-get install -y \
    sudo \
    less \
    vim \
    man \
    wget \
    cmake \
    gcc \
    g++ \
    git \
    curl \
    file \
    # Build ni tukaesou
    build-essential \
    libssl-dev \
    libffi-dev \
    ca-certificates \
    byobu \
    language-pack-ja \
    unzip \
    libgtk2.0-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    nscd \
    protobuf-compiler \
    xvfb \
	freeglut3-dev \
	ffmpeg \
	libsm6 \
	libxrender1 \
    # python
    python3-numpy \
    python3-tk \
    graphviz \
    python3-pip \
    python-pil \
    python-lxml \
	python3-dev \
    python-dev \
    python3.6 \
    # Mecab
    mecab \
    libmecab-dev \
    mecab-ipadic-utf8\
    xz-utils \
    && apt-get -y clean all \
    && rm -rf /var/lib/apt/lists/*

# Set locale
RUN update-locale LANG=$LANG

# Mecab
RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git\
    && cd mecab-ipadic-neologd\
    && bin/install-mecab-ipadic-neologd -n -y

# install python
RUN wget -O ./get-pip.py https://bootstrap.pypa.io/get-pip.py \
&& python3.6 ./get-pip.py \
&& ln -s /usr/bin/python3.6 /usr/local/bin/python3 \
&& ln -s /usr/bin/python3.6 /usr/local/bin/python

# install python packages
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

# install pytorch
RUN pip install https://download.pytorch.org/whl/cu100/torch-1.0.0-cp36-cp36m-linux_x86_64.whl

RUN pip install "https://github.com/megagonlabs/ginza/releases/download/v1.0.2/ja_ginza_nopn-1.0.2.tgz"

# copy jupyter config file
# RUN mkdir /root/.jupyter
# COPY .jupyter/jupyter_notebook_config.py /root/.jupyter

# config and clean up
RUN ldconfig \
&& apt-get clean \
&& apt-get autoremove

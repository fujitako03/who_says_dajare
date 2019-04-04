FROM python:3.7-stretch

ARG project_dir=/home

# Install google cloud sdk
ARG CLOUD_SDK_VERSION=236.0.0
ENV CLOUD_SDK_VERSION=$CLOUD_SDK_VERSION

ARG INSTALL_COMPONENTS
RUN apt-get update -qqy && apt-get install -qqy \
  curl \
  gcc \
  python-dev \
  python-setuptools \
  apt-transport-https \
  lsb-release \
  openssh-client \
  git \
  gnupg \
  && easy_install -U pip && \
  pip install -U crcmod && \
  export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
  echo "deb https://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" > /etc/apt/sources.list.d/google-cloud-sdk.list && \
  curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
  apt-get update && apt-get install -y google-cloud-sdk=${CLOUD_SDK_VERSION}-0 $INSTALL_COMPONENTS && \
  gcloud config set core/disable_usage_reporting true && \
  gcloud config set component_manager/disable_update_check true && \
  gcloud config set metrics/environment github_docker_image && \
  gcloud --version
VOLUME ["/root/.config"]

# Install python2.7
# ENV GPG_KEY C01E1CAD5EA2C4F0B8E3571504C367C218ADD4FF
ENV PYTHON_VERSION 2.7.15

RUN set -ex \
	\
	&& wget -O python.tar.xz "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" \
	&& wget -O python.tar.xz.asc "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc" \
	&& export GNUPGHOME="$(mktemp -d)" \
	# && gpg --batch --keyserver ha.pool.sks-keyservers.net --recv-keys "$GPG_KEY" \
	# && gpg --batch --verify python.tar.xz.asc python.tar.xz \
	&& { command -v gpgconf > /dev/null && gpgconf --kill all || :; } \
	&& rm -rf "$GNUPGHOME" python.tar.xz.asc \
	&& mkdir -p /usr/src/python \
	&& tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
	&& rm python.tar.xz \
	\
	&& cd /usr/src/python \
	&& gnuArch="$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)" \
	&& ./configure \
		--build="$gnuArch" \
		--enable-shared \
		--enable-unicode=ucs4 \
	&& make -j "$(nproc)" \
	&& make install \
	&& ldconfig \
	\
	&& find /usr/local -depth \
		\( \
			\( -type d -a \( -name test -o -name tests \) \) \
			-o \
			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
		\) -exec rm -rf '{}' + \
	&& rm -rf /usr/src/python \
	\
	&& python2 --version

# Re-install pip3 from get-pip.py
ENV PYTHON_PIP_VERSION 19.0.3

 RUN set -ex; \
 	\
 	wget -O get-pip.py 'https://bootstrap.pypa.io/get-pip.py'; \
 	\
 	python3 get-pip.py \
 		--disable-pip-version-check \
 		--no-cache-dir \
 		"pip==$PYTHON_PIP_VERSION" \
 	; \
 	pip --version; \
 	\
 	find /usr/local -depth \
 		\( \
 			\( -type d -a \( -name test -o -name tests \) \) \
 			-o \
 			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
 		\) -exec rm -rf '{}' +; \
 	rm -f get-pip.py


RUN ls -Fla /usr/local/bin/p* \
    && which python  && python -V \
    && which python2 && python2 -V \
    && which python3 && python3 -V \
    && which pip3    && pip3 -V

ADD app/requirements.txt $project_dir
RUN pip3 install -r $project_dir/requirements.txt

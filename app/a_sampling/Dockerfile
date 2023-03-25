FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y python pip unzip xvfb

# RUN apt-get install -y python-opengl=3.1.0+dfsg-1 libosmesa6=19.0.8-0ubuntu0~18.04.2

# try this if no version available
RUN apt-get install -y python-opengl libosmesa6
RUN apt-get install -y libglib2.0-dev
WORKDIR /home
ADD requirements.txt /home
RUN pip install --upgrade pip
RUN pip install -r requirements.txt -i "https://pypi.tuna.tsinghua.edu.cn/simple/"

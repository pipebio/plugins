FROM python:3.9.9-slim-bullseye
LABEL authors="PipeBio"

# Update image
RUN apt-get update && apt-get upgrade -y && apt-get install -y wget

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"

RUN rm /bin/sh && ln -s /bin/bash /bin/sh
ADD ./bin/install.sh ./bin/install.sh

ADD ./environment.yml /environment.yml
RUN conda env create -f environment.yml || conda env update -f environment.yml

ADD bin/entrypoint.sh bin/entrypoint.sh
ADD runner.py runner.py
ADD custom_code/ custom_code/

RUN conda init bash && source ~/.bashrc && conda activate custom-jobs-venv

CMD [ "/bin/entrypoint.sh" ]
ARG REGISTRY_URI
FROM ${REGISTRY_URI}/tensorflow-training:1.15.3-cpu-py37-ubuntu18.04
# FROM ${REGISTRY_URI}/tensorflow-inference:1.15.4-cpu-py36-ubuntu18.04
# tensorflow-inference:1.15.4-gpu-py36-cu100-ubuntu18.04

# FROM tensorflow/serving
# tensorflow-inference:1.15.4-gpu-py36-cu100-ubuntu18.04
# ARG REGISTRY_URI
# FROM ${REGISTRY_URI}/tensorflow-inference:1.15.4-gpu-py36-cu100-ubuntu18.04
# COPY --from=0 / /
RUN apt-get update
#RUN apt-get install -y --no-install-recommends software-properties-common && add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y --no-install-recommends nginx curl \
&& pip3 install --upgrade pip
RUN apt-get install -y --no-install-recommends python3.7
#&& python3-pip python3-dev \
#&& cd /usr/local/bin && ln -s /usr/bin/python3 python

RUN apt-get install -y --no-install-recommends wget
RUN apt-get install -y --no-install-recommends ca-certificates
RUN apt-get install -y --no-install-recommends python3-setuptools
RUN apt-get install -y --no-install-recommends python3-dev
RUN apt-get install -y --no-install-recommends git
RUN pip3 install pip -U
RUN pip3 config set global.index-url https://opentuna.cn/pypi/web/simple
RUN pip3 install pandas \
 && pip3 install numpy \
 && pip3 install boto3

RUN pip3 install --no-cache-dir flask
RUN pip3 install --no-cache-dir gevent
RUN pip3 install --no-cache-dir gunicorn
RUN pip3 install --no-cache-dir s3fs
RUN pip3 install --no-cache-dir glob3

# ADD ./serve_model.py /usr/bin
RUN mkdir -p /opt/ml/model/dkn
ENV MODEL_S3_KEY s3://leigh-gw/dkn_model/dkn-2020-11-28-06-41-17-782/output/model.tar.gz

COPY /dkn /opt/ml/code
WORKDIR /opt/ml/code

ENTRYPOINT ["python", "serve"]

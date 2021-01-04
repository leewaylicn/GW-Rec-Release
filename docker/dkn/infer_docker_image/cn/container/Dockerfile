ARG REGISTRY_URI
FROM ${REGISTRY_URI}/tensorflow-inference:1.15.4-cpu-py36-ubuntu18.04
# tensorflow-inference:1.15.4-gpu-py36-cu100-ubuntu18.04

# FROM tensorflow/serving
# tensorflow-inference:1.15.4-gpu-py36-cu100-ubuntu18.04
# ARG REGISTRY_URI
# FROM ${REGISTRY_URI}/tensorflow-inference:1.15.4-gpu-py36-cu100-ubuntu18.04
# COPY --from=0 / /
RUN apt-get update
RUN pip3 install pip -U
RUN pip3 config set global.index-url https://opentuna.cn/pypi/web/simple
RUN pip3 install boto3

# ADD ./serve_model.py /usr/bin
RUN mkdir -p /opt/ml/model/dkn
ENV MODEL_S3_KEY s3://leigh-gw/dkn_model/dkn-2020-11-28-06-41-17-782/output/model.tar.gz

COPY /dkn /opt/ml/code
WORKDIR /opt/ml/code

ENTRYPOINT ["python", "serve"]

ARG REGISTRY_URI
FROM ${REGISTRY_URI}/tensorflow-training:1.15-gpu-py3
COPY recsys_tools /opt/ml/code/embed_dkn.py

ENV SAGEMAKER_PROGRAM embed_dkn.py
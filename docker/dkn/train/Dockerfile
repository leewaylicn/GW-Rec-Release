ARG REGISTRY_URI
FROM ${REGISTRY_URI}/tensorflow-training:1.14-gpu-py3
COPY /recsys_tools/recsys_kg/embed_dkn.py   /opt/ml/code/embed_dkn.py

ENV SAGEMAKER_PROGRAM embed_dkn.py

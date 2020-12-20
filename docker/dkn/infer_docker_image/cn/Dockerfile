ARG REGISTRY_URI
FROM ${REGISTRY_URI}/tensorflow-inference:1.15.4-cpu-py36-ubuntu18.04
# tensorflow-inference:1.15.4-gpu-py36-cu100-ubuntu18.04

# FROM tensorflow/serving
# tensorflow-inference:1.15.4-gpu-py36-cu100-ubuntu18.04
# ARG REGISTRY_URI
# FROM ${REGISTRY_URI}/tensorflow-inference:1.15.4-gpu-py36-cu100-ubuntu18.04
# COPY --from=0 / /

ADD ./serve_model.py /usr/bin
RUN mkdir -p /opt/ml/model/dkn
ENV MODEL_S3_KEY s3://leigh-gw/dkn_model/dkn-2020-11-28-06-41-17-782/output/model.tar.gz
ENTRYPOINT ["python", "/usr/bin/serve_model.py"]

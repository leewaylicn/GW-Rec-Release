FROM python:3.7.9-slim
RUN pip install boto3

FROM tensorflow/serving
COPY --from=0 / /

ADD ./serve_model.py /usr/bin
RUN mkdir -p /opt/ml/model/dkn
ENV MODEL_S3_KEY s3://leigh-gw/dkn_model/dkn-2020-11-28-06-41-17-782/output/model.tar.gz
ENTRYPOINT ["python", "/usr/bin/serve_model.py"]
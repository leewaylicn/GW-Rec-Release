#!/bin/bash

###############
# for dkn dag #
###############
cd ~
mkdir -p ~/gw_dags
aws s3 cp  --recursive  s3://leigh-gw/airflow ~/gw_dags

mkdir -p ~/airflow/dags/dkn
cp gw_dags/GW/src/config.py  ~/airflow/dags/dkn
cp gw_dags/GW/src/gw_dag.py  ~/airflow/dags/dkn
sed -i 's/<s3-bucket>/${S3BucketName}/g' ./*.*
sed -i 's/<region-name>/${AWS::Region}/g' ./*.*
cd ~/airflow/dags/dkn
zip -r dkn.zip *
rm *.py
##############
# for kg dag #
##############

# Run Airflow webserver and scheduler
airflow list_dags
airflow webserver -D
airflow scheduler -D
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

dag = DAG('xcom-sample', start_date=datetime(2017, 3, 20), schedule_interval='@once')

def push_data(**context):
    context['ti'].xcom_push(key='test_key', value='test_val888')
    return 'the return value'


push_data_op = PythonOperator(
    task_id='push_data',
    python_callable=push_data,
    provide_context=True,
    dag=dag
)


def pull_data(**context):
    test_data = context['ti'].xcom_pull(key='test_key')
    returned = context['ti'].xcom_pull(key='return_value')
    print('=======')
    print(test_data)
    print(returned)


pull_data_op = PythonOperator(
    task_id='pull_data',
    python_callable=pull_data,
    provide_context=True,
    dag=dag
)

push_data_op >> pull_data_op
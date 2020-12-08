# GW-RecSys
## 镜像列表
| 编号 | 名字 | 内容 | 文件夹 | 完成度 |
| ---- | ---- | ---- | ---- | ---- |
| 1 | KG 训练 | 知识图谱训练，生成context/entity/word embeddings.npy| graph/train | [x] |
| 2 | KG 推理 | 知识图谱推理，将单条新闻标题转化为word/entity的索引| graph/inference | [x] |
| 3 | KG 逻辑 | 知识图谱推理调用，将新闻标题转化为word/entity的索引, 写入缓存| graph/logic | [] |

## 使用方法
#### KG 训练
##### 通过sagemaker estimator的方法进行调用，详情参考 graph/complete/test_complete.ipynb, 只用了其中的训练部分
#### KG 推理
##### 通过boto3的方法进行调用，详情参考 graph/inference/test_inference.ipynb


## airflow 部署相关说明
跑CloudFormation模板，airflow-ec2-cn.yaml 。这里要设置3个参数：桶、ec2的key、数据库的密码。
* 桶是用来存放训练数据的
* key是ec2登录用的，这个ec2上运行的是 airflow webserver
* 数据库是airflow用来存放运行任务信息的

## dkn 使用说明
1. 制作 训练和推理的 container
2. 把数据放到指定的位置，位置在 CloudFormation 创建的桶里，具体是在 airflow/GW/src/config.py 里指定的
3. 触发 lambda trigger DAG
4. DAG 运行完成后暴露 NLB
### 打镜像
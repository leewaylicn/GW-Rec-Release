## 关于训练的 container
这个就是通过BYOC的方式，使用当前目录的 Dockerfile，用脚本 build_and_push.sh 完成build并打包到ECR
国内的region 和 global region SM 的container 账号不一样，要改一下 build_and_push.sh 里的脚本

## 关于 dkn 推理的 container 
在目录 infer_docker_image 下面，这个container是部署在ECS的
这个并非完全标准的 TensorFlow model serving container，
用标准的container做model serving的问题在于你要先获取训练好的model才行，然而官方提供的container 不能从S3获取训练好的模型，
所以这里要在container里安装一下 aws cli，通过aws cli来从S3获取model

这里打的container就是整合了 TensorFlow model serving 和 aws cli 的container 
同样的，要修改一下 build_and_push.sh 里的 FROM_ACCOUNT_ID 来适配国内或者global region

另外，值得注意的一点是，container 在ECS上运行并且能从S3获取模型，ECS的 task definition 里设置的role要有S3相应的权限

infer_curl  这个可以通过 http 用来测试部署出来的 container 是否正常工作 

## recsys_kg_byoc.ipynb
这个是在SM上使用byoc运行的notebook
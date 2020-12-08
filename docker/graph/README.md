# Graph part
## 文件夹
| 编号 | 名字 | 内容 |
| ---- | ---- | ---- |
| 1 | complete | 知识图谱训练 + 推理| 
| 2 | inference | 知识图谱推理|
| 3 | train | 知识图谱训练|
| 4 | logic | 知识图谱推理调用，将新闻标题转化为word/entity的索引, 将结果写入cache|
| 5 | local_test | 知识图谱训练/推理本地测试|
## 文件说明
* kg_dbpedia.txt 知识图谱三元组数据（通用+行业）
* entities_dbpedia.dict 实体索引（通用+行业）
* relations_dbpedia.dict 关系索引（通用+行业）
* entity_industry.txt 行业实体

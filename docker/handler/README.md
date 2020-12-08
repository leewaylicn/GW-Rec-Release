
## 关于 handler 的 container 
handler的作用是为graph和dkn提供一个统一的接口给用户排序使用,目前输入输出如下：
```
input：
{
“recall”:[{“id”:1234,”title”:”中国银行”},{“id”:3434,”title”:”中兴进入美国市场”}],
“history”:[{“id”:5555,”title”:”中国银行收紧银根”},{“id”:3334,”title”:”股市低迷”}]
}

output:
{
“result”:[{“id”:5555,”score”:0.23},{“id”:3334,”score”:0.11}]
}
```
另外特别要注意的是启动这个docker依赖于graph和dkn两个docker，需要把两个服务的路径作为环境变量GRAPH_URL和DKN_URL传给handler的docker.
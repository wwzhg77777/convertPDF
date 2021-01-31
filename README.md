

# README


## 开发环境

**&emsp;操作系统： Windows 10 LTSC (2018版)**

**&emsp;Python版本： 3.8.6 &emsp;(Python3及以上版本均可)**

**&emsp;程序应用环境： Windows系统下 `x64`和`x86`平台 &emsp;(分别用pyinstaller打包，详情可看[Python x64和x86平台下pyinstaller打包过程](https://blog.csdn.net/m0_54768192/article/details/113006948))**

**&emsp;Python第三方包： `tkinter, pyinstaller, baidu-aip, pdfminer, pdfminer3k, fitz, requests `**
<br />
<br />

## 部分演示图
`源代码目录结构：`
```
—— src
 |——— myConvert.py	# PDF转图片，PDF转文字的模块
 |——— pdf_Ocr.py	# PDF转图片文字识别模块
 |——— tkPDF.py		# 主程序入口文件
 |
```

`执行文件exe 目录结构：`
```
—— src  (x64 or x86)
 |——— app.ini		# 存放Ocr接口的用户参数和后端的api接口地址
 |——— tkPDF.exe		# 主程序入口
 |
```
![](https://img-blog.csdnimg.cn/20210201041233449.jpg)

<br />

`主界面：`

![t1](https://img-blog.csdnimg.cn/20210201031508870.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L20wXzU0NzY4MTky,size_20,color_FFFFFF,t_10,g_center)


`执行的过程显示 正在转换中...`

![t2](https://img-blog.csdnimg.cn/20210201031508944.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L20wXzU0NzY4MTky,size_20,color_FFFFFF,t_10,g_center)


`支持多选的PDF转图片文字识别`

![t3](https://img-blog.csdnimg.cn/20210201031508936.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L20wXzU0NzY4MTky,size_20,color_FFFFFF,t_10,g_center)


`支持多选的图片文字识别`

![t4](https://img-blog.csdnimg.cn/20210201031508996.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L20wXzU0NzY4MTky,size_20,color_FFFFFF,t_10,g_center)


`支持多选的PDF文件文字提取，对不支持文字提取的PDF另存`

![t5](https://img-blog.csdnimg.cn/202102010315094.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L20wXzU0NzY4MTky,size_20,color_FFFFFF,t_10,g_center)


# 读取本地配置
&emsp;该小工具采用读取本地配置文件的方式，可以灵活地更换`api`接口。主要有2个列表：`SERVER`和`APP_INFO`
&emsp;读取的路径在`tkPDF.py`里已经写明，是读取主程序所在目录下的`app.ini`文件。
```
注：exe主程序可以添加快捷方式，弄到到别的路径，不影响app.ini文件的读取
```

```bash
[SERVER]
url=....

[APP_INFO]
app_id=....
api_key=....
secret_key=....
```


# MySQL
&emsp;后端只用了2张表：
&emsp;`index:`记录了百度AI用户的Ocr接口免费次数
&emsp;`record:`记录用户的上传文件

数据表结构如下:

`index:`
列名     |   数据类型   |   长度   |   主键   |   外键   |   允许空   |   默认值   |   说明
-------- | -----  | ---- | ---- | ---- | ---- | ----- | ---- |
id | int | 4 |是 | 否 |否 |  |
app_id  | varchar | 30 | 否 | 否 | 否 |  |
type  | varchar | 30 | 否 | 否 | 否 |  |
count |int | 8 | 否 | 否 | 否 |  |
unix_time |int | 11 | 否 | 否 | 否 |  | 

`record:`
列名     |   数据类型   |   长度   |   主键   |   外键   |   允许空   |   默认值   |   说明
-------- | -----  | ---- | ---- | ---- | ---- | ----- | ---- |
id | int | 4 |是 | 否 |否 |  |
filename  | varchar | 50 | 否 | 否 | 否 |  |
filesize  | varchar | 20 | 否 | 否 | 否 |  |
app_id |varchar | 30 | 否 | 否 | 否 |  |
type | varchar | 30 | 否 | 否 | 否 |  | 
unix_time |int | 11 | 否 | 否 | 否 |  | 

<br />

查询数据库的结果：


![m1](https://img-blog.csdnimg.cn/20210201040304225.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L20wXzU0NzY4MTky,size_20,color_FFFFFF,t_10,g_center)


![m2](https://img-blog.csdnimg.cn/20210201040304281.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L20wXzU0NzY4MTky,size_20,color_FFFFFF,t_10,g_center)

# 完整代码已在GitHub上开源
`GitHub:`[https://github.com/wwzhg77777/convertPDF](https://github.com/wwzhg77777/convertPDF)


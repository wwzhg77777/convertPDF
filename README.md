# README.md

<br />
<br />

### 该文章的完整介绍来自于:[https://blog.csdn.net/m0_54768192/article/details/113488889](https://blog.csdn.net/m0_54768192/article/details/113488889)

### 开发环境

**&emsp;操作系统： Windows 10 LTSC (2018版)**

**&emsp;Python版本： 3.8.6 &emsp;(Python3及以上版本均可)**

**&emsp;程序应用环境： Windows系统下 `x64`和`x86`平台 &emsp;(分别用pyinstaller打包，详情可看[Python x64和x86平台下pyinstaller打包过程](https://blog.csdn.net/m0_54768192/article/details/113006948))**

**&emsp;Python第三方包： `tkinter, pyinstaller, baidu-aip, pdfminer, pdfminer3k, fitz, requests `**
<br />
<br />

## 目录结构
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

### 读取本地配置
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


### MySQL
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


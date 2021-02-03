# README.md

<br />
<br />

### 完整介绍来自[[个人笔记] python+php 制作C/S架构的PDF文字识别小工具](https://blog.csdn.net/m0_54768192/article/details/113488889)

### 应用环境
&emsp;**Windows系统下 `x64`和`x86`平台**

<br />

### 目录结构

`源代码目录结构：`

```
convertPDF
 |——— api
      |——— index.php    # 后端php代码
 |
 |——— src
      |——— app.ini      # 存放Ocr接口的用户参数和后端的api接口地址
      |——— myConvert.py # PDF转图片，PDF转文字的模块
      |——— pdf_Ocr.py   # PDF转图片文字识别模块
      |——— tkPDF.py     # 主程序入口文件
```

`执行文件的目录结构：`

```
—— src  (x64 or x86)
 |——— app.ini   # 存放Ocr接口的用户参数和后端的api接口地址
 |——— tkPDF.exe # 主程序入口
 |
```

## 主程序生成步骤
&emsp;src目录下执行`pyinstaller -F -w .\tkPDF.py`生成主程序tkPDF.exe
&emsp;复制src目录下的`app.ini`到主程序目录。app.ini内容需要自行补充完整。[百度AI申请地址入口](https://ai.baidu.com/)

`app.ini`
```bash
[SERVER]
url=....

[APP_INFO]
app_id=....
api_key=....
secret_key=....
```

<br />

### 开发环境
&emsp;**Python版本： 3.8.6 &emsp;(Python3及以上版本均可)**

&emsp;**Python第三方包： `tkinter, pyinstaller, baidu-aip, pdfminer, pdfminer3k, fitz, requests `**
<br />
<br />


### MySQL数据表结构
&emsp;后端2张表：
`index`记录了百度AI用户的Ocr接口免费次数
`record`记录用户的上传文件

`pdfrecord`数据库结构如下:

`pdfrecord.index`
列名     |   数据类型   |   长度   |   主键   |   外键   |   允许空   |   默认值   |   说明
-------- | -----  | ---- | ---- | ---- | ---- | ----- | ---- |
id | int | 4 |是 | 否 |否 |  | 唯一标识
app_id  | varchar | 30 | 否 | 否 | 否 |  | Ocr的APP_ID
type  | varchar | 30 | 否 | 否 | 否 |  | Ocr的类型
count |int | 8 | 否 | 否 | 否 |  | Ocr的次数
unix_time |int | 11 | 否 | 否 | 否 |  | 10位UNIX时间戳

`pdfrecord.record`
列名     |   数据类型   |   长度   |   主键   |   外键   |   允许空   |   默认值   |   说明
-------- | -----  | ---- | ---- | ---- | ---- | ----- | ---- |
id | int | 4 |是 | 否 |否 |  | 唯一标识
filename  | varchar | 50 | 否 | 否 | 否 |  | 文件名称
filesize  | varchar | 20 | 否 | 否 | 否 |  | 文件大小(Mb)
app_id |varchar | 30 | 否 | 否 | 否 |  | Ocr的APP_ID
type | varchar | 30 | 否 | 否 | 否 |  | Ocr的类型
unix_time |int | 11 | 否 | 否 | 否 |  | 10位UNIX时间戳


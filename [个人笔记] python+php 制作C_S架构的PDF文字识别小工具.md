@[TOC](Python+PHP实现图片文字识别+PDF转txt的小工具)
# 使用需求
&emsp;&emsp;这个需求来源于学校，做勤工工作时遇到的一个问题，需要**批量提取PDF文件里的文字，对PDF里的图片进行文字识别。**
&emsp;&emsp;当时做了一个非常简易的一个版本，只能实现一对一的图片文字识别。第一版没有备份，技术要点是**面向过程编程、GUI编程、解析PDF、百度文字识别等，Python使用了这些第三方包：`tkinter, pyinstaller, baidu-aip, pdfminer, pdfminer3k, fitz...`**
&emsp;整体上参考了该博主的文章[https://blog.csdn.net/qq_38144563/article/details/96138470](https://blog.csdn.net/qq_38144563/article/details/96138470)

<br />

&emsp;现在做版本迭代，重制了第二版，改成**面向对象编程**，均用`Class`来实现功能，可实现一对多的图片文字识别，PDF转txt，后端PHP的数据库记录。因为百度AI的QPS限制了高并发(免费用户就2次QPS)，所以没用多线程开发。

<br />
<br />

## 开发环境

**&emsp;操作系统： Windows 10 LTSC (2018版)
&emsp;Python版本： 3.8.6 &emsp;(Python3及以上版本均可)
&emsp;程序应用环境： Windows系统下 `x64`和`x86`平台 &emsp;(分别用pyinstaller打包，详情可看[Python x64和x86平台下pyinstaller打包过程](https://blog.csdn.net/m0_54768192/article/details/113006948))
&emsp;Python第三方包： `tkinter, pyinstaller, baidu-aip, pdfminer, pdfminer3k, fitz, requests `**
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

# Python代码
```
注：我用的vsCode，格式化工具flake8，但单行最大字符数是默认的70。
```

## tk主窗体
```
使用Python3的tkinter来创建主窗体
```

`tkPDF.py:`

```python
# coding=utf-8

import os
import sys
import time
import tkinter
from tkinter import messagebox

import requests

from .myConvert import ConvertPDF, ConvertPic


class tkPDF:
    """
    创建PDF转换的Tk窗体
    width: 窗体宽度
    height: 窗体高度
    """

    __Url: str
    __APP_ID: str
    __API_KEY: str
    __SECRET_KEY: str

    window = tkinter.Tk()
    __title: str
    __width: int
    __height: int

    # 创建Button控件, command: 绑定指定函数
    btn_pic = tkinter.Button(window,
                             font=('宋体', 11, 'normal'),
                             text='图片识别文字提取')
    btn_pdf_img = tkinter.Button(window,
                                 font=('宋体', 11, 'normal'),
                                 text='PDF(扫描版)转WORD文档')
    btn_pdf_word = tkinter.Button(window,
                                  font=('宋体', 11, 'normal'),
                                  text='PDF(文字版)转word文档')
    btn_refresh = tkinter.Button(window, font=('黑体', 9, 'bold'), text='再次刷新')

    # 创建Label控件
    label = tkinter.Label(window,
                          font=('黑体', 11, 'bold'),
                          justify='left',
                          text='今日的高精度识别次数：---\n\n今日的标准识别次数：-----')

    def __init__(self, title, width: int, height: int):
        # 读取配置文件
        self.get_env()

        self.__title = title
        self.__width = width
        self.__height = height

        self.window.title(self.__title)
        self.window.geometry('{0}x{1}'.format(self.__width, self.__height))

        # 绑定函数
        self.btn_pic.config(command=self.On_parse_pic)
        self.btn_pdf_img.config(command=self.On_parse_img)
        self.btn_pdf_word.config(command=self.On_parse_word)
        self.btn_refresh.config(command=self.get_freeCount)

        # 设置width, height
        self.btn_pic.place(width=150, height=40)
        self.btn_pdf_img.place(width=180, height=40)
        self.btn_pdf_word.place(width=180, height=40)
        self.btn_refresh.place(width=100, height=30)

        # 设置Label参数
        self.label.place(x=350, y=220)

        # 设置控件在窗体的位置
        _x = 60  # 左上角x
        _y = 100  # 左上角y
        margin = 30  # 控件之间的间距

        self.btn_pic.place(x=_x, y=_y)
        _x += int(self.btn_pic.place_info()['width'])  # 获取控件的width
        _x += margin

        self.btn_pdf_img.place(x=_x, y=_y)
        _x += int(self.btn_pdf_img.place_info()['width'])  # 获取控件的width
        _x += margin

        self.btn_pdf_word.place(x=_x, y=_y)
        self.btn_refresh.place(x=580, y=228)

        # 获取今日的免费次数
        self.get_freeCount()

        # 开始捕获窗体消息(动态更新)
        self.window.mainloop()

    def get_env(self):
        """
        设置配置文件，添加配置参数
        """
        try:
            INI_file = os.path.join(os.path.dirname(sys.argv[0]), r'app.ini')  # 读取主程序目录下的app.ini
            INI_read = open(INI_file, 'r').read()
            INI_rows = INI_read.split('\n')
            for i in range(len(INI_rows)):
                if INI_rows[i].find('[SERVER]') > -1:
                    self.__Url = INI_rows[i + 1].split('=')[1]  # 获取url值
                elif INI_rows[i].find('[APP_INFO]') > -1:
                    self.__APP_ID = INI_rows[i + 1].split('=')[1]  # 获取app_id值
                    self.__API_KEY = INI_rows[i +
                                              2].split('=')[1]  # 获取api_key值
                    self.__SECRET_KEY = INI_rows[i + 3].split('=')[
                        1]  # 获取secret_key值
        except BaseException:
            messagebox.showinfo('提示', '未能加载配置文件: app.ini ，请检查文件是否存在。')
            sys.exit(0)

    def get_freeCount(self):
        """
        获取今日的免费次数
        """

        url_params = {'a': self.__APP_ID, 't': int(time.time())}
        res = requests.get(url=self.__Url, params=url_params)
        if res.status_code == 200:
            result = res.json()
            if result['errCode'] == 0:
                self.label.config(text='今日的高精度识别次数：{}\n\n今日的标准识别次数：{}'.format(
                    500 - int(result['count']['bA']), 50000 -
                    int(result['count']['bG'])))
                self.active_btn()
            else:
                messagebox.showinfo('提示', '获取今天次数失败，请检查网络。')
                self.disable_btn()
        else:
            messagebox.showinfo('提示', '网络中断，请检查网络。')
            self.disable_btn()

    def getInfo_app(self):
        """
        获取AipOcr的参数列表
        """

        return [self.__APP_ID, self.__API_KEY, self.__SECRET_KEY]

    def disable_btn(self):
        """
        禁用按钮
        """

        self.btn_refresh.config(state='active')
        self.btn_pic.config(state='disabled')
        self.btn_pdf_img.config(state='disabled')
        self.btn_pdf_word.config(state='disabled')

    def active_btn(self):
        """
        激活按钮
        """

        self.btn_refresh.config(state='disabled')
        self.btn_pic.config(state='active')
        self.btn_pdf_img.config(state='active')
        self.btn_pdf_word.config(state='active')

    def On_parse_pic(self):
        """
        开始图片文字识别
        """

        # 创建转换Pic的实例类
        mypic = ConvertPic(self.getInfo_app(), self.__Url)
        if mypic.errCode == 0:
            self.window.title('正在转换中，请等待...')
            callback = mypic.mult_parse_pic()
            if callback['errCode'] == 0:
                self.window.title('PDF转换 功能选择')
                messagebox.showinfo('提示', callback['message'])
                self.label.config(text='今日的高精度识别次数：{}\n\n今日的标准识别次数：{}'.format(
                    500 - int(callback['count']['bA']), 50000 -
                    int(callback['count']['bG'])))
                os.startfile(mypic.filedir)
            elif callback['errCode'] == 210:
                messagebox.showinfo('提示', '今天的次数已用完，请等明天。')
            else:
                messagebox.showinfo('提示', '网络中断，请检查网络。')
        else:
            messagebox.showinfo('提示', mypic.errMessage)

    def On_parse_img(self):
        """
        开始PDF的图片文字识别
        """

        # 创建转换PDF的实例类
        mypdf = ConvertPDF(self.getInfo_app(), self.__Url)
        if mypdf.errCode == 0:
            self.window.title('正在转换中，请等待...')
            callback = mypdf.mult_parse_img()
            if callback['errCode'] == 0:
                self.window.title('PDF转换 功能选择')
                messagebox.showinfo('提示', callback['message'])
                self.label.config(text='今日的高精度识别次数：{}\n\n今日的标准识别次数：{}'.format(
                    500 - int(callback['count']['bA']), 50000 -
                    int(callback['count']['bG'])))
                os.startfile(mypdf.filedir)
            elif callback['errCode'] == 210:
                messagebox.showinfo('提示', '今天的次数已用完，请等明天。')
            else:
                messagebox.showinfo('提示', '网络中断，请检查网络。')
        else:
            messagebox.showinfo('提示', mypdf.errMessage)

    def On_parse_word(self):
        """
        开始PDF的文字识别
        """

        # 创建转换PDF的实例类
        mypdf = ConvertPDF()
        if mypdf.errCode == 0:
            self.window.title('正在转换中，请等待...')
            callback = mypdf.mult_parse_word()
            self.window.title('PDF转换 功能选择')
            messagebox.showinfo('提示', callback['message'])
            os.startfile(mypdf.filedir)
        else:
            messagebox.showinfo('提示', mypdf.errMessage)


if __name__ == '__main__':
    myTk = tkPDF("PDF转换 功能选择", 700, 300)
```

<br />
<br />
<br />

## PDF转图片文字识别
```
调用了百度AI的Ocr文字识别的高精度版: basicAccurate 和标准版: basicGeneral
```

`pdf_Ocr.py:`
```python
# coding=utf-8

import os
import threading
import time

import aip.ocr
import requests


class pdf_Ocr:
    """
    提供PDF的Ocr
    """
    __Url: str
    __client: aip.ocr.AipOcr

    lock_ = threading.Lock()

    def __init__(self, client: aip.ocr.AipOcr, url: str):
        self.__client = client
        self.__Url = url

    def Ocr_img(self,
                img_path,
                save_path,
                filename: str = None,
                is_pdf: bool = False):
        """
        图片文字识别
        """

        # 自定义取小数点后两位的函数
        # r2 = lambda r: str(r)[:str(r).rfind('.') + 2 + 1]
        if is_pdf:
            mlist = os.listdir(img_path)
            suffix = mlist[0][-3:]
            imgs = [
                '%i.%s' % (i, suffix)
                for i in sorted([int(mi[:str(mi).rfind('.')]) for mi in mlist])
            ]
            file_basename = os.path.basename(filename)
            pdfsize = os.path.getsize(filename)
        else:
            imgs = os.listdir(img_path)
            file_basename = None
            pdfsize = None

        if is_pdf:  # 以pdf文件命名
            writefile = open(
                save_path +
                '/%s.txt' % file_basename[:str(file_basename).rfind('.')], 'a')
        else:
            writefile = None

        processCount = 100 / len(imgs)
        beilv = processCount
        Mymessage = ''
        Mycount = {}
        Mytype = ''
        pic_count = 0
        for imgfile in imgs:
            print('图片文字识别完成: ' + str(round(processCount, 2)) + '%')
            processCount += beilv

            if not is_pdf:  # 以pic图片命名
                writefile = open(
                    save_path +
                    '/图片_%s.txt' % imgfile[:str(imgfile).rfind('.')], 'w')

            with open(img_path + '/%s' % imgfile, 'rb') as img:
                # 发送给数据库记录次数
                headers = {
                    'Content-Type': 'application/json',
                    'Connection': 'close'
                }
                if is_pdf:
                    data = {
                        'filename': filename,
                        'filesize': pdfsize,
                        'count': 1,
                        'a': self.__client._appId,
                        'nf': imgfile
                    }
                else:
                    data = {
                        'filename': img_path + '/%s' % imgfile,
                        'filesize':
                        os.path.getsize(img_path + '/%s' % imgfile),
                        'count': 1,
                        'a': self.__client._appId
                    }
                res = requests.post(url=self.__Url, json=data, headers=headers)
                try:
                    result = res.json()
                except BaseException as e:
                    return {'errCode': 400, 'message': e, 'result': res.text}
                # 判断返回值
                if result['errCode'] != 0:
                    return {
                        'errCode': result['errCode'],
                        'message': result['message'],
                        'result': result['count']
                    }

                read = img.read()
                # 调用Ocr函数
                message = None
                try:
                    self.lock_.acquire()
                    message = self.get_message(read, result['type'], 0)
                    self.lock_.release()
                except BaseException as e:
                    return {
                        'errCode': 400,
                        'message': e,
                        'result': '连接超时，请检查网络'
                    }
                for read in message.get("words_result"):
                    words = read.get("words")
                    writefile.write(words)
                    writefile.write('\n')
                writefile.write('\n\n%s\n\n' % ('-' * 70))
                Mymessage = result['message']
                Mycount = {
                    'bA': result['count']['bA'],
                    'bG': result['count']['bG']
                }
                Mytype = result['type']
                pic_count += 1

            if not is_pdf:
                writefile.close()

        if is_pdf:
            writefile.close()
        return {
            'errCode': 0,
            'message': Mymessage,
            'count': Mycount,
            'type': Mytype,
            'pic_count': pic_count
        }

    def get_message(self, read, type, is_exit: bool):
        if is_exit:
            if type == 'basicAccurate':
                return self.__client.basicAccurate(read)
            else:
                return self.__client.basicGeneral(read)
        else:
            try:
                if type == 'basicAccurate':
                    return self.__client.basicAccurate(read)
                else:
                    return self.__client.basicGeneral(read)
            except BaseException:
                # 停留2秒再执行一次,再出错则退出
                time.sleep(2)
                return self.get_message(read, type, True)
```

## 读取本地配置
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

<br />

读取本地配置的函数如下：
`get_env(self):`
```python
def get_env(self):
        """
        设置配置文件，添加配置参数
        """
        try:
            INI_file = os.path.join(os.path.dirname(sys.argv[0]), r'app.ini')  # 读取主程序目录下的app.ini
            INI_read = open(INI_file, 'r').read()
            INI_rows = INI_read.split('\n')
            for i in range(len(INI_rows)):
                if INI_rows[i].find('[SERVER]') > -1:
                    self.__Url = INI_rows[i + 1].split('=')[1]  # 获取url值
                elif INI_rows[i].find('[APP_INFO]') > -1:
                    self.__APP_ID = INI_rows[i + 1].split('=')[1]  # 获取app_id值
                    self.__API_KEY = INI_rows[i +
                                              2].split('=')[1]  # 获取api_key值
                    self.__SECRET_KEY = INI_rows[i + 3].split('=')[
                        1]  # 获取secret_key值
        except BaseException:
            messagebox.showinfo('提示', '未能加载配置文件: app.ini ，请检查文件是否存在。')
            sys.exit(0)
```

<br />
<br />
<br />


# 后端代码
&emsp;&emsp;该小工具用`python+php+mysql`实现的`C/S`架构，后端的主要作用是实时保存用户上传的文件记录。
## PHP源码
`index.php:`
```php
<?php
header('Access-Control-Allow-Origin:*');
header('Access-Control-Allow-Methods:GET,POST');
header('Access-Control-Allow-Headers:x-requested-with,Content-Type');

if (isset($_GET['a']) && isset($_GET['t'])) {
    $app_id = $_GET['a'];
    $unix_ontime = $_GET['t'];

    $conn = @mysqli_connect('127.0.0.1', 'root', 'root', 'pdfrecord', 3306, '');
    $input = array(
        'errCode' => '',
        'count' => null,
        'message' => ''
    );

    if (mysqli_connect_error()) {
        $input['errCode'] = 403;
        $input['count'] = null;
        $input['message'] = '连接数据库失败';
        print_r(json_encode($input));
    } else {
        $query = "SELECT * FROM
            `index` WHERE
            `app_id`='$app_id'";
        $result = $conn->query($query);

        # 不存在则新建数据
        if (mysqli_num_rows($result) != 2) {
            $insertsql = "INSERT INTO `index`
            (`app_id`,`type`,`count`,`unix_time`) VALUES ";
            $conn->query($insertsql . "('$app_id','basicAccurate','0',UNIX_TIMESTAMP(NOW()))");
            $conn->query($insertsql . "('$app_id','basicGeneral','0',UNIX_TIMESTAMP(NOW()))");
            # 更新查询集
            $result = $conn->query($query);
        }

        $rows = array();
        # 获取查询的数据
        while ($row = mysqli_fetch_assoc($result)) {
            if ($row['type'] == 'basicAccurate') {
                $rows[0] = $row;
            } else {
                $rows[1] = $row;
            }
        }
        # 返回查询到的数据
        $input['errCode'] = 0;
        $input['count'] = array(
            'bA' => $rows[0]['count'],
            'bG' => $rows[1]['count']
        );
        $input['message'] = 'success';
        print_r(json_encode($input));
    }
    mysqli_close($conn);
    exit;
}

if (isset($_POST)) {
    $postData = file_get_contents('php://input');
    $Data = !empty($postData) ? json_decode($postData, true) : array();

    if (isset($Data['nf'])) {
        $nf = " & {$Data['nf']}";
    } else {
        $nf = "";
    }

    $input = array(
        'errCode' => '',
        'count' => null,
        'message' => '',
        'type' => ''
    );

    if (empty($Data)) {
        $input['errCode'] = 404;
        $input['count'] = null;
        $input['message'] = '未接收到数据';
        print_r(json_encode($input));
    } else {
        $conn = @mysqli_connect('127.0.0.1', 'root', 'root', 'pdfrecord', 3306, '');

        if (mysqli_connect_error()) {
            $input['errCode'] = 403;
            $input['count'] = null;
            $input['message'] = '连接数据库失败';
            print_r(json_encode($input));
        } else {
            $query = "SELECT * FROM
            `index` WHERE
            `app_id`='{$Data['a']}'";
            $result = $conn->query($query);

            # 不存在则新建数据
            if (mysqli_num_rows($result) != 2) {
                $insertsql = "INSERT INTO `index`
                (`app_id`,`type`,`count`,`unix_time`) VALUES ";
                $conn->query($insertsql . "('{$Data['a']}','basicAccurate','0',UNIX_TIMESTAMP(NOW()))");
                $conn->query($insertsql . "('{$Data['a']}','basicGeneral','0',UNIX_TIMESTAMP(NOW()))");
                # 更新查询集
                $result = $conn->query($query);
            }

            $rows = array();
            # 获取查询的数据
            while ($row = mysqli_fetch_assoc($result)) {
                if ($row['type'] == 'basicAccurate') {
                    $rows[0] = $row;
                } else {
                    $rows[1] = $row;
                }
            }
            # 检查并刷新当天的免费次数
            if (strtotime(date('Ymd')) > $rows[0]['unix_time']) {
                # 当天0点的时间戳 > 已用识别记录的时间戳 :  记录是昨天的，需要刷新当天次数
                $c_str = "UPDATE `index` SET
                `count`=0 WHERE
                `app_id`='{$Data['a']}' AND";
                $conn->query($c_str . " `type`='basicAccurate'");
                $conn->query($c_str . " `type`='basicGeneral'");

                # 更新查询集
                $rows[0]['count'] = 0;
                $rows[1]['count'] = 0;
            }

            $sql = "UPDATE `index` SET
            `count`=`count`+1 ,
            `unix_time`=UNIX_TIMESTAMP(NOW()) WHERE
            `app_id`='{$Data['a']}' AND";
            $str = "";

            # 当天次数用完
            if ($rows[0]['count'] >= 500 && $rows[1]['count'] >= 50000) {
                $input['errCode'] = 210;
                $input['count'] = 50000;
                $input['message'] = '次数用光了';
                print_r(json_encode($input));
                exit;
            }
            # 当天次数未用完
            if ($rows[0]['count'] >= 500) {
                $str = "basicGeneral";
                $input['count'] = array(
                    'bA' => $rows[0]['count'],
                    'bG' => $rows[1]['count'] + 1
                );
            } else {
                $str = "basicAccurate";
                $input['count'] = array(
                    'bA' => $rows[0]['count'] + 1,
                    'bG' => $rows[1]['count']
                );
            }

            # 执行自增函数, 返回已用次数
            if ($conn->query($sql . "`type`='$str'")) {
                $input['errCode'] = 0;
                $input['message'] = 'success';
                $input['type'] = $str;
                print_r(json_encode($input));

                # (可选) 记录识别的文件和大小
                $filesize_mb = substr($Data['filesize'] / 1024 / 1024, 0, 4);
                $recordstr = "INSERT INTO `record`
                (`filename`,`filesize`,`app_id`,`type`,`unix_time`) VALUES
                ('{$Data['filename']}$nf','$filesize_mb','{$Data['a']}','$str',UNIX_TIMESTAMP(NOW()))";
                $conn->query($recordstr);
            }
        }
        mysqli_close($conn);
    }
}

```

## MySQL
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



<br />
<br />
参考来源:

[https://blog.csdn.net/qq_38144563/article/details/96138470](https://blog.csdn.net/qq_38144563/article/details/96138470)
[http://baijiahao.baidu.com/s?id=1599992188940440730](http://baijiahao.baidu.com/s?id=1599992188940440730)

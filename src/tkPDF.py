# coding=utf-8

import os
import sys
import time
import tkinter
from tkinter import messagebox

import requests

from myConvert import ConvertPDF, ConvertPic


class tkPDF:
    """
    创建PDF转换的Tk窗体\n
    width: 窗体宽度\n
    height: 窗体高度\n
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

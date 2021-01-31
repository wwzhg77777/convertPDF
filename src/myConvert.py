# coding=utf-8

import importlib
import os
import shutil
import sys
import tkinter.filedialog

import aip.ocr
import fitz
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import (LAParams, LTCurve, LTFigure, LTImage,
                             LTTextBoxHorizontal)
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from pdf_Ocr import pdf_Ocr

importlib.reload(sys)


class ConvertPDF:
    """
    PDF转换

    errCode:
    2001: 提示，PDF文件不支持文字版，返回pdf文件路径
    4001: 文本，创建文件夹失败
    4002: 文本，未选择文件
    4004: 文本，未完成文本提取

    """

    filedir: str
    filelist: list
    errCode: int
    errMessage: str

    __myOcr: pdf_Ocr
    __client: aip.ocr.AipOcr

    def __init__(self, app_info: list = None, url: str = ''):
        # 生成项目Ocr
        if app_info is not None:
            self.__client = aip.ocr.AipOcr(app_info[0], app_info[1],
                                           app_info[2])
            self.__myOcr = pdf_Ocr(self.__client, url)

        # 生成项目文件夹
        attr = self.__create_path()
        if attr['errCode'] == 0:
            self.errCode, self.filedir, self.filelist = attr['errCode'], attr[
                'result']['filedir'], attr['result']['filelist']
        else:
            self.errCode, self.errMessage = attr['errCode'], attr['result']

    @classmethod
    def __create_path(self):
        """
        新建解析PDF项目文件夹
        """

        filelist = tkinter.filedialog.askopenfilenames(
            initialdir='C',
            title='选择PDF文件',
            filetypes=(("PDF文件", '*.pdf'), ('All file', '*.*')))
        if filelist != '':
            first_file = os.path.basename(filelist[0])
            basedir = os.path.dirname(filelist[0])
            pathname = ConvertTools.loop_dir(
                base_dir=basedir,
                pathname=first_file[:str(first_file).rfind('.')]
                if len(filelist) == 1 else 'PDF项目')
            if pathname is None:
                return {'errCode': 4001, 'result': '创建文件夹失败'}
            else:
                os.mkdir(pathname)
                return {
                    'errCode': 0,
                    'result': {
                        'filedir': pathname,
                        'filelist': filelist
                    }
                }
        else:
            return {'errCode': 4002, 'result': '未选择文件'}

    def __parse_word(self, pdf_fullpath):
        """
        单个解析PDF转成文字
        不支持文字则弹窗提示
        """

        fp = open(pdf_fullpath, 'rb')  # 以二进制读模式打开
        # 用文件对象来创建一个pdf文档分析器
        parser = PDFParser(fp)
        # 创建一个PDF文档, 提供初始化密码
        doc = PDFDocument(parser)
        # 连接分析器 与文档对象
        parser.set_document(doc)

        # 检测文档是否提供txt转换，不提供就忽略
        if not doc.is_extractable:
            return {
                'errCode': 2001,
                'result': {
                    'message': 'PDF文件不支持文字版',
                    'pdf_fullpath': pdf_fullpath
                }
            }
        else:
            # 创建PDF资源管理器 来管理共享资源
            rsrcmgr = PDFResourceManager()
            # 创建一个PDF设备对象
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            # 创建一个PDF解释器对象
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            # 用来计数页面，图片，曲线，figure，水平文本框等对象的数量
            (num_page, num_image, num_curve, num_figure,
             num_TextBoxHorizontal) = (0, 0, 0, 0, 0)

            # 循环遍历列表，每次处理一个page的内容
            for page in PDFPage.create_pages(doc):  # 获取page列表
                num_page += 1  # 页面增一
                interpreter.process_page(page)
                # 接受该页面的LTPage对象
                layout = device.get_result()
                for x in layout:
                    if isinstance(x, LTImage):  # 图片对象
                        num_image += 1
                    if isinstance(x, LTCurve):  # 曲线对象
                        num_curve += 1
                    if isinstance(x, LTFigure):  # figure对象
                        num_figure += 1
                    if isinstance(x, LTTextBoxHorizontal):  # 获取文本内容
                        num_TextBoxHorizontal += 1  # 水平文本框对象增一
                        # 保存文本内容
                        file_without_suffix = os.path.basename(
                            pdf_fullpath[:str(pdf_fullpath).rfind('.')])
                        with open(self.filedir +
                                  '/%s.txt' % file_without_suffix,
                                  'a',
                                  encoding='utf-8') as f:  # 生成txt文件的文件名及路径
                            results = x.get_text()
                            f.write(results)
                            f.write('\n')
            if num_TextBoxHorizontal <= 0:
                return {
                    'errCode': 2001,
                    'result': {
                        'message': 'PDF文件不支持文字版',
                        'pdf_fullpath': pdf_fullpath
                    }
                }
            else:
                return {
                    'errCode': 0,
                    'result': {
                        '对象数量': num_figure,
                        '页面数': num_page,
                        '图片数': num_image,
                        '曲线数': num_curve,
                        '水平文本框': num_TextBoxHorizontal
                    }
                }

    def __parse_img(self, pdf_fullpath):
        """
        单个解析PDF转图片, 调用Ocr转文字
        """

        pdf_basename = os.path.basename(
            pdf_fullpath[:str(pdf_fullpath).rfind('.')])
        doc = fitz.Document(pdf_fullpath)
        # 新建存放img的文件夹
        img_path = self.filedir + '/%s_img' % pdf_basename
        if os.path.exists(img_path):
            shutil.rmtree(img_path)
        os.mkdir(img_path)
        # 新建存放pdf的文件夹
        pdf_path = self.filedir + '/pdf'
        if not os.path.exists(pdf_path):
            os.mkdir(pdf_path)
        # 存放pdf文件
        shutil.copy(pdf_fullpath, pdf_path)

        pageCount = 100 / doc.pageCount
        beilv = pageCount
        for pg in range(doc.pageCount):
            print('PDF转图片完成:' + str(round(pageCount, 2)) + '%')
            pageCount += beilv
            page = doc[pg]
            rotate = int(0)
            # 每个尺寸的缩放系数为2，这将为我们生成分辨率提高四倍的图像。
            zoom_x = 2.0
            zoom_y = 2.0
            trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
            pm = page.getDisplayList().getPixmap(matrix=trans, alpha=False)
            pm.writePNG(img_path + '/%s.png' % pg)
        return self.__myOcr.Ocr_img(img_path,
                                    self.filedir,
                                    pdf_fullpath,
                                    is_pdf=True)

    def mult_parse_word(self):
        """
        多个解析PDF转文字
        不支持文字则另存文件夹
        """

        count = 0
        # 遍历filelist的pdf文件转文字
        for pdffile in self.filelist:
            result = self.__parse_word(pdffile)
            if result['errCode'] == 0:  # 成功转换
                count += 1
            else:  # 2001: 不支持转换文字
                if not os.path.exists(self.filedir + '/不支持文字版的PDF'):
                    os.mkdir(self.filedir + '/不支持文字版的PDF')
                shutil.copy(pdffile, self.filedir + '/不支持文字版的PDF')
        return {
            'errCode': 0,
            'count': count,
            'message': '成功转换 %i 个PDF(文字版)文件' % count
        }

    def mult_parse_img(self):
        """
        多个解析PDF转图片, 调用Ocr转文字
        """

        pdf_count = 0
        count = {}
        # 遍历filelist的pdf文件
        for pdffile in self.filelist:
            result = self.__parse_img(pdffile)
            if result['errCode'] == 0:  # 成功转换
                pdf_count += 1
                count = {
                    'bA': result['count']['bA'],
                    'bG': result['count']['bG']
                }
            else:  # 转换出现错误
                return result
        return {
            'errCode': 0,
            'count': count,
            'message': '成功转换 %i 个PDF(扫描版)文件' % pdf_count
        }


class ConvertPic:
    """
    Pic转换
    """

    filedir: str
    filelist: list
    errCode: int
    errMessage: str

    __myOcr: pdf_Ocr
    __client: aip.ocr.AipOcr

    def __init__(self, app_info: list, url: str):
        # 生成项目Ocr
        self.__client = aip.ocr.AipOcr(app_info[0], app_info[1], app_info[2])
        self.__myOcr = pdf_Ocr(self.__client, url)

        # 生成项目文件夹
        attr = self.__create_path()
        if attr['errCode'] == 0:
            self.errCode, self.filedir, self.filelist = attr['errCode'], attr[
                'result']['filedir'], attr['result']['filelist']
        else:
            self.errCode, self.errMessage = attr['errCode'], attr['result']

    @classmethod
    def __create_path(self):
        """
        新建解析pic项目文件夹
        """

        filelist = tkinter.filedialog.askopenfilenames(
            initialdir='C',
            title='选择图片',
            filetypes=(("所有图片", ("*.jpg", "*.jpeg", "*.png")), ('All file',
                                                                '*.*')))
        if filelist != '':
            first_file = os.path.basename(filelist[0])
            basedir = os.path.dirname(filelist[0])
            pathname = ConvertTools.loop_dir(
                base_dir=basedir,
                pathname=first_file[:str(first_file).rfind('.')]
                if len(filelist) == 1 else 'Pic项目')
            if pathname is None:
                return {'errCode': 4001, 'result': '创建文件夹失败'}
            else:
                os.mkdir(pathname)
                return {
                    'errCode': 0,
                    'result': {
                        'filedir': pathname,
                        'filelist': filelist
                    }
                }
        else:
            return {'errCode': 4002, 'result': '未选择文件'}

    def mult_parse_pic(self):
        """
        多个解析图片转文字
        """

        img_path = self.filedir + '/img'
        if not os.path.exists(img_path):
            os.mkdir(img_path)

        count = {}
        # 复制列表文件到filedir\img目录
        for imgfile in self.filelist:
            shutil.copy(
                imgfile, '{imgpath_}/{imgfile_}'.format(
                    imgpath_=img_path, imgfile_=os.path.basename(imgfile)))

        # 执行函数: 图片文字识别
        result = self.__myOcr.Ocr_img(img_path, self.filedir)
        if result['errCode'] == 0:
            count = {'bA': result['count']['bA'], 'bG': result['count']['bG']}
        else:  # 转换出现错误
            return result
        return {
            'errCode': 0,
            'count': count,
            'message': '成功转换 %i 个图片文件' % result['pic_count']
        }


class ConvertTools:
    """
    提供PDF转换的辅助类
    """
    @staticmethod
    def loop_dir(base_dir: str,
                 pathname: str,
                 num: int = 0,
                 is_loop: bool = False):
        """
        新建指定名称的文件夹
        """

        fp1 = '{b_}/'.format(b_=base_dir)
        fp2 = 'Convert_%s' % pathname
        if is_loop:
            fullpath = fp1 + '(重名%i)' % num + fp2
        else:
            fullpath = fp1 + fp2

        if (os.path.exists(fullpath) and os.path.isdir(fullpath)):
            num += 1
            return ConvertTools.loop_dir(base_dir=base_dir,
                                         num=num,
                                         pathname=pathname,
                                         is_loop=True)
        else:
            return fullpath

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

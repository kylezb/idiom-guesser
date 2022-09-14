import time
import tkinter
from functools import partial
from io import BytesIO
from tkinter import Text

import numpy as np
import pyperclip
from PIL import Image
from PIL import ImageGrab
from cnocr import CnOcr
from cv2 import cv2
from pypinyin import pinyin, Style

from guesser import get_sql, query

import warnings

warnings.filterwarnings("ignore")


def is_zh(word):
    """

    :param word:
    :return:
    """
    for index, item in enumerate(word):
        if item < '\u4e00' or '\u9fff' < item:  # 汉字占2单位宽度
            return False
        else:
            continue
    return True


def tones5(word):
    """
    返回声调 （5 轻声，1，2，3，4）
    :param word:
    :return:
    """
    py = pinyin(word.strip(), style=Style.TONE3, strict=False, neutral_tone_with_five=True)
    tones = []
    for p in py:
        tones.append(int(p[0][-1]))
    return tones


def wordle(idiom, shengmu_list, yunmu_list, shengdiao_list, idiom_list, condition, strict=True):
    cod = get_sql(idiom=idiom, idiom_list=idiom_list, shengmu_list=shengmu_list, yunmu_list=yunmu_list,
                  shengdiao_list=shengdiao_list, strict=strict)
    condition += cod
    if strict:
        sql = 'select word,freq from STRICT where ' + str(' and '.join(condition)) + ' ORDER BY freq desc '
    else:
        sql = 'select word,freq from IDIOM where ' + str(' and '.join(condition)) + ' ORDER BY freq desc '

    idioms = query(sql, echo=False)
    return idioms, condition


#
# def ocr(img=None):
#     """
#     OCR识别
#     :param img:
#     :return:
#     """
#     _ocr = ddddocr.DdddOcr(show_ad=False)
#     res = _ocr.classification(img)
#
#     return res


def ocr(img=None):
    """
    OCR识别
    :param img:
    :return:
    """
    ocr = CnOcr(root='ocr_model')
    res = ocr.ocr_for_single_line(img)
    # print("Predicted Chars:", res)
    return res[0][0][0]


def get_word_ocr(img=None):
    """
    返回文字识别结果
    :param img:
    :return:
    """
    x = (img.shape[0])
    y = (img.shape[1])
    word_img = img[int(x * 0.4): x - 20, 10:y - 10]
    imgGray = cv2.cvtColor(word_img, cv2.COLOR_RGB2GRAY)  # 转灰度图
    ret, thresh1 = cv2.threshold(imgGray, 165, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((2, 1), np.uint8)
    thresh1 = cv2.erode(thresh1, kernel, iterations=1)

    # bytesIO = BytesIO()
    # image = Image.fromarray(cv2.cvtColor(thresh1, cv2.COLOR_BGR2RGB))
    # image.save(bytesIO, format='PNG')
    # word = ocr(bytesIO.getvalue())
    word = ocr(thresh1)
    return word


def getVProjection(image, posi='top', name=''):
    """
    只为了获取垂直方向投影 产生的图像不参与运算
    :param image:
    :param posi:
    :param name:
    :return:
    """

    # 将image图像转为黑白二值图，ret接收当前的阈值，thresh1接收输出的二值图
    ret, thresh1 = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    if posi == 'top':
        # 卷积核 2，1 水平方向 腐蚀（颜色取反 故用 腐蚀 代替膨胀）
        kernel = np.ones((2, 1), np.uint8)
        # thresh1 = cv2.morphologyEx(thresh1, cv2.MORPH_CLOSE, kernel)
        # thresh1 = cv2.morphologyEx(thresh1, cv2.MORPH_OPEN, kernel)
        thresh1 = cv2.dilate(thresh1, np.ones((2, 2), np.uint8), iterations=1)
        thresh1 = cv2.erode(thresh1, np.ones((4, 2), np.uint8), iterations=3)

        # cv2.imshow(f'Vimag{name}', image)
        # cv2.imshow(f'Vimage{name}', thresh1)
        # cv2.waitKey()

    if posi == 'bottom':
        # 卷积核 2，1 水平方向 腐蚀（颜色取反 故用 腐蚀 代替膨胀）
        # kernel = np.ones((1, 1), np.uint8)
        # thresh1 = cv2.dilate(thresh1, kernel, iterations=2)
        # thresh1 = cv2.erode(thresh1, np.ones((2, 2), np.uint8), iterations=2)
        # 先腐蚀 再膨胀
        thresh1 = cv2.dilate(thresh1, np.ones((3, 3), np.uint8), iterations=1)
        thresh1 = cv2.erode(thresh1, np.ones((5, 2), np.uint8), iterations=3)
        # cv2.imshow(f'Vimag{name}', image)
        # cv2.imshow(f'Vimage{name}', thresh1)
        # cv2.waitKey()

    (h, w) = thresh1.shape  # 返回高和宽
    a = [0 for z in range(0, w)]  # a = [0,0,0,...,0,0]初始化一个长度为w的数组，用于记录每一列的黑点个数

    # 记录每一列的波峰
    for j in range(0, w):  # 遍历一列
        for i in range(0, h):  # 遍历一行
            if thresh1[i, j] == 0:  # 如果该点为黑点
                a[j] += 1  # 该列的计数器加一计数
                thresh1[i, j] = 255  # 记录完后将其变为白色

    for j in range(0, w):  # 遍历每一列
        for i in range((h - a[j]), h):  # 从该列应该变黑的最顶部的点开始向最底部涂黑
            thresh1[i, j] = 0  # 涂黑
    index_ = []
    th = 5
    if posi == 'top':
        th = 8
    if posi == 'bottom':
        th = 1
    for index, item in enumerate(a):
        if item >= th:
            index_.append(index)
    # if posi == 'top':
    #
    #     cv2.imshow(f'Vimage2{name}', thresh1)
    #     cv2.waitKey()
    return index_


def top(img, name=''):
    (h, w) = img.shape  # 返回高和宽
    top = img[0:int(h * 0.4), 0:w]
    # kernel = np.ones((1, 1), np.uint8)
    # img = cv2.dilate(top, kernel, iterations=2)
    #
    # cv2.imshow(f"bin_top{name} ", top)
    # cv2.waitKey()
    x_posi = getVProjection(top, posi='top', name=name)

    return x_posi


def bottom(img, name=''):
    (h, w) = img.shape  # 返回高和宽
    bottom = img[int(h * 0.4): h - 10, 10:w - 10]

    x_posi = getVProjection(bottom, posi='bottom')
    # x轴黑色像素数量过多可认为是该位置为绿色 黑白取反 互换颜色
    if len(x_posi) / w >= 0.75:
        bottom = ~bottom
    # cv2.imshow(f"bin{name} ", bottom)
    # cv2.waitKey()

    word = ''
    if len(x_posi) > 1:
        # 卷积核 2，1 水平方向 腐蚀（颜色取反 故用 腐蚀 代替膨胀）
        kernel = np.ones((2, 2), np.uint8)
        img_dilate = cv2.erode(bottom, kernel, iterations=2)
        # cv2.imshow(f"bin{name} ", img_dilate)
        # cv2.waitKey()

        word = ocr(img_dilate)

        # # cv 转二进制文件
        # bytesIO = BytesIO()
        # image = Image.fromarray(cv2.cvtColor(img_dilate, cv2.COLOR_BGR2RGB))
        # image.save(bytesIO, format='PNG')
        # word = ocr(bytesIO.getvalue())
        # print(word)

    return x_posi, word


def calc_diff(pixel, bg_color):
    #     计算pixel与背景的离差平方和，作为当前像素点与背景相似程度的度量
    return (pixel[0] - bg_color[0]) ** 2 + (pixel[1] - bg_color[1]) ** 2 + (pixel[2] - bg_color[2]) ** 2


def remove_one_color_opencv(img, delete_color, threshold, name=''):  # 采用opencv方式
    ttt = time.time()
    img1 = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)  # 将图像转成带透明通道的BGRA格式
    for i in range(img1.shape[0]):
        for j in range(img1.shape[1]):
            if calc_diff(img1[i][j], delete_color) > threshold:
                img1[i][j] = (255, 255, 255, 1)

    # cv2.imshow('dsad', img1)
    # cv2.waitKey()
    # print(time.time() - ttt)

    image1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    retval, dst = cv2.threshold(image1, 150, 255, cv2.THRESH_BINARY)
    # cv2.imshow(f"bin{name} ", dst)
    # cv2.waitKey()
    # cv2.imshow(f"gray{name} ", image1)

    a = top(dst, name)
    b, word = bottom(dst, name)
    data = {
        'top': a,
        'bottom': b,
        'word': word
    }
    return data


def remove_one_color_pillow(img, delete_color, threshold, name=''):  # 采用pillow方式
    ttt = time.time()

    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    img2 = img.convert('RGBA')
    pixdata = img2.load()
    for y in range(img2.size[1]):
        for x in range(img2.size[0]):
            if calc_diff(pixdata[x, y], delete_color) > threshold:
                pixdata[x, y] = (255, 255, 255, 0)

    r, g, b, a = img2.split()  # 分离通道
    img2 = Image.merge("RGB", (b, g, r))  # 合并通道 RGB->BGR
    img = np.array(img2)  # img对象转cv矩阵

    image1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    retval, dst = cv2.threshold(image1, 150, 255, cv2.THRESH_BINARY)
    # cv2.imshow(f"bin{name} ", dst)
    # cv2.imshow(f"gray{name} ", image1)

    # cv2.imshow('dsad', dst)
    # cv2.waitKey()
    # return
    # print(time.time() - ttt)

    a = top(dst, 'name')
    b, word = bottom(dst, 'name')
    data = {
        'top': a,
        'bottom': b,
        'word': word,
    }
    return data


def remove_yellow(img, des=''):  # 采用opencv方式
    delete_color = [60, 120, 200]
    threshold = 5000
    return remove_one_color_opencv(img, delete_color, threshold, des)


def remove_green(img, des=''):  # 采用opencv方式
    delete_color = [130, 165, 50]
    threshold = 5000
    return remove_one_color_opencv(img, delete_color, threshold, des)


def remove_gray(img, des=''):  # 采用opencv方式
    delete_color = [125, 125, 125]
    threshold = 1000
    return remove_one_color_opencv(img, delete_color, threshold, des)


def remove_yellow2(img, des=''):
    delete_color = [200, 120, 60]
    threshold = 5000
    return remove_one_color_pillow(img, delete_color, threshold, des)


def remove_green2(img, des=''):
    delete_color = [30, 155, 150]
    threshold = 5000
    return remove_one_color_pillow(img, delete_color, threshold, des)


def remove_gray2(img, des=''):
    delete_color = [140, 130, 120]
    threshold = 600
    return remove_one_color_pillow(img, delete_color, threshold, des)


def remove_black(img, des=''):
    delete_color = [60, 65, 80]
    threshold = 600
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    img2 = img.convert('RGBA')
    pixdata = img2.load()
    for y in range(img2.size[1]):
        for x in range(img2.size[0]):
            if calc_diff(pixdata[x, y], delete_color) < threshold:
                pixdata[x, y] = (255, 255, 255, 0)

    for y in range(img2.size[1]):
        for x in range(img2.size[0]):
            if calc_diff(pixdata[x, y], [30, 155, 150]) < 9700:
                pixdata[x, y] = (255, 255, 255, 0)
    for y in range(img2.size[1]):
        for x in range(img2.size[0]):
            if calc_diff(pixdata[x, y], [255, 240, 255]) < 120:
                pixdata[x, y] = (128, 128, 128, 0)
    r, g, b, a = img2.split()  # 分离通道
    img2 = Image.merge("RGB", (b, g, r))  # 合并通道 RGB->BGR
    img = np.array(img2)  # img对象转cv矩阵

    image1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    retval, dst = cv2.threshold(image1, 150, 255, cv2.THRESH_BINARY)
    # cv2.imshow(f"bin{name} ", dst)
    cv2.imshow(f"grayfff ", image1)
    cv2.waitKey()
    # cv2.imshow('dsad', dst)
    # cv2.waitKey()
    # return
    # print(time.time() - ttt)

    a = top(dst, 'name')
    b, word = bottom(dst, 'name')
    data = {
        'top': a,
        'bottom': b,
        'word': word
    }
    return data


# 获取图片坐标bgr值
def get_pix_bgr(img, x: int, y: int):
    px = img[x, y]
    blue = img[x, y, 0]
    green = img[x, y, 1]
    red = img[x, y, 2]
    return blue, green, red


def ShapeDetection(img):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 寻找轮廓点
    c = []
    for obj in contours:
        # cv2.drawContours(imgContour, obj, -1, (255, 0, 0), 4)  # 绘制轮廓线
        perimeter = cv2.arcLength(obj, True)  # 计算轮廓周长
        approx = cv2.approxPolyDP(obj, 0.02 * perimeter, True)  # 获取轮廓角点坐标
        x, y, w, h = cv2.boundingRect(approx)  # 获取坐标值和宽度、高度
        # cv2.rectangle(imgContour, (x, y), (x + w, y + h), (0, 0, 255), 2)
        c.append([x, y, w, h])
    c.reverse()
    return c


def get_img_row(data):
    row = []
    tmp = []
    for index, item in enumerate(data[:-4]):
        tmp.append(item)
        if (index + 1) % 4 == 0:
            row.append(tmp)
            tmp = []
    return row


def show(data, img, th=0, **kwargs):
    condition = []

    for index, item in enumerate(data[:]):
        # print(item)  # [[40, 40, 160, 160], [220, 40, 160, 160], [400, 40, 160, 160], [580, 40, 160, 160]]
        x, y, w, h = item[0][0], item[0][1], item[3][0] - item[0][0] + item[0][2], item[0][3]
        # img_ = img[y + th: y - th + h, x + th:x - th + w]
        #
        # img_ = img[y + th: y - th + h, x + th:x - th + w]
        # a = remove_black(img_)
        # # a = remove_gray2(img_)
        # # a = remove_green2(img_)
        # # a = remove_yellow2(img_)
        #
        # # cv2.imshow(f"Original img {x, y}", a)
        # continue

        idiom = ''
        parms = {
            'sm': [0, 0, 0, 0],
            'ym': [0, 0, 0, 0],
            'sd': [0, 0, 0, 0],
            'word': [0, 0, 0, 0],
            'idiom': '',
        }
        for i, d in enumerate(item[:]):
            x, y, w, h = d
            # cv2.imshow(f"Original img {x,y}", img[y: y + h, x:x + w])
            img_ = img[y + th: y - th + h, x + th:x - th + w]

            gray = remove_gray2(img_, f'--gray i')
            green = remove_green2(img_, f'--green i')
            yellow = remove_yellow2(img_, f'--yellow i')
            # print(gray.get('top'))
            # print(green.get('top'))
            # print(yellow.get('top'))

            sm, ym, sd, word = 3, 3, 3, 0
            b, g, r = get_pix_bgr(img_, 20, 20)
            if calc_diff([b, g, r], [155, 156, 28]) < 100:
                idiom += get_word_ocr(img_)

                sm, ym, sd, word = 2, 2, 2, 2
                parms['sm'][i] = sm
                parms['ym'][i] = ym
                parms['sd'][i] = sd
                parms['word'][i] = word
                parms['idiom'] = idiom

                continue
            else:
                if gray.get('bottom'):
                    idiom += gray.get('word')
                    word = 0
                if green.get('bottom'):
                    idiom += green.get('word')
                    word = 2
                if yellow.get('bottom'):
                    idiom += yellow.get('word')
                    word = 1
            # if i == 3:
            # # debugging
            #     print(yellow.get('top'))
            #     print(gray.get('top'))
            #     print(green.get('top'))

            # 问就是排列组合 27种 硬写if else
            if not gray.get('top'):

                if not yellow.get('top'):
                    sm, ym, sd = 2, 2, 2
                elif not green.get('top'):
                    sm, ym, sd = 1, 1, 1
                elif yellow.get('top')[0] > green.get('top')[0]:
                    if yellow.get('top')[-1] < green.get('top')[-1]:
                        sm, ym, sd = 2, 1, 2
                    if yellow.get('top')[-1] > green.get('top')[-1]:
                        if green.get('top')[-1] > w / 2 and len(yellow.get('top')) / 160 < 0.1:  # 横向像素占比>0.1说明韵母、声调颜色相同
                            sm, ym, sd = 2, 2, 1
                        else:
                            sm, ym, sd = 2, 1, 1
                elif green.get('top')[0] > yellow.get('top')[0]:
                    if green.get('top')[-1] < yellow.get('top')[-1]:
                        sm, ym, sd = 1, 2, 1
                    if green.get('top')[-1] > yellow.get('top')[-1]:
                        if yellow.get('top')[-1] > w / 2 and len(green.get('top')) / 160 < 0.1:
                            sm, ym, sd = 1, 1, 2
                        else:
                            sm, ym, sd = 1, 2, 2

            if gray.get('top'):
                if not green.get('top'):
                    if not yellow.get('top'):
                        sm, ym, sd = 0, 0, 0

                    elif yellow.get('top')[0] > gray.get('top')[0]:
                        if yellow.get('top')[-1] < gray.get('top')[-1]:
                            sm, ym, sd = 0, 1, 0
                        if yellow.get('top')[-1] > gray.get('top')[-1]:
                            if gray.get('top')[-1] > w / 2 and len(yellow.get('top')) / 160 < 0.1:
                                sm, ym, sd = 0, 0, 1
                            else:
                                sm, ym, sd = 0, 1, 1

                    elif gray.get('top')[0] > yellow.get('top')[0]:
                        if gray.get('top')[-1] < yellow.get('top')[-1]:
                            sm, ym, sd = 1, 0, 1
                        if gray.get('top')[-1] > yellow.get('top')[-1]:
                            if yellow.get('top')[-1] > w / 2 and len(gray.get('top')) / 160 < 0.1:
                                sm, ym, sd = 1, 1, 0
                            else:
                                sm, ym, sd = 1, 0, 0

                elif not yellow.get('top'):
                    if green.get('top')[0] > gray.get('top')[0]:
                        if green.get('top')[-1] < gray.get('top')[-1]:
                            sm, ym, sd = 0, 2, 0
                        if green.get('top')[-1] > gray.get('top')[-1]:
                            if gray.get('top')[-1] > w / 2 and len(green.get('top')) / 160 < 0.1:
                                sm, ym, sd = 0, 0, 2
                            else:
                                sm, ym, sd = 0, 2, 2

                    if gray.get('top')[0] > green.get('top')[0]:
                        if gray.get('top')[-1] < green.get('top')[-1]:
                            sm, ym, sd = 2, 0, 2
                        if gray.get('top')[-1] > green.get('top')[-1]:
                            if green.get('top')[-1] > w / 2 and len(gray.get('top')) / 160 < 0.1:
                                sm, ym, sd = 2, 2, 0
                            else:
                                sm, ym, sd = 2, 0, 0

                else:
                    if green.get('top')[0] > gray.get('top')[0]:
                        if yellow.get('top')[0] > green.get('top')[0]:
                            sm, ym, sd = 0, 2, 1
                        elif gray.get('top')[0] > yellow.get('top')[0]:
                            sm, ym, sd = 1, 0, 2
                        else:
                            sm, ym, sd = 0, 1, 2
                    elif green.get('top')[0] < gray.get('top')[0]:
                        if gray.get('top')[0] < yellow.get('top')[0]:
                            sm, ym, sd = 2, 0, 1
                        elif yellow.get('top')[0] > green.get('top')[0]:
                            sm, ym, sd = 2, 1, 0
                        else:
                            sm, ym, sd = 1, 2, 0

            parms['sm'][i] = sm
            parms['ym'][i] = ym
            parms['sd'][i] = sd
            parms['word'][i] = word
            parms['idiom'] = idiom

            # print(sm, ym, sd, word)
        print(parms)
        if 3 in parms['ym'] or 3 in parms['sm'] or 3 in parms['sd']:
            continue
        if len(parms['idiom']) != 4:
            continue
        if not is_zh(parms['idiom']):
            continue

        if 5 in tones5(parms['idiom']):
            continue

        # todo 伪代码
        # if '多音字' in parms['idiom']:
        #     parms['sd'] = []

        idioms, condition = wordle(parms['idiom'], parms['sm'], parms['ym'],
                                   parms['sd'], parms['word'], condition, strict=False)

        text = kwargs.get('text')
        clip = ''
        if text:
            text.insert('insert', '\n'.join(i[0] for i in idioms[:15]) + '\n\n')
        print(f'{len(idioms)}\t' + '\t'.join(i[0] for i in idioms[:10]))
        if idioms:
            clip = idioms[0][0]
        if clip:
            pyperclip.copy(f"{clip}")

        if len(idioms) <= 5:
            pyperclip.copy(f"{clip}")

            # print(idioms[0][0])
            break


def main(img=None):
    if img is None:
        path = '59.jpg'
        img = cv2.imread(path)
    # img = cv2.resize(img, (0, 0), fx=0.9, fy=0.9, interpolation=cv2.INTER_CUBIC)
    imgContour = img.copy()

    imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 转灰度图
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)  # 高斯模糊
    imgCanny = cv2.Canny(imgBlur, 60, 60)  # Canny算子边缘检测
    data = ShapeDetection(imgCanny)  # 形状检测
    idiom = get_img_row(data)
    show(idiom, img)
    # cv2.imshow("Original img", img)
    # cv2.imshow("imgGray", imgGray)
    # cv2.imshow("imgBlur", imgBlur)
    # cv2.imshow("imgCanny", imgCanny)
    # cv2.imshow("shape Detection", imgContour)

    # cv2.waitKey(0)


def grab_img(**kwargs):
    # 保存剪切板内图片
    im = ImageGrab.grabclipboard()
    if isinstance(im, Image.Image):
        print("Image: size : %s, mode: %s" % (im.size, im.mode))

        r, g, b = im.split()  # 分离通道
        im = Image.merge("RGB", (b, g, r))  # 合并通道 RGB->BGR
        img = np.array(im)  # img对象转cv矩阵

        # cv2.imshow('dsd', img)
        # cv2.waitKey(0)
        main(img)

        # imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 转灰度图
        # imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)  # 高斯模糊
        # imgCanny = cv2.Canny(imgBlur, 60, 60)  # Canny算子边缘检测
        # data = ShapeDetection(imgCanny)  # 形状检测
        # idiom = get_img_row(data)
        #
        # return idiom, img
    else:
        print("clipboard is empty")
        return None, None


def main_fun(text: Text):
    text.delete('1.0', 'end')
    idiom, img = grab_img()
    if not idiom:
        text.insert('insert', '粘贴板第一项未发现图片')
    else:
        show(idiom, img, text=text)


def windows():
    # 界面展示

    win = tkinter.Tk()  # 创建主窗口
    win.title('猜成语')
    win.geometry("400x500")
    win.resizable(width=False, height=False)  # 宽不可变, 高可变,默认为True
    text2 = tkinter.Text(win, height=25, width=45, font=('微软雅黑', 12))
    text2.place(x=0, y=50)

    button2 = tkinter.Button(win, text="点击运行", command=partial(main_fun, text2), font=('楷体', 14))
    button2.place(x=300, y=10)
    # 创建子窗口
    win.mainloop()


if __name__ == '__main__':
    # code_ocr()
    t = time.time()
    # print(np.ones((3, 3), np.uint8))
    # main()
    grab_img()
    # paddle_ocr('')
    # windows()
    print('耗时： ', time.time() - t)
    # print(pinyin('不想玩了'))
    # print(pinyin('一个日子'))
    # print(pinyin('一蹶不振'))
    # print(pinyin('万人空巷'))
    # print(pinyin('滥用职权'))

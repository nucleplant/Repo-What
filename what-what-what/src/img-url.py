# -*- coding: utf-8 -*-

import urllib,base64

data = urllib.urlopen('http://imgcomic.naver.com/webtoon/335885/387/20121120162539_IMAG01_1.jpg')
data_uri = data.read().encode('base64').replace('\n', '')
img_tag = '<img src="data:image/jpeg;base64,{0}">'.format(data_uri)
print(img_tag)

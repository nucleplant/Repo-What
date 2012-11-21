# -*- coding: utf-8 -*-

"""
BeautifulSoup을 이용한 네이버 웹툰 긁어오기

참고:
http://toors.tistory.com/entry/Python-BeautifulSoup%EC%9C%BC%EB%A1%9C-%EA%B2%8C%EC%8B%9C%ED%8C%90-%EA%B8%81%EC%96%B4%EC%98%A4%EA%B8%B0-%ED%8C%A8%ED%84%B4

"""

import urllib, BeautifulSoup

data = urllib.urlopen('http://comic.naver.com/webtoon/list.nhn?titleId=335885&weekday=tue')
soup = BeautifulSoup.BeautifulSoup(data)
cartoons = soup.findAll('td', attrs={'class':'title'})
title = cartoons[0].find('a').text
link = cartoons[0].find('a')['href']

data = urllib.urlopen('http://comic.naver.com'+link)
soup = BeautifulSoup.BeautifulSoup(data)
imglinks = soup.find('div', attrs={'class':'wt_viewer'}).findAll('img')
imglist = []
for imglink in imglinks:
    imglist.append(imglink['src']) 
    
print title, imglist
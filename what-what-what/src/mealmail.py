# -*- coding: utf-8 -*-

import os, httplib2, urllib, logging, json, webapp2, jinja2, BeautifulSoup
from google.appengine.api import mail
from datetime import tzinfo, timedelta, datetime


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Seoul_tzinfo(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=9)
    def dst(self, dt):
        return timedelta(0)
    
today = datetime.now(Seoul_tzinfo()).strftime("%Y-%m-%d")


def postAction(http, url, body):
    try:    
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept-Language': 'ko-kr',
                   'Connection': 'keep-alive',
                   'Proxy-Connection': 'keep-alive',
                   'User-Agent': 'Mozilla/4.0 (compatible;)'}        
        response, content = http.request(url, 'POST', headers=headers, body=body)
        
    #    return False
        if (response['status'] != '200') or (content == '')  :
            logging.error("status error %s", str(url))
            return False 
        
        content = json.loads(content.decode('euc-kr'))
        
        if (content == None):
            logging.error("Result error (No Content) %s", str(url+' (Post)'+body))
            return False       

        return content
    except:
        logging.exception("Exception : %s ", str(url +' (Post)'+ body))        
        return False


def sendMail(to, sbj, html):
    mail.send_mail(sender='what@what-what-what.appspotmail.com', to = to, subject = sbj, body = '', html = html)

def naverWebtoon():
    data = urllib.urlopen('http://comic.naver.com/webtoon/list.nhn?titleId=335885&weekday=tue')
    soup = BeautifulSoup.BeautifulSoup(data)
    cartoons = soup.findAll('td', attrs={'class':'title'})
    lastTitle = cartoons[0].find('a').text
    lastLink = cartoons[0].find('a')['href']
    
    title = soup.find('div', attrs={'class':'comicinfo'}).find('img')['title']
    title += ' ('+lastTitle+')'
    
    data = urllib.urlopen('http://comic.naver.com'+lastLink)
    soup = BeautifulSoup.BeautifulSoup(data)
    imglinks = soup.find('div', attrs={'class':'wt_viewer'}).findAll('img')
    imglist = []
    for imglink in imglinks:
        imglist.append(imglink['src'])         
    return title, imglist
     
def genHTML():        
    http = httplib2.Http()
    url = 'http://www.welstory.com/mobile/menu_today.jsp'
    body = {'hall_no': 'E329' , 'date': today, 'device': 'iphone' }
    content= postAction(http, url, urllib.urlencode(body))

    title1, imglist1 = naverWebtoon()
    
    template_values = {
        'content' : content,
        'title1' : title1,
        'webtoon1' : imglist1,
    }
    
    template = jinja_environment.get_template('lunchmail.html')
    return template.render(template_values)

class MealMail(webapp2.RequestHandler):
    def get(self):        
        revList = ['lovedino@gmail.com','wonjeon.ahn@gmail.com', 'erimpre@gmail.com', 'seungryun.lee@samsung.com', 'wonjeon.ahn@samsung.com','ym1127.park@samsung.com']        
        sendMail( revList,  '['+ today + u'] 이-건-뭐-지-?', genHTML())            

class MealWeb(webapp2.RequestHandler):
    def get(self):        
        self.response.out.write( genHTML()) 


app = webapp2.WSGIApplication([('/meal/mail', MealMail),
                               ('/meal/web', MealWeb),
                                                             
                               ], debug=True)
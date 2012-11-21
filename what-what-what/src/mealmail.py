# -*- coding: utf-8 -*-

import os, httplib2, urllib, logging, json, webapp2, jinja2, BeautifulSoup, base64
from google.appengine.api import mail
from google.appengine.api import taskqueue
from datetime import tzinfo, timedelta, datetime


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Seoul_tzinfo(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=9)
    def dst(self, dt):
        return timedelta(0)
    
today = datetime.now(Seoul_tzinfo()).strftime("%Y-%m-%d")
weekName = datetime.now(Seoul_tzinfo()).strftime("%a")



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

def img2base64(url):
    http = httplib2.Http()
    headers = {'referer': 'http://comic.naver.com/webtoon/',
               'Accept-Language': 'ko-kr',
               'Connection': 'keep-alive',
               'Proxy-Connection': 'keep-alive',
               'User-Agent': 'Mozilla/4.0 (compatible;)'}        
    response, content = http.request(url, 'GET', headers=headers, body='')
    
    
    data_uri = content.encode('base64').replace('\n', '')
    
#    data_uri = urllib.urlopen(url).read().encode('base64').replace('\n', '')
    
    img_tag = '"data:image/jpeg;base64,{0}"'.format(data_uri)
    return img_tag

def naverWebtoon(url):
    data = urllib.urlopen(url)
    soup = BeautifulSoup.BeautifulSoup(data)
    cartoons = soup.findAll('td', attrs={'class':'title'})
    lastTitle = cartoons[0].find('a').text
    lastLink = cartoons[0].find('a')['href']
    
    title = soup.find('div', attrs={'class':'comicinfo'}).find('img')['title']
#    title += ' ('+lastTitle+')'
    
    data = urllib.urlopen('http://comic.naver.com'+lastLink)
    soup = BeautifulSoup.BeautifulSoup(data)
    imglinks = soup.find('div', attrs={'class':'wt_viewer'}).findAll('img')
    imglist = []
    for imglink in imglinks:
        imglist.append(img2base64(imglink['src']))
    
    webtoon={}    
    webtoon['title'] = title
    webtoon['subtitle'] = lastTitle
    webtoon['imglist'] = imglist
    return webtoon

def webtoons():
    webtoonList=[]
#    urls = ['http://comic.naver.com/webtoon/list.nhn?titleId=335885&weekday=tue']
    weekurls = {'Mon': ['http://comic.naver.com/webtoon/list.nhn?titleId=25613&weekday=mon'],
                'Tue': ['http://comic.naver.com/webtoon/list.nhn?titleId=20853&weekday=tue'],
                'Wed': ['http://comic.naver.com/webtoon/list.nhn?titleId=103759&weekday=wed'],
                'Thu': ['http://comic.naver.com/webtoon/list.nhn?titleId=507275&weekday=thu'],
                'Fri': ['http://comic.naver.com/webtoon/list.nhn?titleId=20853&weekday=fri'],
                'Sat': ['http://comic.naver.com/webtoon/list.nhn?titleId=25613&weekday=sat'],
                'Sun': ['http://comic.naver.com/webtoon/list.nhn?titleId=26316&weekday=sun']                
                }
#    urls = weekurls[weekName]    
    
    for url in weekurls[weekName]:
        webtoonList.append(naverWebtoon(url))
    return webtoonList

def todaysmeal():
    http = httplib2.Http()
    url = 'http://www.welstory.com/mobile/menu_today.jsp'
    body = {'hall_no': 'E329' , 'date': today, 'device': 'iphone' }
    return postAction(http, url, urllib.urlencode(body))
    
     
def genHTML():        
    template_values = {
        'todaysmeal' : todaysmeal(),
        'webtoons' : webtoons(),
    }    
    template = jinja_environment.get_template('lunchmail.html')
    return template.render(template_values)

class MealMailTask(webapp2.RequestHandler):
    def post(self):
        mode = self.request.get('mode')
        if mode == 'debug':
            revList = ['lovedino@gmail.com']
        else:                    
            revList = ['lovedino@gmail.com','wonjeon.ahn@gmail.com', 'erimpre@gmail.com', 'seungryun.lee@samsung.com', 'wonjeon.ahn@samsung.com','ym1127.park@samsung.com']        
        sendMail( revList,  '['+ today + u'] 이-건-뭐-지-?', genHTML())            

class MealMail(webapp2.RequestHandler):
    def get(self):
        mode = self.request.get('mode')        
        taskqueue.add(url="/meal/mail/task", params={'mode': mode})
        self.response.out.write( u"""<HTML><body>메일발송! """+mode+"""</body></HTML>""") 
         

class MealWeb(webapp2.RequestHandler):
    def get(self):        
        self.response.out.write( genHTML()) 


app = webapp2.WSGIApplication([('/meal/mail', MealMail),
                               ('/meal/mail/task', MealMailTask),
                               ('/meal/web', MealWeb),
                                                             
                               ], debug=True)
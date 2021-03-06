#coding=utf-8
from nntplib import NNTP
from time import strftime,time,localtime
from email import message_from_string
from urllib import urlopen
import re
import textwrap

day = 24*60*60

def wrap(string,max=70):
    """
    将字符串调整为最大行宽
    :param string:
    :param max:
    :return:
    """
    return '\n'.join(textwrap.wrap(string))+'\n'

class NewsAgent:
    """
    可以从新闻来源获取新闻项目并且发布到新闻目标的对象。
    """
    def __init__(self):
        self.sources=[]
        self.destinations=[]
    def addSource(self,source):
        self.sources.append(source)
    def addDestination(self,dest):
        self.destinations.append(dest)
    def distribute(self):
        """
        从所有来源获取所有新闻并且发布到所有目标
        :return:
        """
        items = []
        for source in self.sources:
            items.extend(source.getItems())
        for dest in self.destinations:
            dest.receiveItems(items)

class NewsItem:
    """
    包括标题和主体文本的简单新闻项目
    """
    def __init__(self,body,title):
        self.body = body
        self.title = title

class NNTPSource:
    """
    从NNTP租中获取新闻项目的x新闻来源


    """
    def __init__(self,source,group,window):
        self.source = source
        self.group = group
        self.window = window
    def getItems(self):
        start = localtime(time()-self.window*day)
        date = strftime('%y%m%d',start)
        hour = strftime('%H%M%S',start)
        server = NNTP(self.source)

        ids = server.newnews(self.group,date,hour)[1]

        for id in ids:
            lines = server.article(id)[3]
            message = message_from_string('\n'.join(lines))

            title = message['subject']
            body = message.get_payload()
            if message.is_multipart():
                body = body[0]

            yield NewsItem(title,body)
        server.quit()
class SimpleWebSource:
    """
    使用正则表达式从网页中提取新闻项目的新闻来源
    """
    def __init__(self,url,titlePattern,bodyPattern):
        self.url = url
        self.titlePattern = re.compile(titlePattern)
        self.bodyPattern = re.compile(bodyPattern)

    def getItems(self):
        text = urlopen(self.url).read()
        titles = self.titlePattern.findall(text)
        bodies = self.bodyPattern.findall(text)
        for title,body in zip(titles,bodies):
            yield NewsItem(title,wrap(body))

class PlainDestination:
    """
    将所有新闻项目格式化为纯文本的新闻目标类
    """
    def receiveItems(self,items):
        for item in items:
            print item.title
            print '-'*len(item.title)
            print item.body

class HTMLDestination:
    """
    将所有新闻项目格式化为HTM的目标类
    """
    def __init__(self,filename):
        self.filename = filename

    def receiveItems(self,items):
        out = open(self.filename,'w')
        print >> out,"""
            <html>
                <head>
                    <title>Today's News</title>
                </head>
                <body>
                    <h1>Today's News</h1>
        """

        print >> out,'<ul>'
        id=0
        for item in items:
            id+=1
            print >>out,'<li ><a href="#%i">%s</a></li>'%(id,item.title)
        print >> out,'</ul>'

        id=0
        for item in items:
            id+=1
            print >> out,'<h2><a name="%i">%s</a></h2>'%(id,item.title)
            print >> out,'<pre>%s</pre>' %item.body

        print >> out,"""
            </body>
            </html>
        """

def runDefaultSetup():
    """
    来源跟目标默认
    :return:
    """
    agent = NewsAgent()
    bbc_url = 'http://news.bbc.co.uk/text_only.stm'
    bbc_title = r'(?s)a href="[^"]*">\s*<b>\s*(.*?)\s*</b>'
    bbc_body = r'(?s)</a>\s*<br/>\s*(.*?)\s<'
    bbc = SimpleWebSource(bbc_url,bbc_title,bbc_body)
    agent.addSource(bbc)
    #从comp.lang.python.annouce获取新闻的NNTPSource

    clpa_server = 'news.aioe.org'
    clpa_group = 'comp.lang.python'
    clpa_window = 1
    clpa_source = NNTPSource(clpa_server,clpa_group,clpa_window)
    agent.addSource(clpa_source)

    agent.addDestination(PlainDestination())
    agent.addDestination(HTMLDestination("news.html"))

    #发布新闻
    agent.distribute()

if __name__=='__main__':
    runDefaultSetup()












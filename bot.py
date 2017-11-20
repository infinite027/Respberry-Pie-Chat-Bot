#-*- coding=utf-8 -*-
import itchat
import random
import urllib.request as url
import re
import json
import pprint
from snownlp import SnowNLP as snow

apiId = '5632757478a5a77d61b77d9534027468'
commonCity = {
"surrey":6159905,
"white rock":6180961,
"richmond":6122085
}



responses=[]
restricts = []

@itchat.msg_register(itchat.content.TEXT)
def mainLoop(msg):
    reply = ''
    try:
        print(msg['Text'])
    except(UnicodeEncodeError):
        return "不支持unicode表情哦"
    text = msg['Text'].lower()

    weather = r'天气 \w*'
    match = re.findall(weather,text)
    if match:
        match = match[0][3::]
        if match in commonCity:
            code=commonCity[match]
            result = getWeatherByCode(apiId,code)
        else:
            result = getWeather(apiId,match)
        reply=processWeather(result)
    else:
        reply=chat(text)
    return reply

def chat(text):
    reply = ''
    possible = []
    if 'ar716' in text:
        restricts.append(text[6:])
        file = open("restricts.txt",'a')
        file.write('\n'+text[5:])
        file.close()
    tag = sentenceProcess(text)
    for response in responses:
        if tag in response.getTag():
            possible.append(response.getText())
    randomN = random.randint(0,len(possible)-1)
    reply = possible[randomN]
    for restrict in restricts:
        if restrict in text:
            reply = "拒绝回答"
    return reply


def sentenceProcess(sentence):
    s = snow(sentence)
    returnV = False
    if s.sentiments<0.4:
        returnV = 'B'
    elif s.sentiments>0.8:
        returnV = 'G'
    else:
        returnV = 'N'
    return returnV

class response():
    def __init__(self,text,tags):
        self.text=text
        self.tags=tags
    def getText(self):
        return self.text
    def getTag(self):
        return self.tags

def loadReplies():
    with open("replies.txt") as file:
        li = [line.rstrip('\n') for line in file]
        file.close()
    li = [line.rstrip(' ') for line in li]
    for line in li:
        if line and line!='\n':
            temp = line.split('/')
            res = temp[0]
            tags = temp[1].split('*')
            newResponse = response(res,tags)
            responses.append(newResponse)

def loadRestrictions():
    with open("restricts.txt") as file:
        restricts = file.readlines()
        file.close()


@itchat.msg_register(itchat.content.PICTURE)
def reply_to_picture(msg):
    return "你指望我一个机器人看懂图片吗"

def getWeatherByCode(apiId,code):
    web = 'http://api.openweathermap.org/data/2.5/weather?id='+str(code)
    content =url.urlopen(web).read().decode('utf-8')
    return str(content)

def getWeather(apiId,city):
    web = 'http://api.openweathermap.org/data/2.5/weather?q='+city+'&APPID='+apiId
    content =url.urlopen(web).read().decode('utf-8')
    return str(content)

def processWeather(text):
    reply=''
    main=r'("main":")(\w*)'
    description=r'("description":")(\w+)'
    main=re.search(main,text)
    description=re.search(description,text)
    print(description.groups())
    reply+=description.group(2)+' '+main.group(2)+"\n"
    temp_max=r'temp_max":(\d*.?\d*)'
    temp_min=r'temp_min":(\d*.?\d*)'
    temp_max=re.search(temp_max,text)
    temp_min=re.search(temp_min,text)
    reply+="最高温度："+str(float(temp_max.group(1))-273.15)+"最低温度："+str(float(temp_min.group(1))-273.15)+"\n"
    wind=r'wind":{"speed":(\d*.?\d*),"deg":(\d*.?\d*)'
    wind=re.search(wind,text)
    reply+="风力："+wind.group(1)+"风向："+wind.group(2)+"\n"
    return reply

if __name__ == '__main__':
    loadReplies()
    loadRestrictions()
    itchat.auto_login(hotReload=True)
    itchat.run()
    mainLoop()

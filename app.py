from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *


#======未來規劃會呼叫的檔案=====
#from message import *
#from new import *
#from Function import *
#======這裡是呼叫的檔案內容=====

#======python函數庫==========
#import tempfile
import datetime
#import time
import requests
from bs4 import BeautifulSoup
import re
import random
import pandas as pd
#======python的函數庫==========

app = Flask(__name__)
# Channel Access Token
line_bot_api = LineBotApi('raFMu2pn970CUDi5zSJ3C+mIHJ4EqR53/+skpyNoD8s/4LLv9FBnOoyenzaNw7QdF82+cXMfubCOKh9SI+enBj2YaK7ZyI+P6SJBwMiNsAzQcM+LfZpP+alLpOoglouX2xX0TniEuBjBQ1k5RaRJXgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('332208a8567bada72f985b63a46d9b06')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'



def ptt(bd):
    web='https://www.ptt.cc/bbs/'+bd+'/index.html'
    cookies = {'over18': '1'}
    apple = requests.get(web,cookies=cookies)
    pineapple = BeautifulSoup(apple.text,'html.parser')
    last = pineapple.select('div.btn-group-paging a')
    last_web = 'https://www.ptt.cc'+last[1]['href']
    apple = requests.get(last_web,cookies=cookies)
    pineapple = BeautifulSoup(apple.text,'html.parser')
    article = pineapple.select('div.title a')
    random.shuffle(article)
    re_imgur = re.compile('http[s]?://i.imgur.com/\w+\.(?:jpg)')
    for tit in article:
        apple = requests.get('https://www.ptt.cc'+tit['href'],cookies=cookies)
        images = re_imgur.findall(apple.text)
        if len(images)!=0:
            break
    num=random.randint(0,len(images)-1)
    return images[num]




# 處理user傳送的text訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    dirty_words = ['幹', '操']
    functions = ['功能']
    author = ['作者']
    teaches = ['教學']
    pttbdpics = ['正', '表特']
    cats = ['貓貓']
    movies = ['電影']
    joke_words = ['厭世']
    msg = event.message.text
    msg_arr = []
    #msg == event.message.text == user傳來的文字訊息
    if msg in dirty_words:
        message = TextSendMessage(text = msg + "...不要罵髒話啊！")
        line_bot_api.reply_message(event.reply_token, message)
    
    elif msg in pttbdpics:
        a = ptt("beauty")
        #print (a)
        message = ImageSendMessage(original_content_url = a, preview_image_url = a)
        line_bot_api.reply_message(event.reply_token, message)

    elif msg in joke_words:
        df = pd.read_csv('joke.csv')
        message = TextSendMessage(text=df['joke'][random.randint(0,len(df)-1)])
        line_bot_api.reply_message(event.reply_token, message)
    
    elif msg in cats:
        a = ptt("cat")
        #print(a)
        message = ImageSendMessage(original_content_url = a, preview_image_url = a)
        line_bot_api.reply_message(event.reply_token, message)

    elif (msg == '最新新聞'):
        html = requests.get('https://www.setn.com/ViewAll.aspx').text
        soup  = BeautifulSoup(html,'html.parser')
        newList = soup.find("div",class_="row NewsList")
        newList = newList.find_all("div", class_="col-sm-12 newsItems", limit=3)
        for i in newList:
            div = i.find("div")
            h3 = div.find("h3")
            a = h3.find("a")
            if ('https' in a.get('href')):
                msg_arr.append(TextSendMessage(a.get('href')))
            else :
                msg_arr.append(TextSendMessage("https://www.setn.com/" + a.get('href')))
        line_bot_api.reply_message(event.reply_token, msg_arr)


    elif msg in author:
        message = TextSendMessage(text = "真拿你沒辦法～\nhttps://www.instagram.com/cwei_11/?hl=zh-tw")
        line_bot_api.reply_message(event.reply_token, message)

    elif msg in functions:
        rtext = f"""--- 指令教學 ---\n
        - 表特\n  > 今天我...想奶奶了\n
        - 厭世\n  > 來點負能量\n
        - 貓貓\n  > 需要療癒？來點貓貓圖\n
        - 最新新聞\n  >小時不讀書，長大當記者\n
        - 電影評價（建置中）\n  > 給你目前院線片的評價\n
        - 星座運勢（建置中）\n  > 運氣不好不要怪星座\n
        - 陪機器人聊天（建置中）\n  > 機器學習（AI語意識別訓練模組）\n
        - 作者\n  > 看誰這麼無聊？作者資訊\n
        - 教學\n  > ...再教一次"""
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=rtext))

    elif msg in teaches:
        message = TextSendMessage(text = msg + "往上滑啊...")
        line_bot_api.reply_message(event.reply_token, message)

    else:
        message = TextSendMessage(text="您所輸入的「" + msg + "」，目前沒有設定功能唷！")
        line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
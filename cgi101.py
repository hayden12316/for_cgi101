# 載入LineBot所需要的套件
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import pyimgur
from pathlib import Path

IMGUR_CLIENT_ID = '52a24284b01c394'
# 連接資料庫， 帶進自己的資訊
conn = pymysql.connect(host = 'localhost',
                                    database='project1',
                                    user='root',
                                    password='1234567890')


sql = """
SELECT d.date, d.count, w.`Temperature(°C)`
FROM mooga_weather w JOIN (SELECT DATE(odatetime) date, count(*) count FROM mooga_orderitems GROUP BY DATE(odatetime) order by date) d 
ON d.date=w.date;"""

cur = conn.cursor()
cur.execute(sql)

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('b+sTKdho12m4+yfB4tv2/2E7Qpetf3qgOPi0cOpwwe+vQeXE3zs0K+6VKlcu0C6HkmwVchvXubrxjqJk0nRkd4n10bhs1ZQ4lG+i2YpGOnAGaIAREzxeAQf71iQELK2FnwhlgnU+0gUHdDIvhZYpzAdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('203521a641695c4d7110debaf7b1ecb2')

line_bot_api.push_message('U93285018abb1284972b72cd643b1ce41', TextSendMessage(text='你可以開始了'))


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
def data_chart(IMGUR_CLIENT):
    fields = [field_md[0] for field_md in cur.description]
    # zip column names and rows
    result = [dict(zip(fields, row)) for row in cur.fetchall()]
    df = pd.DataFrame(result)

    # 畫圖
    fig, ax = plt.subplots()
    ax.plot(df['date'], df['count'], color="red")

    # set x-axis label
    ax.set_xlabel("date", fontsize=14)
    # set y-axis label
    ax.set_ylabel("count",
                  color="red",
                  fontsize=14)
    ax2 = ax.twinx()
    # make a plot with different y-axis using second axis object
    ax2.plot(df['date'], df['Temperature(°C)'], color='b')
    ax2.set_ylabel("temp", color="blue", fontsize=14)
    # plt.show()

    # 儲存圖檔
    fig.savefig('氣溫及日常業績.jpg',
                format='jpeg',
                dpi=100,
                bbox_inches='tight')
    PATH = "氣溫及日常業績.jpg"

    im = pyimgur.Imgur(IMGUR_CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title=" candlestick chart")
    return uploaded_image.link

# 訊息傳遞區塊
##### 基本上程式編輯都在這個function #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "@報表":
        content = data_chart(IMGUR_CLIENT_ID)
        message = ImageSendMessage(original_content_url=content, preview_image_url=content)
        line_bot_api.reply_message(event.reply_token, message)
        # filePath = Path
        # filePath.unlink()

# 主程式
import os

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0",port=5002)
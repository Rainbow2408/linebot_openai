from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 1. 增加計數功能：初始化全域變數
msg_count = 0

# 2. 設定 ChatGPT 的個性
# 你可以在這裡修改 content 的內容，例如：「你是一個幽默的助手」、「你是一個嚴格的英文老師」
AI_PERSONALITY = "你是一個非常親切、愛用貼圖且說話幽默的助理。"

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global msg_count  # 聲明使用全域變數
    text1=event.message.text
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "system", "content": AI_PERSONALITY}, # 設定個性
            {"role": "user", "content": text1}
        ],
        model="gpt-5-nano",
        temperature = 1,
    )
    try:
        ret = response['choices'][0]['message']['content'].strip()
        # 成功獲取回覆後，計數器加 1
        msg_count += 1
        # 在回覆訊息後面附上次數資訊（選用）
        final_ret = f"{ret}\n\n(這是 OpenAI 今日回覆的第 {msg_count} 則訊息)"
    except:
        final_ret = '發生錯誤！'
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=final_ret))

if __name__ == '__main__':
    app.run()

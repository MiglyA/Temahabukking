import json
import concurrent.futures
import os
import sys
from argparse import ArgumentParser

from io import BytesIO

from flask import Flask, request, abort
import requests
from linebot import (
    LineBotApi, WebhookHandler, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, ImageMessage, StickerMessage, AudioMessage,
    PostbackEvent,
)

msgs = []
image = []
audio = []
sticker = []
postback = []

#################handler##########
# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

channel_access_token = 'DvNsKeKTNGDsPDAHmEdzgifwYLtPdg1BV1+YAvz0a3TQmP7LCXbaZF6up4XHpR1Ye8XMItPbX8HB5zsuQLKe5m0YHWlNlp6EAZ73xJCoXZLyarr4HLikG2ZAobqAyn0Ay3ObOoIKHGgbCCL5eAwQUwdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(
    'DvNsKeKTNGDsPDAHmEdzgifwYLtPdg1BV1+YAvz0a3TQmP7LCXbaZF6up4XHpR1Ye8XMItPbX8HB5zsuQLKe5m0YHWlNlp6EAZ73xJCoXZLyarr4HLikG2ZAobqAyn0Ay3ObOoIKHGgbCCL5eAwQUwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('1a6c43c73240a4a03e5754e1f7959704')
parser = WebhookParser('1a6c43c73240a4a03e5754e1f7959704')

app = Flask(__name__)


###################################

@app.route("/callback", methods=['POST'])
def callback():
    global postback, msgs, image, sticker, audio
    id = 0
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    if 'userId' in body:
        id = json.loads(body)["events"][0]["source"]["userId"]

    if 'groupId' in body:
        id = json.loads(body)["events"][0]["source"]["groupId"]

    for event in events:
        if isinstance(event, PostbackEvent):
            postback.append(event.postback.data)
            print(event.postback.data)
        if not isinstance(event, MessageEvent):
            continue
        if isinstance(event.message, TextMessage):
            msgs.append([id, event.message.text])
        if isinstance(event.message, ImageMessage):
            image.append([id, event.message.id])
        if isinstance(event.message, StickerMessage):
            sticker.append([id, event.message.id])
        if isinstance(event.message, AudioMessage):
            audio.append([id, event.message.id])

    print(len(postback))
    print(len(msgs))
    print(len(image))
    print(len(sticker))
    print(len(audio))

    return 'OK'


#####################################################

class LineApp:

    def __init__(self):
        # スレッド起動
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        executor.submit(self.__line_init__)

    def __line_init__(self):
        arg_parser = ArgumentParser(
            usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
        )
        arg_parser.add_argument('-p', '--port', default=8000, help='port')
        arg_parser.add_argument('-d', '--debug', default=False, help='debug')
        options = arg_parser.parse_args()

        app.run(debug=options.debug, port=options.port)

    def push_msgs(self, id, str):
        if not id == '':
            line_bot_api.push_message(
                id,
                TextSendMessage(str)
            )
            return

        else:
            print("not addr")

    def push_json(self, data: json):
        header = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {" + channel_access_token + "}"
        }
        print(requests.post('https://api.line.me/v2/bot/message/push', headers=header, data=json.dumps(data)))

    def push_img(self, id, url):
        if not id == '':
            line_bot_api.push_message(
                id,
                ImageSendMessage(
                    original_content_url=url,
                    preview_image_url=url
                )
            )
            return

        else:
            print("not addr")

    def get_msgs(self):
        global msgs
        return msgs

    def get_postback(self):
        global postback
        return postback

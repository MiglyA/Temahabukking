import json
import concurrent.futures
import os
import sys
from argparse import ArgumentParser

from io import BytesIO

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent,
    TextMessage, ImageMessage, AudioMessage
)

msgs = []

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

line_bot_api = LineBotApi(
    '/07Z+OlPxitHyS23cLdU+jdE7XOhZJ8ABueC4ctVy/chTD3sxn3qUTRN66UoUH/weuD3MkL7twkVGs9Ik3tjAcD+NHBXU7t9HcRi+ebCcwuJq+RAG77Ad3P7WplaOgCx8qovCfUON3LiV5OZndRLtgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('4ceb98627c0c99db6aa38531c54c3b02')
parser = WebhookParser('4ceb98627c0c99db6aa38531c54c3b02')

app = Flask(__name__)


###################################

@app.route("/callback", methods=['POST'])
def callback():
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

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        msgs.append([id, event.message.text])

    return 'OK'


# 画像、音声メッセージの場合
@handler.add(MessageEvent, message=(ImageMessage, AudioMessage))
def handle_image_audio_message(event):
    content = line_bot_api.get_message_content(event.message.id)
    with open('file', 'w') as f:
        for c in content.iter_content():
            f.write(c)


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
                # TextSendMessage(str)
            )
            return

        else:
            print("not addr")

    def push_img(self, id, url):
        if not id == '':
            line_bot_api.push_message(
                id,
                # ImageSendMessage(
                #    original_content_url=url,
                #    preview_image_url=url
                # )
            )
            return

        else:
            print("not addr")

    def get_msgs(self):
        return msgs

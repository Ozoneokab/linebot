import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.webhooks import MessageEvent, TextMessageContent, MemberJoinedEvent
from linebot.v3.exceptions import InvalidSignatureError
from models.database import init_db
from handlers.message import handle_message
from handlers.war import handle_war_event, is_war_mode
from services.blacklist import check_and_alert

app = Flask(__name__)
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# os.makedirs("/tmp")
init_db()

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try: handler.handle(body, signature)
    except InvalidSignatureError: abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def on_message(event):
    group_id = getattr(event.source, "group_id", None)
    user_id = event.source.user_id
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if group_id and is_war_mode(group_id):
            handled, _ = handle_war_event(group_id, user_id, line_bot_api)
            if handled: return
        handle_message(event, line_bot_api)

@handler.add(MemberJoinedEvent)
def on_join(event):
    group_id = event.source.group_id
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        for m in event.joined.members: check_and_alert(m.user_id, group_id, line_bot_api)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

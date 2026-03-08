import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, PushMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent, TextMessageContent,
    ImageMessageContent, StickerMessageContent,
    MemberJoinedEvent
)
from linebot.v3.exceptions import InvalidSignatureError
from models.database import init_db
from handlers.message import handle_message
from handlers.war import handle_war_event, is_war_mode
from services.blacklist import check_and_alert

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN", "")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET", "")

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# ── เริ่มต้นระบบ ───────────────────────────────
with app.app_context():
    init_db()
    print("✅ LineGuard Bot started successfully.")

# ── Health Check ──────────────────────────────
@app.route("/")
def health_check():
    return {"status": "LineGuard Bot is running 🛡️"}

# ── Webhook รับข้อมูลจาก LINE ─────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# ── จัดการข้อความ Text ────────────────────────
@handler.add(MessageEvent, message=TextMessageContent)
def on_text_message(event):
    if not hasattr(event.source, "group_id"):
        return

    group_id = event.source.group_id
    user_id = event.source.user_id

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if is_war_mode(group_id):
            handled, reason = handle_war_event(
                group_id, user_id, line_bot_api
            )
            if handled:
                return

        handle_message(event, line_bot_api)

# ── จัดการรูปภาพ ──────────────────────────────
@handler.add(MessageEvent, message=ImageMessageContent)
def on_image_message(event):
    if not hasattr(event.source, "group_id"):
        return
    with ApiClient(configuration) as api_client:
        handle_message(event, MessagingApi(api_client))

# ── จัดการ Sticker ────────────────────────────
@handler.add(MessageEvent, message=StickerMessageContent)
def on_sticker_message(event):
    if not hasattr(event.source, "group_id"):
        return
    with ApiClient(configuration) as api_client:
        handle_message(event, MessagingApi(api_client))

# ── ตรวจสอบสมาชิกใหม่ ─────────────────────────
@handler.add(MemberJoinedEvent)
def on_member_joined(event):
    group_id = event.source.group_id
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        for member in event.joined.members:
            check_and_alert(member.user_id, group_id, line_bot_api)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)

from services.spam_detector import analyze_message
from services.rate_limiter import is_muted, mute_user
from services.blacklist import ban_user
from models.database import add_warn, log_violation, get_role
from config import WARN_BEFORE_KICK, SUPER_ADMINS

def handle_message(event, line_bot_api):
    user_id = event.source.user_id
    group_id = getattr(event.source, "group_id", None)
    msg_type = event.message.type
    text = event.message.text if msg_type == "text" else ""

    role = get_role(user_id)
    if user_id in SUPER_ADMINS: role = "super_admin"

    if role in ["super_admin", "admin"]:
        if text.startswith("/"): handle_admin_command(text, user_id, group_id, line_bot_api)
        return

    if is_muted(user_id): return

    is_spam, reason, severity = analyze_message(user_id, text, msg_type)
    if is_spam and group_id:
        take_action(user_id, group_id, reason, severity, line_bot_api)
        log_violation(user_id, group_id, "spam", reason, severity)

def take_action(user_id, group_id, reason, severity, line_bot_api):
    try:
        if severity == "warn":
            warn_count = add_warn(user_id)
            if warn_count >= WARN_BEFORE_KICK:
                line_bot_api.kick_group_member(group_id, user_id)
            else:
                mute_user(user_id, 60)
                line_bot_api.push_message(group_id, messages=[{"type": "text", "text": f"⚠️ เตือน {warn_count}/{WARN_BEFORE_KICK}\nเหตุผล: {reason}"}])
        elif severity in ["kick", "ban"]:
            line_bot_api.kick_group_member(group_id, user_id)
            if severity == "ban": ban_user(user_id, reason, group_id, "system")
    except: pass

def handle_admin_command(text, user_id, group_id, line_bot_api):
    parts = text.strip().split()
    cmd = parts[0].lower()
    if cmd == "/help":
        line_bot_api.push_message(group_id or user_id, messages=[{"type": "text", "text": "📋 /warn, /kick, /ban, /unban, /warmode on/off"}])
    # ... เพิ่มคำสั่งอื่นๆ ได้ที่นี่

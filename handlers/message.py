from linebot.models import TextSendMessage
from services.spam_detector import analyze_message
from services.rate_limiter import is_muted, mute_user, get_mute_remaining
from services.blacklist import ban_user
from models.database import add_warn, log_violation, get_role
from config import WARN_BEFORE_KICK, SUPER_ADMINS, ADMINS, MODERATORS

def handle_message(event, line_bot_api):
    """
    จุดรับข้อความหลัก
    ทุกข้อความที่เข้ามาในกลุ่มจะผ่านฟังก์ชันนี้
    """
    user_id = event.source.user_id
    group_id = event.source.group_id
    
    # ดึงข้อมูลข้อความ
    msg_type = event.message.type
    text = event.message.text if msg_type == "text" else ""
    
    # ── แอดมินไม่โดนตรวจสอบ ──────────────────────
    role = get_role(user_id)
    if role in ["super_admin", "admin"]:
        handle_admin_command(text, user_id, group_id, line_bot_api)
        return
    
    # ── ตรวจสอบ mute ──────────────────────────────
    if is_muted(user_id):
        remaining = get_mute_remaining(user_id)
        try:
            line_bot_api.delete_message(event.message.id)
        except:
            pass
        return
    
    # ── วิเคราะห์ข้อความ ──────────────────────────
    is_spam, reason, severity = analyze_message(user_id, text, msg_type)
    
    if is_spam:
        take_action(user_id, group_id, reason, severity, line_bot_api)
        log_violation(user_id, group_id, "spam", reason, severity)

def take_action(user_id, group_id, reason, severity, line_bot_api):
    """
    ดำเนินการตามความรุนแรงของการละเมิด
    warn → mute → kick → ban
    """
    try:
        if severity == "warn":
            warn_count = add_warn(user_id)
            
            if warn_count >= WARN_BEFORE_KICK:
                # kick เมื่อ warn ครบ
                line_bot_api.kick_group_member(group_id, user_id)
                line_bot_api.push_message(group_id, TextSendMessage(
                    text=f"🚫 Kicked สมาชิกออกจากกลุ่มแล้วครับ\nเหตุผล: {reason}\n(warn ครบ {WARN_BEFORE_KICK} ครั้ง)"
                ))
            else:
                mute_user(user_id, 60)
                line_bot_api.push_message(group_id, TextSendMessage(
                    text=f"⚠️ คำเตือนครั้งที่ {warn_count}/{WARN_BEFORE_KICK}\n"
                         f"เหตุผล: {reason}\n"
                         f"ถูก mute 1 นาทีครับ"
                ))

        elif severity == "kick":
            line_bot_api.kick_group_member(group_id, user_id)
            line_bot_api.push_message(group_id, TextSendMessage(
                text=f"🚫 Kicked สมาชิกออกจากกลุ่มแล้วครับ\nเหตุผล: {reason}"
            ))

        elif severity == "ban":
            line_bot_api.kick_group_member(group_id, user_id)
            ban_user(user_id, reason, group_id, "system")
            line_bot_api.push_message(group_id, TextSendMessage(
                text=f"🔴 Banned และเพิ่มเข้า Blacklist แล้วครับ\nเหตุผล: {reason}"
            ))

    except Exception as e:
        print(f"Action error: {e}")

def handle_admin_command(text, user_id, group_id, line_bot_api):
    """
    จัดการคำสั่งแอดมิน
    พิมพ์ /help เพื่อดูคำสั่งทั้งหมด
    """
    if not text.startswith("/"):
        return
    
    parts = text.strip().split()
    cmd = parts[0].lower()
    
    commands = {
        "/help": show_help,
        "/warn": cmd_warn,
        "/kick": cmd_kick,
        "/ban": cmd_ban,
        "/unban": cmd_unban,
        "/warmode": cmd_warmode,
    }
    
    if cmd in commands:
        commands[cmd](parts, user_id, group_id, line_bot_api)

def show_help(parts, user_id, group_id, line_bot_api):
    help_text = (
        "📋 คำสั่งแอดมิน\n"
        "/warn @user — เตือนสมาชิก\n"
        "/kick @user — kick สมาชิก\n"
        "/ban @user [เหตุผล] — ban และ blacklist\n"
        "/unban [userID] — ยกเลิก blacklist\n"
        "/warmode on/off — เปิด/ปิด War Mode"
    )
    line_bot_api.push_message(group_id, TextSendMessage(text=help_text))

def cmd_warn(parts, user_id, group_id, line_bot_api):
    if len(parts) < 2:
        return
    target = parts[1].replace("@", "")
    warn_count = add_warn(target)
    line_bot_api.push_message(group_id, TextSendMessage(
        text=f"⚠️ Admin ออก warn ให้ {target} แล้วครับ (ครั้งที่ {warn_count})"
    ))

def cmd_kick(parts, user_id, group_id, line_bot_api):
    if len(parts) < 2:
        return
    target = parts[1].replace("@", "")
    line_bot_api.kick_group_member(group_id, target)
    line_bot_api.push_message(group_id, TextSendMessage(
        text=f"🚫 Kicked {target} ออกจากกลุ่มแล้วครับ"
    ))

def cmd_ban(parts, user_id, group_id, line_bot_api):
    if len(parts) < 2:
        return
    target = parts[1].replace("@", "")
    reason = " ".join(parts[2:]) if len(parts) > 2 else "ban โดย admin"
    ban_user(target, reason, group_id, user_id)
    line_bot_api.kick_group_member(group_id, target)
    line_bot_api.push_message(group_id, TextSendMessage(
        text=f"🔴 Banned {target} แล้วครับ\nเหตุผล: {reason}"
    ))

def cmd_unban(parts, user_id, group_id, line_bot_api):
    if len(parts) < 2:
        return
    target = parts[1]
    from services.blacklist import pardon_user
    pardon_user(target)
    line_bot_api.push_message(group_id, TextSendMessage(
        text=f"✅ ยกเลิก blacklist {target} แล้วครับ"
    ))

def cmd_warmode(parts, user_id, group_id, line_bot_api):
    if len(parts) < 2:
        return
    from handlers.war import activate_war_mode, deactivate_war_mode
    if parts[1].lower() == "on":
        activate_war_mode(group_id)
        line_bot_api.push_message(group_id, TextSendMessage(
            text="🔴 War Mode เปิดแล้วครับ ระบบป้องกันเต็มรูปแบบกำลังทำงาน"
        ))
    else:
        deactivate_war_mode(group_id)
        line_bot_api.push_message(group_id, TextSendMessage(
            text="🟢 War Mode ปิดแล้วครับ กลับสู่โหมดปกติ"
        ))

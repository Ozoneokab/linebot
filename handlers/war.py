from collections import defaultdict
from services.spam_detector import detect_war_bot
war_mode_active = defaultdict(bool)
def activate_war_mode(group_id): war_mode_active[group_id] = True
def deactivate_war_mode(group_id): war_mode_active[group_id] = False
def is_war_mode(group_id): return war_mode_active[group_id]
def handle_war_event(group_id, user_id, line_bot_api):
    is_bot, reason = detect_war_bot(user_id)
    if is_bot:
        activate_war_mode(group_id)
        try:
            line_bot_api.push_message(group_id, messages=[{"type": "text", "text": "⚠️ WAR MODE ⚠️\nดีดบอทออกครับ"}])
            line_bot_api.kick_group_member(group_id, user_id)
            return True, reason
        except: pass
    return False, None

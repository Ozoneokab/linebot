from models.database import add_to_blacklist, is_blacklisted, remove_from_blacklist, log_violation
def check_and_alert(user_id, group_id, line_bot_api):
    if is_blacklisted(user_id):
        try:
            line_bot_api.push_message(group_id, messages=[{"type": "text", "text": f"⚠️ แจ้งเตือน Admin ⚠️\nพบ Blacklist: {user_id}"}])
            log_violation(user_id, group_id, "blacklist_join", "Blacklist เข้ากลุ่ม", "alerted")
            return True
        except: pass
    return False
def ban_user(user_id, reason, group_id, admin_id):
    add_to_blacklist(user_id, reason)
    log_violation(user_id, group_id, "banned", reason, f"by_{admin_id}")

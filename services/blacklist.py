from models.database import add_to_blacklist, is_blacklisted, remove_from_blacklist, log_violation

def check_and_alert(user_id, group_id, line_bot_api):
    if is_blacklisted(user_id):
        try:
            line_bot_api.push_message(group_id, messages={"type": "text", "text": f"⚠️ แจ้งเตือน Admin ⚠️\nตรวจพบสมาชิก Blacklist เข้ากลุ่ม\nUser ID: {user_id}"})
            log_violation(user_id, group_id, "blacklist_join", "สมาชิก blacklist เข้ากลุ่ม", "alerted_admin")
            return True
        except Exception as e:
            print(f"Error alerting admin: {e}")
    return False

def ban_user(user_id, reason, group_id, admin_id):
    add_to_blacklist(user_id, reason)
    log_violation(user_id, group_id, "banned", reason, f"banned_by_{admin_id}")

def pardon_user(user_id):
    remove_from_blacklist(user_id)

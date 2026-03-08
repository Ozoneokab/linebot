import time
from collections import defaultdict

# เก็บสถานะ mute ของแต่ละ user
muted_users = {}
# เก็บเวลาที่ถูก mute
mute_until = defaultdict(float)

def is_muted(user_id):
    """ตรวจสอบว่า user ถูก mute อยู่หรือไม่"""
    if user_id in mute_until:
        if time.time() < mute_until[user_id]:
            return True
        else:
            del mute_until[user_id]
    return False

def mute_user(user_id, duration_seconds=300):
    """mute user ชั่วคราว (default 5 นาที)"""
    mute_until[user_id] = time.time() + duration_seconds

def unmute_user(user_id):
    """ยกเลิก mute"""
    if user_id in mute_until:
        del mute_until[user_id]

def get_mute_remaining(user_id):
    """เวลาที่เหลือของการ mute (วินาที)"""
    if user_id in mute_until:
        remaining = mute_until[user_id] - time.time()
        return max(0, int(remaining))
    return 0
กด CTRL + X → Y → Enter ครับ
จากนั้นสร้างไฟล์ที่สองครับ
nano services/blacklist.py
from models.database import (
    add_to_blacklist,
    is_blacklisted,
    remove_from_blacklist,
    log_violation
)

def check_and_alert(user_id, group_id, line_bot_api):
    """
    ตรวจสอบเมื่อมีสมาชิกเข้ากลุ่ม
    ถ้าอยู่ใน blacklist ให้แจ้งเตือน admin ทันที
    """
    if is_blacklisted(user_id):
        try:
            # แจ้งเตือนในกลุ่ม
            line_bot_api.push_message(
                group_id,
                messages={
                    "type": "text",
                    "text": (
                        f"⚠️ แจ้งเตือน Admin ⚠️\n"
                        f"ตรวจพบสมาชิกที่อยู่ใน Blacklist เพิ่งเข้ากลุ่ม\n"
                        f"User ID: {user_id}\n"
                        f"กรุณาตรวจสอบและดำเนินการครับ"
                    )
                }
            )
            log_violation(user_id, group_id, "blacklist_join", 
                         "สมาชิก blacklist เข้ากลุ่ม", "alerted_admin")
            return True
        except Exception as e:
            print(f"Error alerting admin: {e}")
    return False

def ban_user(user_id, reason, group_id, admin_id):
    """เพิ่ม user เข้า blacklist พร้อมบันทึกเหตุผล"""
    add_to_blacklist(user_id, reason)
    log_violation(user_id, group_id, "banned", reason, f"banned_by_{admin_id}")

def pardon_user(user_id):
    """赦免 user ออกจาก blacklist"""
    remove_from_blacklist(user_id)

import time
from collections import defaultdict
from services.spam_detector import detect_war_bot

# เก็บสถานะ War Mode ของแต่ละกลุ่ม
war_mode_active = defaultdict(bool)
war_start_time = defaultdict(float)
enemy_bot_tracker = defaultdict(list)

def activate_war_mode(group_id):
    """เปิด War Mode สำหรับกลุ่มนี้"""
    war_mode_active[group_id] = True
    war_start_time[group_id] = time.time()
    print(f"War Mode activated for group: {group_id}")

def deactivate_war_mode(group_id):
    """ปิด War Mode"""
    war_mode_active[group_id] = False
    enemy_bot_tracker[group_id] = []

def is_war_mode(group_id):
    """ตรวจสอบว่ากลุ่มนี้อยู่ใน War Mode หรือไม่"""
    return war_mode_active[group_id]

def track_enemy(group_id, user_id):
    """
    ติดตามพฤติกรรมบอทศัตรู
    ถ้าส่งข้อความเกิน threshold ใน 5 วินาที
    ถือว่าเป็น enemy bot
    """
    now = time.time()
    enemy_bot_tracker[group_id] = [
        (t, uid) for t, uid in enemy_bot_tracker[group_id]
        if now - t < 5
    ]
    enemy_bot_tracker[group_id].append((now, user_id))
    
    # นับข้อความจาก user นี้ใน 5 วินาที
    count = sum(1 for _, uid in enemy_bot_tracker[group_id] if uid == user_id)
    return count

def get_war_counter_message(count):
    """
    สร้างข้อความตอบโต้บอทศัตรู
    ยิ่งโจมตีมาก ยิ่งตอบโต้แรง
    """
    if count >= 20:
        return (
            "🔴 CRITICAL WAR MODE 🔴\n"
            "ตรวจพบการโจมตีระดับสูงสุด\n"
            "ระบบป้องกันเต็มรูปแบบกำลังทำงาน\n"
            "Admin ได้รับการแจ้งเตือนแล้วครับ"
        )
    elif count >= 10:
        return (
            "⚠️ WAR MODE ACTIVE ⚠️\n"
            "ตรวจพบบอทกำลังโจมตีกลุ่ม\n"
            "กำลังดำเนินการบล็อกอัตโนมัติครับ"
        )
    else:
        return (
            "🛡️ ระบบป้องกันกำลังทำงาน\n"
            "ตรวจพบพฤติกรรมผิดปกติครับ"
        )

def handle_war_event(group_id, user_id, line_bot_api):
    """
    จัดการเหตุการณ์ War ทั้งหมด
    ตรวจจับ ตอบโต้ และ kick อัตโนมัติ
    """
    is_bot, reason = detect_war_bot(user_id)
    
    if is_bot:
        activate_war_mode(group_id)
        count = track_enemy(group_id, user_id)
        counter_msg = get_war_counter_message(count)
        
        try:
            # ส่งข้อความเตือนในกลุ่ม
            line_bot_api.push_message(
                group_id,
                messages={"type": "text", "text": counter_msg}
            )
            
            # kick บอทศัตรูออกจากกลุ่ม
            line_bot_api.kick_group_member(group_id, user_id)
            return True, reason
            
        except Exception as e:
            print(f"War handler error: {e}")
    
    return False, None

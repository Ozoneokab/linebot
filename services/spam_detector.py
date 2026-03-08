import re
import time
from collections import defaultdict
from config import (
    MAX_MESSAGES_PER_10SEC,
    DUPLICATE_MSG_THRESHOLD,
    BANNED_PATTERNS,
    BANNED_WORDS,
    BOT_DETECTION_THRESHOLD
)

# เก็บประวัติข้อความของแต่ละ user ไว้ในหน่วยความจำ
message_history = defaultdict(list)
duplicate_tracker = defaultdict(list)
war_tracker = defaultdict(list)

def check_rate_limit(user_id):
    """ตรวจสอบว่าส่งข้อความถี่เกินไปหรือไม่"""
    now = time.time()
    history = message_history[user_id]
    
    # เก็บเฉพาะข้อความใน 10 วินาทีที่ผ่านมา
    message_history[user_id] = [t for t in history if now - t < 10]
    message_history[user_id].append(now)
    
    if len(message_history[user_id]) > MAX_MESSAGES_PER_10SEC:
        return True, f"ส่งข้อความเร็วเกินไป ({len(message_history[user_id])} ข้อความใน 10 วินาที)"
    return False, None

def check_duplicate(user_id, text):
    """ตรวจสอบข้อความซ้ำ"""
    now = time.time()
    history = duplicate_tracker[user_id]
    
    # เก็บเฉพาะข้อความใน 60 วินาทีที่ผ่านมา
    duplicate_tracker[user_id] = [(t, m) for t, m in history if now - t < 60]
    
    # นับข้อความที่ซ้ำกัน
    count = sum(1 for _, m in duplicate_tracker[user_id] if m == text)
    duplicate_tracker[user_id].append((now, text))
    
    if count >= DUPLICATE_MSG_THRESHOLD:
        return True, f"ส่งข้อความซ้ำ {count + 1} ครั้ง"
    return False, None

def check_banned_content(text):
    """ตรวจสอบลิงก์ QR code และเนื้อหาต้องห้าม"""
    # ตรวจ pattern ต้องห้าม
    for pattern in BANNED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True, f"พบเนื้อหาต้องห้าม: {pattern}"
    
    # ตรวจคำต้องห้าม
    text_lower = text.lower()
    for word in BANNED_WORDS:
        if word.lower() in text_lower:
            return True, f"พบคำต้องห้าม: {word}"
    
    return False, None

def check_image_spam(message_type, user_id):
    """ตรวจสอบการส่งรูปภาพหรือ QR code ซ้ำ"""
    if message_type in ["image", "sticker"]:
        now = time.time()
        history = message_history.get(f"img_{user_id}", [])
        history = [t for t in history if now - t < 30]
        history.append(now)
        message_history[f"img_{user_id}"] = history
        
        if len(history) > 3:
            return True, "ส่งรูปภาพหรือ sticker ถี่เกินไป"
    return False, None

def detect_war_bot(user_id):
    """ตรวจสอบว่าเป็นบอทที่กำลัง war หรือไม่"""
    now = time.time()
    war_tracker[user_id] = [t for t in war_tracker[user_id] if now - t < 5]
    war_tracker[user_id].append(now)
    
    if len(war_tracker[user_id]) >= BOT_DETECTION_THRESHOLD:
        return True, f"ตรวจพบพฤติกรรมบอท ({len(war_tracker[user_id])} ข้อความใน 5 วินาที)"
    return False, None

def analyze_message(user_id, text, message_type="text"):
    """
    วิเคราะห์ข้อความทั้งหมด
    คืนค่า: (is_spam, reason, severity)
    severity: 'warn', 'kick', 'ban'
    """
    # ตรวจ war bot ก่อนเลย
    is_war, war_reason = detect_war_bot(user_id)
    if is_war:
        return True, war_reason, "ban"
    
    # ตรวจ rate limit
    is_rate, rate_reason = check_rate_limit(user_id)
    if is_rate:
        return True, rate_reason, "warn"
    
    # ตรวจเนื้อหาต้องห้าม
    if message_type == "text":
        is_banned, banned_reason = check_banned_content(text)
        if is_banned:
            return True, banned_reason, "kick"
        
        is_dup, dup_reason = check_duplicate(user_id, text)
        if is_dup:
            return True, dup_reason, "warn"
    
    # ตรวจรูปภาพ/sticker spam
    is_img, img_reason = check_image_spam(message_type, user_id)
    if is_img:
        return True, img_reason, "warn"
    
    return False, None, None

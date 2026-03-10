import re, time
from collections import defaultdict
from config import MAX_MESSAGES_PER_10SEC, DUPLICATE_MSG_THRESHOLD, BANNED_PATTERNS, BANNED_WORDS, BOT_DETECTION_THRESHOLD
message_history = defaultdict(list)
duplicate_tracker = defaultdict(list)
war_tracker = defaultdict(list)
def check_rate_limit(user_id):
    now = time.time()
    message_history[user_id] = [t for t in message_history[user_id] if now - t < 10]
    message_history[user_id].append(now)
    return (len(message_history[user_id]) > MAX_MESSAGES_PER_10SEC, "ส่งข้อความเร็วเกินไป")
def check_duplicate(user_id, text):
    now = time.time()
    duplicate_tracker[user_id] = [(t, m) for t, m in duplicate_tracker[user_id] if now - t < 60]
    count = sum(1 for _, m in duplicate_tracker[user_id] if m == text)
    duplicate_tracker[user_id].append((now, text))
    return (count >= DUPLICATE_MSG_THRESHOLD, f"ส่งข้อความซ้ำ {count + 1} ครั้ง")
def check_banned_content(text):
    for pattern in BANNED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE): return (True, "พบเนื้อหาต้องห้าม")
    return (False, None)
def detect_war_bot(user_id):
    now = time.time()
    war_tracker[user_id] = [t for t in war_tracker[user_id] if now - t < 5]
    war_tracker[user_id].append(now)
    return (len(war_tracker[user_id]) >= BOT_DETECTION_THRESHOLD, "ตรวจพบพฤติกรรมบอท")
def analyze_message(user_id, text, message_type="text"):
    is_war, war_reason = detect_war_bot(user_id)
    if is_war: return True, war_reason, "ban"
    is_rate, rate_reason = check_rate_limit(user_id)
    if is_rate: return True, rate_reason, "warn"
    if message_type == "text":
        is_banned, banned_reason = check_banned_content(text)
        if is_banned: return True, banned_reason, "kick"
        is_dup, dup_reason = check_duplicate(user_id, text)
        if is_dup: return True, dup_reason, "warn"
    return False, None, None

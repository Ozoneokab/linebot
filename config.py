import os

# ดึงค่าจาก Environment Variables (ที่ตั้งค่าไว้ใน Render)
CHANNEL_ACCESS_TOKEN = os.getenv("k+ssxzPg5ZV6ej3BQmRkngXs65BD0gI9jBe+CdXQP0gGLQk9cQIVBQGYpcB319NTdeP/p6NY+yyFn5S8EGwtIisxn9PQ33FtLwKJrEqiZsAOQiSA6P1vez275YCdbThdi83auI1RaBlV737k0tP48QdB04t89/1O/w1cDnyilFU=", "")
CHANNEL_SECRET = os.getenv("1362d112e4d04c9038ff94cd9154173e", "")

# --- รายชื่อแอดมิน ---
# ให้โอโซนเอา User ID ของตัวเองมาใส่ในเครื่องหมายคำพูดนะครับ
SUPER_ADMINS = ["Ub05c4d3cf85d9149e63eb3e39ca0f76db"] 
ADMINS = []
MODERATORS = []

# --- ตั้งค่าระบบป้องกัน (ส่วนที่ขาดหายไป) ---
MAX_MESSAGES_PER_10SEC = 5      # ส่งข้อความได้ไม่เกิน 5 ครั้งใน 10 วินาที
DUPLICATE_MSG_THRESHOLD = 3     # ส่งข้อความซ้ำเกิน 3 ครั้งจะโดนเตือน
WARN_BEFORE_KICK = 3           # เตือนครบ 3 ครั้งจะโดนเตะ
BOT_DETECTION_THRESHOLD = 10    # ความไวในการตรวจจับบอท
WAR_MODE_ENABLED = True         # เปิดใช้งานโหมดป้องกัน (True = เปิด)

# --- รูปแบบข้อความ/ลิงก์ที่สั่งแบน ---
BANNED_PATTERNS = [
    r"https?://",           # แบนลิงก์ทุกชนิด
    r"line\.me/ti/g/",      # แบนลิงก์เชิญกลุ่ม
]
BANNED_WORDS = ["ฝากร้าน", "โปรโมท"] # เพิ่มคำที่อยากแบนได้ในนี้

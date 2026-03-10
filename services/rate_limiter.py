import time
from collections import defaultdict
mute_until = defaultdict(float)
def is_muted(user_id):
    if user_id in mute_until and time.time() < mute_until[user_id]: return True
    if user_id in mute_until: del mute_until[user_id]
    return False
def mute_user(user_id, duration_seconds=300):
    mute_until[user_id] = time.time() + duration_seconds

import time
from collections import defaultdict

muted_users = {}
mute_until = defaultdict(float)

def is_muted(user_id):
    if user_id in mute_until:
        if time.time() < mute_until[user_id]:
            return True
        else:
            del mute_until[user_id]
    return False

def mute_user(user_id, duration_seconds=300):
    mute_until[user_id] = time.time() + duration_seconds

def unmute_user(user_id):
    if user_id in mute_until:
        del mute_until[user_id]

def get_mute_remaining(user_id):
    if user_id in mute_until:
        remaining = mute_until[user_id] - time.time()
        return max(0, int(remaining))
    return 0

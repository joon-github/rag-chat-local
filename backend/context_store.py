# backend/context_store.py
from collections import defaultdict

context_messages = defaultdict(list)

DEFAULT_SYSTEM_MSG = {
    "role": "system",
    "content": "당신은 문서 기반 질문에 친절하게 답하는 AI입니다."
}

MAX_MESSAGES = 10  # user + assistant 합쳐 최대 10개

def get_context(user_id="default"):
    if not context_messages[user_id]:
        context_messages[user_id].append(DEFAULT_SYSTEM_MSG)
    return context_messages[user_id]

def _trim_context(user_id="default"):
    msgs = context_messages[user_id]
    system_msg = msgs[0]
    # system을 제외한 메시지만 추림
    trimmed = msgs[1:][-MAX_MESSAGES:]
    context_messages[user_id] = [system_msg] + trimmed

def add_user_message(content, user_id="default"):
    get_context(user_id).append({"role": "user", "content": content})
    _trim_context(user_id)

def add_assistant_message(content, user_id="default"):
    get_context(user_id).append({"role": "assistant", "content": content})
    _trim_context(user_id)
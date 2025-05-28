from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from threading import Thread
import time
import threading
import os
import signal

from watcher import start_watching
from extractor import extract_text_from_file
from vector_store import add_to_index
from vector_store import search
from llm import stream_answer
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
load_dotenv()
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app = FastAPI()

last_ping_time = time.time()

@app.get("/ping")
def ping():
    global last_ping_time
    last_ping_time = time.time()
    return {"message": "pong"}

# 종료 감시 스레드
def shutdown_if_idle():
    is_process_running = True
    while True:
        time.sleep(10)
        if time.time() - last_ping_time > 15:  # 15초 이상 ping 없음
            print("❌ 클라이언트 ping 없음. 서버 종료.")
            is_process_running = False
            os.kill(os.getpid(), signal.SIGINT)

threading.Thread(target=shutdown_if_idle, daemon=True).start()

# 폴더 감시 설정
watcher_thread = None

class FolderRequest(BaseModel):
    folder_path: str

@app.post("/watch")
def start_watch(req: FolderRequest):
    global watcher_thread

    def handle_file_created(file_path):
        print(f"[백엔드] 파일 감지됨: {file_path}")
        # 이후 문서 추출과 임베딩 처리 예정
        print(f"[백엔드] 파일 감지됨: {file_path}")
        content = extract_text_from_file(file_path)
        print(f"[추출된 텍스트] {content[:200]}...")  # 너무 길면 앞부분만 출력
        add_to_index(content)

    def run_watcher():
        start_watching(req.folder_path, handle_file_created)
        while True:
            time.sleep(1)

    if watcher_thread is None:
        watcher_thread = Thread(target=run_watcher, daemon=True)
        watcher_thread.start()
        return {"status": "watching", "path": req.folder_path}
    else:
        return {"status": "already_watching"}

@app.get("/search")
def search_docs(q: str):
    results = search(q)
    return {"results": results}

@app.get("/ask")
def ask(q: str):
    docs = search(q)
    context = "\n---\n".join(docs)
    full_prompt = f"""
당신은 친절한 문서 요약 도우미입니다.
다음 문서들을 참고하여 사용자의 질문에 답하십시오.

문서의 출처도 함께 출력해주세요.

문서들:
{context}

질문: {q}
답변:"""

    def event_generator():
        try:
            for chunk in stream_answer(full_prompt):
                if hasattr(chunk.choices[0].delta, "content"):
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"\n[Error] {e}"

    return StreamingResponse(event_generator(), media_type="text/plain")
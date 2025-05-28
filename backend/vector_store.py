# backend/vector_store.py
import os
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer

VECTOR_DIR = "vector_store"
INDEX_PATH = os.path.join(VECTOR_DIR, "index.faiss")
DOCS_PATH = os.path.join(VECTOR_DIR, "doc_store.pkl")

# 모델 불러오기
model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384
index = faiss.IndexFlatL2(dimension)
doc_store = []

# ────────── 초기 로딩 ──────────
def load_index():
    global index, doc_store
    if os.path.exists(INDEX_PATH) and os.path.exists(DOCS_PATH):
        print("🗂 기존 인덱스 로딩 중...")
        index = faiss.read_index(INDEX_PATH)
        with open(DOCS_PATH, "rb") as f:
            doc_store = pickle.load(f)
        print(f"✅ 로딩 완료 - 문서 수: {len(doc_store)}")
    else:
        print("🆕 새 인덱스 시작")

load_index()

# ────────── 인덱싱 함수 ──────────
def add_to_index(text: str):
    if not text.strip():
        return
    embedding = model.encode([text])[0].astype("float32")
    index.add(np.array([embedding]))
    doc_store.append(text)
    print(f"✅ 인덱싱 완료 (총 문서 수: {len(doc_store)})")
    save_index()

# ────────── 검색 함수 ──────────
def search(query: str, top_k=3):
    q_embedding = model.encode([query])[0].astype("float32")
    D, I = index.search(np.array([q_embedding]), top_k)
    return [doc_store[i] for i in I[0] if i < len(doc_store)]

# ────────── 저장 함수 ──────────
def save_index():
    if not os.path.exists(VECTOR_DIR):
        os.makedirs(VECTOR_DIR)
    faiss.write_index(index, INDEX_PATH)
    with open(DOCS_PATH, "wb") as f:
        pickle.dump(doc_store, f)
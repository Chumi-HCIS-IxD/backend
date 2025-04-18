# push_units_1_to_5.py
"""
Unit_1 ~ Unit_5 各寫 10 題到 Firestore
執行：python push_units_1_to_5.py
"""
import firebase_admin
from firebase_admin import credentials, firestore

# ─────────────────── 0. 服務帳戶金鑰路徑 ───────────────────
SERVICE_KEY_PATH = "/Users/zhunglun/Downloads/chumi/app/serviceAccountKey.json"  # ← 改成你的

# ─────────────────── 1. 初始化 Firebase Admin ───────────────────
cred = credentials.Certificate(SERVICE_KEY_PATH)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()
print("✔ Firestore 初始化完成，專案 ID =", db.project)

# ─────────────────── 2. 題組與題目資料 ───────────────────
COMMON_TITLE = "請聽語音並選出正確單詞"

# 範例 10 題（水果選項）；你可自行更換或增修
base_questions = [
    {"option": ["蘋果", "香蕉", "西瓜", "葡萄"], "ans": 0},
    {"option": ["草莓", "香蕉", "鳳梨", "橘子"], "ans": 1},
    {"option": ["芒果", "番茄", "西瓜", "檸檬"], "ans": 2},
    {"option": ["葡萄", "蘋果", "百香果", "奇異果"], "ans": 0},
    {"option": ["桃子", "鳳梨", "香蕉", "李子"], "ans": 1},
    {"option": ["草莓", "柳橙", "荔枝", "龍眼"], "ans": 0},
    {"option": ["橘子", "梨子", "椰子", "柿子"], "ans": 0},
    {"option": ["萊姆", "檸檬", "柚子", "梅子"], "ans": 1},
    {"option": ["李子", "梅子", "桃子", "杏子"], "ans": 2},
    {"option": ["奇異果", "哈密瓜", "蘋果", "柿子"], "ans": 0}
]

# ─────────────────── 3. 寫入 Unit_1 ~ Unit_5 ───────────────────
for i in range(1, 6):
    unit_id = f"Unit_{i}"
    unit_title = f"水果選擇題 {i}"
    description = "請聽語音並選出正確單詞"

    # 主文件
    unit_ref = db.collection("questionSets").document(unit_id)
    unit_ref.set({
        "unitTitle" : unit_title,
        "description": description,
        "createdAt" : firestore.SERVER_TIMESTAMP,
        "updatedAt" : firestore.SERVER_TIMESTAMP
    }, merge=True)

    # 子集合 questions
    questions_col = unit_ref.collection("questions")
    batch = db.batch()

    for idx, q in enumerate(base_questions, start=1):
        doc_ref = questions_col.document(f"q{idx:02}")   # 固定 ID：q01 ~ q10
        batch.set(doc_ref, {
            "title"    : COMMON_TITLE,
            "option"   : q["option"],
            "ans"      : q["ans"],
            "createdAt": firestore.SERVER_TIMESTAMP
        })

    batch.commit()
    print(f"✅ {unit_id} 完成 (10 題)")

print("🎉 所有單元寫入完成！")

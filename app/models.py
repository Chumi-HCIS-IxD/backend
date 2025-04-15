# app/models.py
from app.extensions import get_firestore_client

# 取得 Firestore 客戶端
db = get_firestore_client()

class User:
    @classmethod
    def get_by_uid(cls, uid):
        """
        根據 uid 查詢 Firestore 中的使用者文件。
        若找到符合的文件，則傳回該文件資料（dict），否則傳回 None。
        """
        users_ref = db.collection("users")
        docs = users_ref.where("uid", "==", uid).limit(1).get()
        if docs:
            return docs[0].to_dict()
        return None

    @classmethod
    def get_by_username(cls, username):
        """
        根據 username 查詢 Firestore 中的使用者文件。
        若找到符合的文件，則傳回該文件資料（dict），否則傳回 None。
        """
        users_ref = db.collection("users")
        docs = users_ref.where("username", "==", username).limit(1).get()
        if docs:
            return docs[0].to_dict()
        return None

    @classmethod
    def create(cls, user_data):
        """
        在 Firestore 中建立一筆新的使用者記錄，
        使用 user_data 中的 uid 作為文件 ID。
        回傳該使用者的 uid。
        """
        uid = user_data.get("uid")
        if not uid:
            raise ValueError("user_data 必須包含 uid")
        users_ref = db.collection("users")
        new_doc = users_ref.document(uid)
        new_doc.set(user_data)
        return uid

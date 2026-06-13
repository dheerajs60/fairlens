import sys
from firebase_admin import firestore, initialize_app, credentials
import json

try:
    from backend.config.firebase_admin import db
    print("DB initialized")
    query = db.collection("audit_history")
    user_id = "test_user"
    user_docs = query.where("user_id", "==", user_id).stream()
    docs = [doc.to_dict() for doc in user_docs]
    print("Success!", len(docs))
except Exception as e:
    import traceback
    traceback.print_exc()

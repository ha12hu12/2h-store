import firebase_admin
from firebase_admin import credentials, messaging
from pathlib import Path


# مسار ملف الاعتماد
firebase_credentials = Path(__file__).resolve().parent.parent / "firebase-credentials.json"

# إنشاء بيانات الاعتماد
cred = credentials.Certificate(firebase_credentials)

# تهيئة Firebase
firebase_admin.initialize_app(cred)


def send_push_notification(tokens: list[str], title: str, body: str):
    # لو ما في أجهزة مسجلة، ما نرسل شي
    if not tokens:
        return

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data={
        "url": "https://2h-store-frontend.vercel.app/"
        },
        tokens=tokens,
    )

    messaging.send_each_for_multicast(message)
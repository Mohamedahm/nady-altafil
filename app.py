from flask import Flask, render_template, request, redirect

from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import psycopg2
import os
load_dotenv()

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
DATABASE_URL = os.getenv("DATABASE_URL")
app = Flask(__name__)

# إعداد قاعدة البيانات
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT,
            start_date DATE,
            is_paid BOOLEAN DEFAULT FALSE,
            sent_payment_email BOOLEAN DEFAULT FALSE
        );
    """)
    conn.commit()
    conn.close()

init_db()

# دالة إرسال الإيميل
def send_welcome_email(to_email, name):
    msg = MIMEText(f"""
مرحبًا {name} 🌟

شكرًا لاشتراكك في نادي طفلي!
لقد بدأت الآن تجربتك المجانية لمدة 3 أيام.

📌 خلال هذه الفترة، سيتم إرسال أنشطة تعليمية يومية لطفلك.

سنراسلك بعد انتهاء الفترة التجريبية في حال رغبتك بالاشتراك الكامل.

مع أطيب التمنيات،
فريق نادي طفلي
    """, "plain", "utf-8")
    msg["Subject"] = "🎉 مرحبًا بك في نادي طفلي"
    msg["From"] = EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
            print(f"✅ تم إرسال الإيميل إلى: {to_email}")
    except Exception as e:
        print(f"❌ فشل إرسال الإيميل: {e}")

@app.route("/")
def index():
    return render_template("index.html")


DATABASE_URL = os.getenv("DATABASE_URL")

@app.route("/subscribe", methods=["GET", "POST"])
def subscribe():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        try:
            conn = psycopg2.connect(DATABASE_URL)
            c = conn.cursor()
            c.execute("""
                INSERT INTO subscribers (name, email, start_date)
                VALUES (%s, %s, %s)
            """, (name, email, datetime.today().strftime('%Y-%m-%d')))
            conn.commit()
            conn.close()

            send_welcome_email(email, name)
            return redirect("/thankyou")

        except Exception as e:
            print(f"❌ Error subscribing user: {e}")
            return "حدث خطأ أثناء الاشتراك، الرجاء المحاولة لاحقًا."

    return render_template("subscribe.html")

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

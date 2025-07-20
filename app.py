from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import psycopg2
import os
import threading
<<<<<<< HEAD
=======

>>>>>>> 33ded97 (🎨 Updated thank you page with email instructions + CSS enhancements)
load_dotenv()

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)

# Initialize DB
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
            sent_payment_email BOOLEAN DEFAULT FALSE,
            last_material_sent DATE,
            subscription_end DATE,
            receipt_sent BOOLEAN DEFAULT FALSE
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id SERIAL PRIMARY KEY,
            type TEXT,
            link TEXT
        );
    """)
    conn.commit()
    conn.close()

init_db()

# Send email
def send_email(to_email, subject, body, html=False):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = to_email

    if html:
        msg.attach(MIMEText(body, "html", "utf-8"))
    else:
        msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
            print(f"✅ Email sent to {to_email}")

            # تسجيل الإيميل في جدول email_logs
        try:
            conn = psycopg2.connect(DATABASE_URL)
            c = conn.cursor()
            c.execute(
                "INSERT INTO email_logs (to_email, subject, body) VALUES (%s, %s, %s)",
                (to_email, subject, body)
            )
            conn.commit()
            conn.close()
        except Exception as log_error:
            print(f"⚠️ فشل تسجيل الإيميل في جدول logs: {log_error}")

    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")

def send_welcome_email(email, name):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute("SELECT link FROM materials WHERE type = 'trial_3days' LIMIT 1")
        result = c.fetchone()
        conn.close()

        material_link = result[0] if result else "لم يتم العثور على رابط المواد."
    except Exception as e:
        material_link = "حدث خطأ في تحميل رابط المواد."

    send_email(
        email,
        "🎉 مرحبًا بك في نادي طفلي",
        f"""
مرحبًا {name} 🌟

شكرًا لاشتراكك في نادي طفلي!
لقد بدأت الآن تجربتك المجانية لمدة 3 أيام.

📌 خلال هذه الفترة، سيتم إرسال أنشطة تعليمية لطفلك.
رابط الأنشطة: {material_link}

سنراسلك بعد انتهاء الفترة التجريبية إذا رغبت بالاستمرار.
"""
    )


# Send receipt as HTML email
def send_receipt_email(name, email):
    html = f"""
    <html>
      <body>
        <h2>إيصال الدفع - نادي طفلي</h2>
        <p><strong>الاسم:</strong> {name}</p>
        <p><strong>البريد:</strong> {email}</p>
        <p><strong>تاريخ الدفع:</strong> {datetime.today().date()}</p>
        <p>شكرًا لاشتراكك! سيتم إرسال المحتوى الأسبوعي تلقائيًا.</p>
      </body>
    </html>
    """
    send_email(email, "📄 إيصال الدفع", html, html=True)

# Send materials
# def send_materials():
#     try:
#         conn = psycopg2.connect(DATABASE_URL)
#         c = conn.cursor()
#
#         c.execute("""
#             SELECT id, name, email, start_date, is_paid, last_material_sent, subscription_end, last_material_type
#             FROM subscribers
#         """)
#
#         rows = c.fetchall()
#         today = datetime.today().date()
#
#         for row in rows:
#             id, name, email, start_date, is_paid, last_sent, end_date, last_material_type = row
#
#             delta = (today - start_date).days
#
#             if not is_paid and delta == 0:
#                 # تجربة 3 أيام
#                 if last_sent is None or last_material_type != 'trial_3days':
#                     c.execute("SELECT link FROM materials WHERE type = 'trial_3days' LIMIT 1")
#                     link = c.fetchone()
#                     if link:
#                         send_email(email, "موادك التعليمية - اليوم الأول", f"رابط الأنشطة: {link[0]}")
#                         c.execute(
#                             "UPDATE subscribers SET last_material_sent = %s, last_material_type = %s WHERE id = %s",
#                             (today, 'trial_3days', id))
#
#             elif is_paid:
#                 if last_material_type != 'complete_4days':
#                     # أول مرة بعد الدفع: إرسال complete_4days
#                     c.execute("SELECT link FROM materials WHERE type = 'complete_4days' LIMIT 1")
#                     link = c.fetchone()
#                     if link:
#                         send_email(email, "📦 مواد مكملة", f"رابط الأنشطة: {link[0]}")
#                         c.execute(
#                             "UPDATE subscribers SET last_material_sent = %s, last_material_type = %s WHERE id = %s",
#                             (today, 'complete_4days', id))
#
#                 elif (today - last_sent).days >= 7 and end_date and today <= end_date:
#                     week_number = ((today - start_date).days) // 7
#                     week_type = f"week_{week_number}"
#                     if last_material_type != week_type:
#                         c.execute("SELECT link FROM materials WHERE type = %s LIMIT 1", (week_type,))
#                         link = c.fetchone()
#                         if link:
#                             send_email(email, "📚 محتوى الأسبوع", f"رابط الأنشطة: {link[0]}")
#                             c.execute(
#                                 "UPDATE subscribers SET last_material_sent = %s, last_material_type = %s WHERE id = %s",
#                                 (today, week_type, id))
#
#         conn.commit()
#         conn.close()
#     except Exception as e:
#         print(f"❌ Error in material scheduler: {e}")


def send_materials():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()

        # تحميل المواد مع تجاهل week_1
        c.execute("SELECT type FROM materials WHERE type != 'week_1' ORDER BY id")
        material_types = [row[0] for row in c.fetchall()]  # e.g. ['trial_3days', 'complete_4days', 'week_2', 'week_3', ...]

        # قراءة المشتركين
        c.execute("""
            SELECT id, name, email, start_date, is_paid, last_material_sent, subscription_end, last_material_type
            FROM subscribers
        """)

        rows = c.fetchall()
        today = datetime.today().date()

        for row in rows:
            id, name, email, start_date, is_paid, last_sent, end_date, last_material_type = row
            delta_days = (today - start_date).days

            if not is_paid and delta_days == 0:
                # تجربة 3 أيام
                if last_sent is None or last_material_type != 'trial_3days':
                    c.execute("SELECT link FROM materials WHERE type = 'trial_3days' LIMIT 1")
                    link = c.fetchone()
                    if link:
                        send_email(email, "موادك التعليمية - المحتوى المجاني", f"رابط الأنشطة: {link[0]}")
                        c.execute(
                            "UPDATE subscribers SET last_material_sent = %s, last_material_type = %s WHERE id = %s",
                            (today, 'trial_3days', id))

            elif is_paid and end_date and today <= end_date:
                # شرط مرور أسبوع على آخر إرسال
                if last_sent is None or (today - last_sent).days >= 7:
                    try:
                        if last_material_type is None:
                            current_index = material_types.index('trial_3days')
                        else:
                            current_index = material_types.index(last_material_type)

                        next_index = current_index + 1
                        if next_index < len(material_types):
                            next_type = material_types[next_index]
                            c.execute("SELECT link FROM materials WHERE type = %s LIMIT 1", (next_type,))
                            link = c.fetchone()
                            if link:
                                print(f"🟢 Sending {next_type} to {email} because last_material_type was {last_material_type}")
                                send_email(email, f"📚 محتوى {next_type}", f"رابط الأنشطة: {link[0]}")
                                c.execute("""
                                    UPDATE subscribers
                                    SET last_material_sent = %s, last_material_type = %s
                                    WHERE id = %s
                                """, (today, next_type, id))
                    except ValueError:
                        print(f"⚠️ لم يتم العثور على {last_material_type} في جدول المواد")

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"❌ Error in material scheduler: {e}")



def check_new_paid_users():
    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()

    today = datetime.today().date()
    new_subscription_end = today + timedelta(days=30)

    # 🧠 Load all materials in order
    c.execute("SELECT type FROM materials ORDER BY id")
    material_types = [row[0] for row in c.fetchall()]  # e.g., ['trial_3days', 'complete_4days', 'week_1', 'week_2', ...]

    # 🔎 Fetch all paid users
    c.execute("""
        SELECT id, name, email, subscription_end, receipt_sent, post_payment_material_sent, last_material_type
        FROM subscribers
        WHERE is_paid = TRUE
    """)
    rows = c.fetchall()

    for id, name, email, subscription_end, receipt_sent, post_sent, last_material_type in rows:
        print(f"🔄 Checking {email} with last: {last_material_type}")

        # 1. Ensure subscription end date
        if not subscription_end or subscription_end <= today:
            c.execute("UPDATE subscribers SET subscription_end = %s WHERE id = %s", (new_subscription_end, id))

        # 2. Determine the next material type
        if not post_sent:
            try:
                if last_material_type is None:
                    next_index = material_types.index('trial_3days') + 1
                else:
                    next_index = material_types.index(last_material_type) + 1

                # Prevent IndexError
                if next_index < len(material_types):
                    next_type = material_types[next_index]
                else:
                    next_type = None

            except ValueError:
                next_type = 'complete_4days'  # fallback

            if next_type:
                # Get link for next material
                c.execute("SELECT link FROM materials WHERE type = %s LIMIT 1", (next_type,))
                link = c.fetchone()
                link_text = link[0] if link else "لم يتم العثور على الرابط."

                # Send material email
                send_email(
                    email,
                    f"📦 مواد {next_type}",
                    f"""
مرحبًا {name} 🌟

✅ تم تأكيد اشتراكك المدفوع بنجاح!

🎁 إليك روابط المواد التعليمية:
👉 {link_text}

🧾 هذه رسالة تؤكد الدفع، ونشكر لك ثقتك.

مع أطيب التحيات،
فريق نادي طفلي
                    """
                )

                # Send receipt if not yet sent
                if not receipt_sent:
                    send_receipt_email(name, email)

                # Update subscriber record
                c.execute("""
                    UPDATE subscribers
                    SET last_material_sent = %s,
                        last_material_type = %s,
                        subscription_end = %s,
                        post_payment_material_sent = TRUE,
                        receipt_sent = TRUE
                    WHERE id = %s
                """, (today, next_type, new_subscription_end, id))

    conn.commit()
    conn.close()




# Background tasks
def background_tasks():
    while True:

        send_materials()
        check_new_paid_users()


        # Payment reminder
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute("""
            SELECT id, name, email, start_date FROM subscribers
            WHERE is_paid = FALSE AND sent_payment_email = FALSE
        """)
        for id, name, email, start_date in c.fetchall():
            if (datetime.today().date() - start_date).days >= 3:
                send_email(email, "💰 هل ترغب بالاستمرار؟", "إذا كنت ترغب بالاستمرار، يرجى الدفع على الحساب المرفق...")
                c.execute("UPDATE subscribers SET sent_payment_email = TRUE WHERE id = %s", (id,))

        # Receipt + set subscription_end if just paid
        c.execute("SELECT id, name, email, subscription_end, receipt_sent FROM subscribers WHERE is_paid = TRUE")
        for id, name, email, end_date, receipt_sent in c.fetchall():
            if not end_date:
                new_end = datetime.today().date() + timedelta(days=30)
                c.execute("UPDATE subscribers SET subscription_end = %s WHERE id = %s", (new_end, id))
            if not receipt_sent:
                send_receipt_email(name, email)
                c.execute("UPDATE subscribers SET receipt_sent = TRUE WHERE id = %s", (id,))

        # Expiration
        c.execute("SELECT id, email, subscription_end FROM subscribers WHERE is_paid = TRUE")
        for id, email, end_date in c.fetchall():
            if end_date and datetime.today().date() >= end_date:
                c.execute("UPDATE subscribers SET is_paid = FALSE WHERE id = %s", (id,))
                send_email(email, "🔔 انتهى اشتراكك", "لقد انتهت فترة اشتراكك، نأمل عودتك قريبًا")

        conn.commit()
        conn.close()
        threading.Event().wait(60)

# Start background task
threading.Thread(target=background_tasks, daemon=True).start()



# Routes
@app.route("/")
def index():
    return render_template("index.html")

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
            """, (name, email, datetime.today().date()))
            conn.commit()
            conn.close()

            send_welcome_email(email, name)
            return redirect("/thankyou")
        except Exception as e:
            return f"❌ Error: {e}"
    return render_template("subscribe.html")


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

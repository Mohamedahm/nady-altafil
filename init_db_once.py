import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def update_schema():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()

        # ✅ إضافة عمود last_material_type إذا لم يكن موجودًا
        c.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscribers' AND column_name='last_material_type'
                ) THEN
                    ALTER TABLE subscribers ADD COLUMN last_material_type TEXT;
                END IF;
            END
            $$;
        """)

        # ✅ إنشاء جدول email_logs إذا لم يكن موجودًا
        c.execute("""
            CREATE TABLE IF NOT EXISTS email_logs (
                id SERIAL PRIMARY KEY,
                to_email TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        conn.close()
        print("✅ تم تعديل قاعدة البيانات وإنشاء جدول email_logs (إن لم يكن موجودًا).")
    except Exception as e:
        print(f"❌ خطأ أثناء تعديل قاعدة البيانات: {e}")

update_schema()

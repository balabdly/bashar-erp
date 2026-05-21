import os
import sqlite3
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Bashar Pro ERP - Python Server")

# السماح بالاتصال بين الواجهة والسيرفر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "erp_database.db"

# دالة لإنشاء قاعدة البيانات والجداول تلقائياً عند التشغيل الأول
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # جدول المشاريع
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT,
            code TEXT,
            type TEXT,
            engineer TEXT,
            status TEXT,
            value REAL,
            progress INTEGER,
            startDate TEXT,
            endDate TEXT
        )
    ''')
    # جدول المخزون
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id TEXT PRIMARY KEY,
            name TEXT,
            sku TEXT,
            quantity REAL,
            unit TEXT,
            minQty REAL,
            warehouse TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- مسارات الـ API للمشاريع ---

@app.get("/api/projects")
def get_projects():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/projects")
def save_projects(projects: list = Body(...)):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects") # مسح القديم للتحديث الشامل المتوافق مع syncStorage
    for p in projects:
        cursor.execute('''
            INSERT INTO projects (id, name, code, type, engineer, status, value, progress, startDate, endDate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (str(p.get('id')), p.get('name'), p.get('code'), p.get('type'), p.get('engineer'), p.get('status'), p.get('value'), p.get('progress'), p.get('startDate'), p.get('endDate')))
    conn.commit()
    conn.close()
    return {"status": "success"}

# --- مسارات الـ API للمخزون ---

@app.get("/api/inventory")
def get_inventory():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/inventory")
def save_inventory(items: list = Body(...)):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory")
    for item in items:
        cursor.execute('''
            INSERT INTO inventory (id, name, sku, quantity, unit, minQty, warehouse)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (str(item.get('id')), item.get('name'), item.get('sku'), item.get('quantity'), item.get('unit'), item.get('minQty'), item.get('warehouse')))
    conn.commit()
    conn.close()
    return {"status": "success"}

# تشغيل صفحة الويب الحالية
@app.get("/")
def read_root():
    return FileResponse("index.html")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print(" جاري تشغيل نظام بشار برو ERP بنجاح عبر بايثون!")
    print(" افتح المتصفح واذهب إلى الرابط التالي: http://127.0.0.1:8000")
    print("="*50 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)

from flask import Flask, request
import requests
import json
import os
import gspread
from google.oauth2 import service_account
from datetime import datetime
import tempfile

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
SHEET_ID = os.environ.get('SHEET_ID')
GOOGLE_CREDENTIALS_JSON = os.environ.get('GOOGLE_CREDENTIALS_JSON')

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# 将 JSON 写入临时文件
with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as temp:
    temp.write(GOOGLE_CREDENTIALS_JSON)
    temp_path = temp.name

credentials = service_account.Credentials.from_service_account_file(temp_path, scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SHEET_ID).sheet1

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.startswith("/创建任务"):
            create_task(chat_id, text)
        elif text.startswith("/开始任务"):
            update_task_status(chat_id, text, "进行中")
        elif text.startswith("/完成任务"):
            update_task_status(chat_id, text, "已完成")
        elif text.startswith("/取消任务"):
            update_task_status(chat_id, text, "已取消")
        elif text.startswith("/我的任务"):
            list_my_tasks(chat_id)
        elif text.startswith("/今天截止"):
            list_today_deadlines(chat_id)
        elif text.startswith("/菜单"):
            send_menu(chat_id)

    return "ok"

def create_task(chat_id, text):
    try:
        content = text.split(" ", 1)[1]
        parts = content.split("，")

        task_content = parts[0]
        assignees = []
        label = "无"
        priority = "中"
        deadline = "未指定"

        for part in parts[1:]:
            if "指派给" in part:
                assignees = part.replace("指派给", "").strip().split(" ")
            if "标签" in part:
                label = part.replace("标签：", "").strip()
            if "优先级" in part:
                priority = part.replace("优先级：", "").strip()
            if "截止时间" in part:
                deadline = part.replace("截止时间：", "").strip()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sheet.append_row([
            task_content, ",".join(assignees), label, priority, "待开始", now, deadline, now
        ])

        msg = f"✅ 任务已创建\n任务内容：{task_content}\n负责人：{', '.join(assignees)}\n标签：{label}\n优先级：{priority}\n截止时间：{deadline}\n当前状态：待开始"
        send_message(chat_id, msg)

    except Exception as e:
        send_message(chat_id, f"❌ 创建任务失败：{e}")

def update_task_status(chat_id, text, new_status):
    try:
        content = text.split(" ", 1)[1].strip()
        all_rows = sheet.get_all_records()
        for idx, row in enumerate(all_rows, start=2):
            if row['任务内容'] == content and row['状态'] not in ["已完成", "已取消"]:
                sheet.update_cell(idx, 5, new_status)
                sheet.update_cell(idx, 8, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                send_message(chat_id, f"✅ 任务【{content}】状态已更新为：{new_status}")
                return
        send_message(chat_id, "❌ 没找到该任务或者已经完成/取消")

    except Exception as e:
        send_message(chat_id, f"❌ 更新任务失败：{e}")

def list_my_tasks(chat_id):
    try:
        mytasks = []
        all_rows = sheet.get_all_records()
        for row in all_rows:
            if row['状态'] not in ["已完成", "已取消"]:
                mytasks.append(f"{row['任务内容']}（{row['标签']}，优先级：{row['优先级']}，截止：{row['截止时间']}）")

        if not mytasks:
            send_message(chat_id, "暂无进行中的任务")
        else:
            send_message(chat_id, "你的任务列表：\n" + "\n".join(mytasks))

    except Exception as e:
        send_message(chat_id, f"❌ 查询失败：{e}")

def list_today_deadlines(chat_id):
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        today_tasks = []
        all_rows = sheet.get_all_records()
        for row in all_rows:
            if today in row['截止时间'] and row['状态'] not in ["已完成", "已取消"]:
                today_tasks.append(f"{row['任务内容']}（优先级：{row['优先级']}）")

        if not today_tasks:
            send_message(chat_id, "今天没有到期任务")
        else:
            send_message(chat_id, "今天到期的任务：\n" + "\n".join(today_tasks))

    except Exception as e:
        send_message(chat_id, f"❌ 查询失败：{e}")

def send_menu(chat_id):
    menu_text = """📋 任务管理Bot指令菜单：
/创建任务 内容，指派给 @成员，标签，优先级，截止时间
/开始任务 内容
/完成任务 内容
/取消任务 内容
/我的任务
/今天截止
/菜单
"""
    send_message(chat_id, menu_text)

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

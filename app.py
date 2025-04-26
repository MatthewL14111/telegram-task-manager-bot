
from flask import Flask, request
import requests
import json
import os
import gspread
from google.oauth2 import service_account
from datetime import datetime

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
SHEET_ID = os.environ.get('SHEET_ID')

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# 重点修正：环境变量中 \n 转为 

credentials_raw = os.environ.get("GOOGLE_CREDENTIALS_JSON")
credentials_str = credentials_raw.replace('\\n', '\n')
credentials_info = json.loads(credentials_str)

credentials = service_account.Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
)

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

# (其他函数逻辑略，为原来内容)

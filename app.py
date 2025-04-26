
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

# 直接在代码中写入 credentials 信息
credentials_json = {
  "type": "service_account",
  "project_id": "telegrambot-457908",
  "private_key_id": "12d8aa325f71339c2aa2e566ea78049e57c670fc",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCpflGx0leTvDAG\n4OWECa9inXMhCjUl97gjnYF7v31YPo52wcDD6yIgxkxEASDsaO54+kbEGB51Um11\nPUHJAz+M/H+JZl7LGuTjeRVViCgJhG+8p8MyxZPfG7QCrACfPTT+RBXguO01hXA7\nlxReDKII7pySfTTrI84nngMpbXPFUphXyynYJTzBy3Wvu0QzES7lCY0xxfyuawAq\nKK5NxUHsaix8BEWngirKCXF6CzBTeU8bPuPg0xghy4/mkQtzpLYQ283hL7pDSFr2\n/resevTboZzTvK1WDAPZWxmzuTHe9oZ79qgvRF2PqoXd/mgtfNRiQPFXYAR7zPZX\naF3rZNj5AgMBAAECggEAEmi5Co9yKeaDEGIxp4hOQ2+euzBSwrmPx1WChGxxWqnr\nuxATBeyGX8kt7CZzux2wBhWH5WFJwJwn7ZeOSz0GNGPR3dxvsA9vHBpRBAHWeGcp\nJDRT9hIh3BYUFIS2ShVhqbq/JhHr2LfyL1S61na4jDAPczU0b9QrHmAyD3g2/m/L\ngonvJJ9t3nsZraf9b5WZwziUmiKcU0+mEbo7Fq0NEBf/HDRCneLM1hq0HqooRKa5\ntsrxQirdxKdgBOXGrh1ee2W0OX9JyQnKXxfWfEWZesdr5zGG67O9+oyzCoJpvIyA\nnhINj9nRt612B6RPmbXpKMB/AgoFRWj3E7vi88GaUQKBgQDQmRg5L5v4Ks09qeT/\n492+CvCFMnWS/Cj1Yox/M6ix4sL244IQV5ZybQUPjimn7VwR5QeiG4yFtM9/MQg5\nPrkGpny0khrDWkpgvdRYBuagNCkciracPpQRfFwhKp3wbINyjurN7fgi8Yjr6Pvd\n3tNrShOkQ80bCVFbJSFM/vh26QKBgQDQAl5F5Y+X7o3lWV89KcrCEh0aAf6r4gLE\nTqRAS+CAlfLaeO6TaHqCY3Za4tbk64ZdIAnAPrJIlv66uwkQNqd3TSApOr5VcdNN\n5PunIsX78Wv85xcea/mObzAIPXTsopV9apHiEmLlzMsV9F5IE+wbX62HGpznQ80m\n2l0WcqwnkQKBgH8UpbNBE+4OdVcZx881DQQYOguLgCF5yaIk1Z8w45brpQcv9y7p\njVhMnoapfys06aBlPU8/JU7XponAX1gwpBwvFU4UrIVS3nktbM3r9linLlybDUEG\nxsIYVzBFfE7abQI/m0C1tzPinh3KpJa4h2iXinvKaowMEypJ5o23z7rxAoGAfoGS\nOExfQnXRUrVCGP6708AUdubTrlGsgRubBYegKFQJ+Rknb/tQ1tALAUeIjn03oJeF\nlqgK4d8DWSm7X2L+Aq6jaq/RZkHt0yf6bTHW211+4bbh9pyQkDHLMpe97tUKudYA\nl0+7WittMBMI7ClBpXxRGyPyXSx9Lq4Lg0WGsiECgYBfggQzqpAg6gXtcggAJdqV\ncH7kTzGE+hCZKUZGRJfYWueAr0EpwUAnn1iOjGh4/t+rN3ZbkziUJJimY8ULGCit\ncpFdjUJ/j4UGmbJxK52GRfQUsfY/OnO/PP6cW5cT+rr/5gfcRarB1ZcWH6VTs77D\npGeQd9jCmvyIWY8bSAkjkw==\n-----END PRIVATE KEY-----\n",
  "client_email": "taskbot-writer@telegrambot-457908.iam.gserviceaccount.com",
  "client_id": "108280162609745483690",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/taskbot-writer%40telegrambot-457908.iam.gserviceaccount.com"
}

credentials = service_account.Credentials.from_service_account_info(
    credentials_json,
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

# 后续任务处理逻辑保持不变

# 以下是后续任务处理逻辑的复用，参考之前版本的create_task, update_task_status, list_my_tasks, list_today_deadlines, send_menu, send_message（为简洁省略）。

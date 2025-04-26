
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

# 直接在代码中写入新的 credentials 信息
credentials_json = {
  "type": "service_account",
  "project_id": "telegrambot-457908",
  "private_key_id": "e328a3a427e94c9793688a3bf86492dae8bf01a2",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCgmJbbP8bYf4Vw\n15zctsgotrZk+feWGmWd1ldthc5e1qaaUr5m2aEjtlE96R+h+NKIHJ8eSO1+AxoZ\nQAHSwsQE7Kt3LNGqs1BJl/jSNCLAnaHDDQ0o5eHJsLjW+uNVWrzzNFmPY0m06s2U\n9YEJSH6/syS8JNflA4ZHNTXC2HhC6Mw2+E0qs5Fd5LJ8GIXxWYBeB4t+uuzsIuQG\nHR+N162iwZnnjEWFAxPZON2Twy+CJMBOWkFyesVzQLkMksRQWagjcQ2GKUfdtzo2\nGOTG6XUlyQxRIC9RvkGpXm5pm6Fdj//v9Ai5hVEukzfiLQSvlpcNT8no69wdDJyV\nW/sDQUzrAgMBAAECggEABCOlW8BQkTr0MbI0+6awZlrokkCzxh18ZK2Qx6S3wCUF\n2ptrBz6bvc5mA1OoujrYvk5dNuFypu6l3mRnx6ANKlf+nA3pLN5TTET2UlYAAU6Z\ndpa1sfSpiv0a6TDtPsFzIPeb9ACp9oJIyzVACVZiLJxi7tXU71+rDIHNbBi6kiA1\nxevKzGdUaj642wuN1M7yOlKQk/cvM7ATI48zfF1mTBsUAEtQGWz6ZF/QiqIkhiJb\njzsuFycLElsTWsPiKYnv5b25UhrVyh43bXJqxyVWRQ6Oj0DmKjvK7tA4B5u2sQ3Q\nojmPBa9yA3scyIO148/f2VvfA7+UNcGtzO78Wxt4EQKBgQDgO0Flb4TnBliq+6Gh\nhmuCpMvKP6StaJUuuKvqubZl4oUTWq3GIjjt1Zgdsu/vKQnmJLtwTwcMrQtaDjmK\ndcvjiIY8WPlgwR6Dvi0EYlSgzcumzAZxACWmTW/rK8AzkO332I2zhgXlb74U6XA1\n1ROYc5rX2UECY7ms5k93l71WuwKBgQC3WVB/R+F54kYfVME5FNr9qFdgxxeWMmer\nTgwjY9IRmEUyz45KiH1WlZf43tO7ke4qOFxP0ABUdfar7myvuVkwO2UCwrjZDK60\n2jPUo06sOSZManvcnAP7oV722mAlEDmbkpv4g5/MS+kGoxXPWvbVSra7nCTOqP+M\nMmCoYpM3kQKBgQDKivvRYmCMRiFFoTIos0Ddq3ohYEeiE7vdjhZMWiA1+9z01I3v\nUO5Xdv6GpSExyMIWTsu48MmPW6fLWtoDBdB74NBQJpZsHUUw/1GuihujfQEd02Fm\nJRndFEmqBcUBT0KFA+lLZh5hVwQ943bmSWf/5zzRCH8+Z1JKqWbSwg/XDQKBgFZX\n8keugymR/LHeiQwnnSWddGC4AYyS+i07GQ5FgPUWP2g5RGonMtdmpWXnEdEgXQd2\n+UoAy1b7Ioo/QuHSKIVFQ0F0j/ZvOYsjwwrdSTxjwXx1HRV8R4flq8IWfvaVWHvC\nJD95RPTBvuCIRsoarWkuwTVCyDamcYoFY22I1olxAoGAIJdLrAKpdqTWjHu5wrh1\naZSyfRa9OcNPEN1v/NzhfJNsnRBfqkEgC/gAcfdtpZbg+hVjOzEv5DnV6WhiQzm8\nWNQrdDRjHVz9VSR2t0vlIdyeHynxJ6rgPAQC7h04abBnzpKMgGmda27TBfaPL3J0\nqS0WjStxtquUIvIywD2kzvE=\n-----END PRIVATE KEY-----\n",
  "client_email": "telegram-bot-sa@telegrambot-457908.iam.gserviceaccount.com",
  "client_id": "100755840496833240798",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/telegram-bot-sa%40telegrambot-457908.iam.gserviceaccount.com"
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

# 后续 task function 保持原有逻辑

# （后面保持原有逻辑，包括 create_task, update_task_status, list_my_tasks, list_today_deadlines, send_menu, send_message 等）

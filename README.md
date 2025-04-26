# Telegram 任务管理机器人 (中文)

## 功能
- 创建任务（内容、负责人、标签、优先级、截止时间）
- 更新任务状态
- 查询自己的任务
- 每日到期任务提醒
- 群组中文指令操作

## 部署到 Render
1. 新建 Web Service
2. 上传代码或连 GitHub
3. 配置环境变量：
    - `TELEGRAM_TOKEN`
    - `SHEET_ID`
    - `GOOGLE_CREDENTIALS_JSON`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python app.py`

## 使用指令
```
/创建任务 内容，指派给 @成员，标签，优先级，截止时间
/开始任务 内容
/完成任务 内容
/取消任务 内容
/我的任务
/今天截止
/菜单
```
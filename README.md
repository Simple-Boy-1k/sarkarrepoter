# 🤖 Telegram Multi-Account Manager & Report Bot

Pyrogram V2 aur MongoDB (Motor) par bana Telegram Bot.

---

## 🚀 Deploy to Heroku

Single-click deployment ke liye niche button par click karein:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Simple-Boy-1k/sarkarrepoter)

---

## ⚙️ Environment Variables (Config Vars)

Heroku par deploy karte waqt ye 5 variables set karein:

| Variable Name | Description |
| :--- | :--- |
| `API_ID` | Telegram API ID ([my.telegram.org](https://my.telegram.org) se) |
| `API_HASH` | Telegram API HASH ([my.telegram.org](https://my.telegram.org) se) |
| `BOT_TOKEN` | Bot Token ([@BotFather](https://t.me/BotFather) se) |
| `MONGO_URL` | MongoDB Connection URI |
| `OWNER_ID` | Aapka Numeric Telegram User ID |

---

## 📁 Repository Structure

```text
├── bot.py
├── Procfile
├── requirements.txt
├── runtime.txt
├── app.json
└── README.md

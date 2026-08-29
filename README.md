# 🤖 Telegram Multi-Account Manager & Report Bot

Pyrogram V2 aur MongoDB (Motor) par bana Telegram Bot jo String Sessions manage karne, Channel Reports handle karne, aur Owner Control Panel provide karne ke liye design kiya gaya hai.

---

## 🚀 Deploy to Heroku

Single-click deployment ke liye niche diye gaye button par click karein:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME)

> ⚠️ **Note:** README save karne se pehle link me `YOUR_GITHUB_USERNAME` ko apne GitHub Username se aur `YOUR_REPO_NAME` ko apni Repository ke naam se replace kar dein.

---

## ⚙️ Environment Variables (Config Vars)

Heroku par deploy karte waqt ye 5 variables set karna zaroori hai:

| Variable Name | Description |
| :--- | :--- |
| `API_ID` | Telegram API ID ([my.telegram.org](https://my.telegram.org) se milegi) |
| `API_HASH` | Telegram API HASH ([my.telegram.org](https://my.telegram.org) se milegi) |
| `BOT_TOKEN` | Bot Token ([@BotFather](https://t.me/BotFather) se milega) |
| `MONGO_URL` | MongoDB Cluster Connection String |
| `OWNER_ID` | Aapka numeric Telegram User ID |

---

## ✨ Main Features

* **➕ Account Addition:** Pyrogram V2 String Session live validation ke sath add karein.
* **📱 My Accounts:** Saved accounts ki list dekhein aur single-click delete karein.
* **📢 Channel Report:** Interactive Inline Keyboard se step-by-step reporting.
* **👑 Owner Admin Panel:** Total stats, DB accounts management, aur mass broadcast system.

---

## 📁 Repository Structure

```text
├── bot.py
├── Procfile
├── requirements.txt
├── runtime.txt
├── app.json
└── README.md


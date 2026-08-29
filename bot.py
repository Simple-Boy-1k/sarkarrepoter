import os
import logging
import asyncio
import motor.motor_asyncio
from bson.objectid import ObjectId
from pyrogram import Client, filters, idle
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message
)

# Logging Setup
logging.basicConfig(level=logging.INFO)

# ==================== CONFIGURATION ====================
API_ID = int(os.environ.get("API_ID", "123456"))
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "123456789"))
MONGO_URL = os.environ.get("MONGO_URL", "YOUR_MONGO_URL")

# Database Connection with Timeout
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGO_URL,
    serverSelectionTimeoutMS=5000
)
db = mongo_client["multi_account_bot_db"]
accounts_col = db["user_accounts"]
reports_col = db["submitted_reports"]
users_col = db["bot_users"]

USER_STATES = {}

app = Client(
    "multi_account_manager_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==================== KEYBOARDS ====================

def get_main_keyboard(user_id):
    buttons = [
        [
            InlineKeyboardButton("➕ Add Account", callback_data="btn_add_account"),
            InlineKeyboardButton("📱 My Accounts", callback_data="btn_my_accounts")
        ],
        [
            InlineKeyboardButton("📢 Report Channel", callback_data="btn_start_report")
        ],
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="btn_help"),
            InlineKeyboardButton("👑 Owner", url="https://t.me/Simple_Boy_1k")
        ]
    ]
    if user_id == OWNER_ID:
        buttons.append([InlineKeyboardButton("⚙️ Owner Admin Panel", callback_data="btn_admin_panel")])
    return InlineKeyboardMarkup(buttons)

def get_cancel_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="btn_cancel")]])

def get_admin_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Total Stats", callback_data="adm_stats"),
            InlineKeyboardButton("🗂 All DB Accounts", callback_data="adm_all_accs")
        ],
        [
            InlineKeyboardButton("📢 Broadcast Message", callback_data="adm_broadcast")
        ],
        [
            InlineKeyboardButton("🔙 Main Menu", callback_data="btn_back_main")
        ]
    ])

# ==================== HELPER FUNCTION ====================

async def validate_and_get_me(session_string: str):
    temp_client = Client(
        "session_tester",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=session_string,
        in_memory=True
    )
    try:
        await temp_client.connect()
        me = await temp_client.get_me()
        await temp_client.disconnect()
        return me
    except Exception:
        try:
            await temp_client.disconnect()
        except Exception:
            pass
        return None

# ==================== COMMAND HANDLERS ====================

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id
    USER_STATES.pop(user_id, None)

    # Safe DB User Insert
    try:
        await users_col.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id, "first_name": message.from_user.first_name}},
            upsert=True
        )
    except Exception as e:
        logging.error(f"Database Connection Error: {e}")

    start_text = (
        f"👋 **Welcome, {message.from_user.first_name}!**\n\n"
        "Ye bot Telegram Accounts (Pyrogram String Sessions) aur Illegal Channel Reporting manage karne ke liye hai."
    )
    await message.reply_text(start_text, reply_markup=get_main_keyboard(user_id))

@app.on_message(filters.command("admin") & filters.private)
async def admin_cmd_handler(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        await message.reply_text("⛔ **Access Denied! Aap owner nahi hain.**")
        return
    await message.reply_text("👑 **OWNER CONTROL PANEL**", reply_markup=get_admin_keyboard())

# ==================== CALLBACK QUERY HANDLER ====================

@app.on_callback_query()
async def callback_handler(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data

    # User Actions
    if data == "btn_add_account":
        USER_STATES[user_id] = {"step": "WAITING_FOR_SESSION"}
        await callback_query.answer()
        await callback_query.edit_message_text(
            "🔑 **Pyrogram V2 String Session Bhejein:**",
            reply_markup=get_cancel_keyboard()
        )

    elif data == "btn_my_accounts":
        await callback_query.answer()
        try:
            user_accs = await accounts_col.find({"added_by": user_id}).to_list(length=100)
        except Exception as e:
            logging.error(f"DB Error: {e}")
            user_accs = []

        if not user_accs:
            await callback_query.edit_message_text(
                "❌ Aapka koi account added nahi hai.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="btn_back_main")]])
            )
            return

        acc_buttons = []
        text = f"📱 **Aapke Accounts ({len(user_accs)}):**\n\n"
        for idx, acc in enumerate(user_accs, 1):
            text += f"{idx}. {acc.get('first_name')} | ID: `{(acc.get('account_id'))}`\n"
            acc_buttons.append([InlineKeyboardButton(f"🗑 Delete {acc.get('first_name')}", callback_data=f"del_acc_{acc.get('_id')}")])
        acc_buttons.append([InlineKeyboardButton("🔙 Back", callback_data="btn_back_main")])
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(acc_buttons))

    elif data.startswith("del_acc_"):
        acc_doc_id = data.replace("del_acc_", "")
        query = {"_id": ObjectId(acc_doc_id)} if user_id == OWNER_ID else {"_id": ObjectId(acc_doc_id), "added_by": user_id}
        try:
            await accounts_col.delete_one(query)
        except Exception as e:
            logging.error(f"DB Delete Error: {e}")
        await callback_query.answer("✅ Account Removed!", show_alert=True)
        await callback_query.edit_message_text("🗑 **Account Database se remove ho gaya.**", reply_markup=get_main_keyboard(user_id))

    elif data == "btn_start_report":
        USER_STATES[user_id] = {"step": "WAITING_FOR_LINK"}
        await callback_query.answer()
        await callback_query.edit_message_text("📌 **Channel Link/Username Bhejein:**", reply_markup=get_cancel_keyboard())

    elif data == "btn_help":
        await callback_query.answer()
        await callback_query.edit_message_text(
            "ℹ️ **Help Options:**\n\n1. **Add Account:** Connect your Telegram session.\n2. **Report:** Submit channel link and reason.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="btn_back_main")]])
        )

    # Owner / Admin Actions
    elif data == "btn_admin_panel":
        if user_id != OWNER_ID:
            await callback_query.answer("⛔ Access Denied!", show_alert=True)
            return
        await callback_query.answer()
        await callback_query.edit_message_text("👑 **OWNER CONTROL PANEL**", reply_markup=get_admin_keyboard())

    elif data == "adm_stats":
        if user_id != OWNER_ID: return
        await callback_query.answer()
        try:
            tot_users = await users_col.count_documents({})
            tot_accs = await accounts_col.count_documents({})
            tot_reports = await reports_col.count_documents({})
        except Exception:
            tot_users = tot_accs = tot_reports = 0

        stats_text = (
            "📊 **SYSTEM STATS (OWNER PANEL)**\n\n"
            f"👤 **Total Bot Users:** `{tot_users}`\n"
            f"📱 **Total Accounts in DB:** `{tot_accs}`\n"
            f"📝 **Total Reports Submitted:** `{tot_reports}`"
        )
        await callback_query.edit_message_text(stats_text, reply_markup=get_admin_keyboard())

    elif data == "adm_all_accs":
        if user_id != OWNER_ID: return
        await callback_query.answer()
        try:
            all_accs = await accounts_col.find().to_list(length=100)
        except Exception:
            all_accs = []

        if not all_accs:
            await callback_query.edit_message_text("❌ Database me koi account nahi hai.", reply_markup=get_admin_keyboard())
            return

        acc_buttons = []
        text = f"🗂 **Database Ke Saare Accounts ({len(all_accs)}):**\n\n"
        for idx, acc in enumerate(all_accs, 1):
            text += f"{idx}. {acc.get('first_name')} | User: `{acc.get('added_by')}` | ID: `{acc.get('account_id')}`\n"
            acc_buttons.append([InlineKeyboardButton(f"🚨 Delete {acc.get('first_name')}", callback_data=f"del_acc_{acc.get('_id')}")])
        acc_buttons.append([InlineKeyboardButton("🔙 Back Admin", callback_data="btn_admin_panel")])
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(acc_buttons))

    elif data == "adm_broadcast":
        if user_id != OWNER_ID: return
        USER_STATES[user_id] = {"step": "WAITING_FOR_BROADCAST"}
        await callback_query.answer()
        await callback_query.edit_message_text("📢 **Message Bhejein:**\nJo message sabhi bot users ko bhejna hai wo yahan type karein.", reply_markup=get_cancel_keyboard())

    elif data in ["btn_cancel", "btn_back_main"]:
        USER_STATES.pop(user_id, None)
        await callback_query.answer()
        await callback_query.edit_message_text("<b>👑 Main Menu</b>", reply_markup=get_main_keyboard(user_id))

# ==================== MESSAGE INPUT HANDLER ====================

@app.on_message(filters.private & ~filters.command(["start", "admin"]))
async def message_input_handler(client: Client, message: Message):
    user_id = message.from_user.id
    state = USER_STATES.get(user_id)

    if not state:
        return

    step = state.get("step")

    # Account Add System
    if step == "WAITING_FOR_SESSION":
        session_str = message.text.strip()
        status_msg = await message.reply_text("⏳ **Session testing...**")
        acc_me = await validate_and_get_me(session_str)

        if not acc_me:
            await status_msg.edit_text("❌ **Invalid Session String!**", reply_markup=get_cancel_keyboard())
            return

        try:
            existing = await accounts_col.find_one({"account_id": acc_me.id})
            if existing:
                await status_msg.edit_text("⚠️ **Yeh account pehle se DB me hai!**", reply_markup=get_main_keyboard(user_id))
                USER_STATES.pop(user_id, None)
                return

            await accounts_col.insert_one({
                "added_by": user_id,
                "account_id": acc_me.id,
                "first_name": acc_me.first_name,
                "username": acc_me.username or "",
                "session_string": session_str
            })
        except Exception as e:
            logging.error(f"DB Error: {e}")

        USER_STATES.pop(user_id, None)
        await status_msg.edit_text(f"✅ **Account Added!** Name: {acc_me.first_name}", reply_markup=get_main_keyboard(user_id))

    # Report System
    elif step == "WAITING_FOR_LINK":
        link = message.text.strip()
        USER_STATES[user_id] = {"step": "WAITING_FOR_REASON", "link": link}
        await message.reply_text("📝 **Reason Bhejein:**", reply_markup=get_cancel_keyboard())

    elif step == "WAITING_FOR_REASON":
        reason = message.text.strip()
        link = state.get("link")
        USER_STATES.pop(user_id, None)

        try:
            await reports_col.insert_one({"user_id": user_id, "target": link, "reason": reason})
        except Exception as e:
            logging.error(f"DB Error: {e}")

        try:
            await client.send_message(
                OWNER_ID,
                f"🚨 **New Report!**\nUser: `{user_id}`\nTarget: {link}\nReason: {reason}"
            )
        except Exception:
            pass

        await message.reply_text("✅ **Report Submitted!**", reply_markup=get_main_keyboard(user_id))

    # Owner Broadcast System
    elif step == "WAITING_FOR_BROADCAST" and user_id == OWNER_ID:
        USER_STATES.pop(user_id, None)
        try:
            users = await users_col.find().to_list(length=5000)
        except Exception:
            users = []
        success = 0
        status_msg = await message.reply_text("⏳ **Broadcast bhej raha hu...**")

        for u in users:
            try:
                await message.copy(u["user_id"])
                success += 1
                await asyncio.sleep(0.1)
            except Exception:
                pass

        await status_msg.edit_text(f"✅ **Broadcast Done!** Delivered to {success} users.", reply_markup=get_main_keyboard(user_id))

# ==================== BOT RUNNER ====================

async def main():
    await app.start()
    logging.info("Bot Started Successfully!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())

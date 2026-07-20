import asyncio
import logging
import random
import json
import os
import shutil
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ChatMemberHandler, ConversationHandler, filters

logging.basicConfig(level=logging.INFO)

TOKEN = "8694643746:AAE2bLh7yOR5XfxEl9RzvvvHH4PoNX-fsX0"
CHAT_LINK = "https://t.me/joinchat/75xD5Z_btvliOGJi"
SUPPORT_USERNAME = "@mix_929"
ADMIN_ID = 6901387556
REVIEW_CHAT_ID = -1003644060282
BOOST_LINK = "https://t.me/boost/popa0193"
INVITE_LINK = "https://t.me/joinchat/75xD5Z_btvliOGJi"

BACKUP_DIR = "backups"
COUNTRIES_FILE = "countries_s3.json"
PENDING_FILE = "pending_s3.json"
RESOURCES_FILE = "resources_s3.json"
ARCHIVE_FILE = "archive.json"
REVIEWS_FILE = "reviews_s3.json"
USERS_FILE = "users_s3.json"
BANNED_FILE = "banned.json"
ADMINS_FILE = "admins.json"
MAPER_FILE = "maper.json"
MAPER_ORDERS_FILE = "maper_orders.json"
MAPER_DONE_FILE = "maper_done.json"
ADMIN_LOG_FILE = "admin_log.json"
SURVEYS_FILE = "surveys.json"
RESOURCES_LIST_FILE = "resources.txt"

os.makedirs(BACKUP_DIR, exist_ok=True)

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_txt(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return ["Нет данных."]

def load_txt_full(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def load_resources():
    return load_txt(RESOURCES_LIST_FILE)

def get_random_resources():
    all_res = load_resources()
    if not all_res: return ["Ресурсы не найдены"]
    return random.sample(all_res, min(4, len(all_res)))

def load_mechanics():
    if os.path.exists("mechanics.txt"):
        with open("mechanics.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "Механика не найдена."

def load_start_conditions():
    if os.path.exists("start_conditions.txt"):
        with open("start_conditions.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "Стартовые условия не найдены."

def backup_files():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for f in [COUNTRIES_FILE, PENDING_FILE, RESOURCES_FILE, ARCHIVE_FILE, REVIEWS_FILE, USERS_FILE, BANNED_FILE, ADMINS_FILE, MAPER_FILE, MAPER_ORDERS_FILE, MAPER_DONE_FILE, ADMIN_LOG_FILE, SURVEYS_FILE]:
        if os.path.exists(f):
            shutil.copy2(f, os.path.join(BACKUP_DIR, f"{timestamp}_{f}"))

reviews = load_json(REVIEWS_FILE)
countries = load_json(COUNTRIES_FILE)
pending_countries = load_json(PENDING_FILE)
resources_data = load_json(RESOURCES_FILE)
archive = load_json(ARCHIVE_FILE)
all_users = load_json(USERS_FILE)
banned_users = set(load_json(BANNED_FILE))
admins_list = set(load_json(ADMINS_FILE))
maper_ids = set()
maper_id = None
maper_data = load_json(MAPER_FILE)
if maper_data:
    if "ids" in maper_data:
        maper_ids = set(maper_data["ids"])
        maper_id = list(maper_ids)[0] if maper_ids else None
    elif "id" in maper_data:
        maper_ids = {maper_data["id"]}
        maper_id = maper_data["id"]
maper_orders = load_json(MAPER_ORDERS_FILE)
maper_done = load_json(MAPER_DONE_FILE)
admin_log = load_json(ADMIN_LOG_FILE)
user_surveys = load_json(SURVEYS_FILE)

if not all_users: all_users = {}
if not maper_orders: maper_orders = {}
if not maper_done: maper_done = {}
if not admin_log: admin_log = []
if not user_surveys: user_surveys = {}

season_number = 3
season_name = "Сезон 3 (2008)"
season_archived = False
country_counter = {3: 0}
if archive and archive.get("season_3_archived", False):
    season_archived = True
if countries:
    country_counter[3] = max(c.get("number", 0) for c in countries.values())
else:
    country_counter[3] = 0

def is_banned(uid):
    return uid in banned_users

import handlers as h

h.TOKEN = TOKEN
h.CHAT_LINK = CHAT_LINK
h.SUPPORT_USERNAME = SUPPORT_USERNAME
h.ADMIN_ID = ADMIN_ID
h.REVIEW_CHAT_ID = REVIEW_CHAT_ID
h.BOOST_LINK = BOOST_LINK
h.INVITE_LINK = INVITE_LINK
h.ALL_RESOURCES = load_resources()
h.season_number = season_number
h.season_name = season_name
h.country_counter = country_counter
h.countries = countries
h.pending_countries = pending_countries
h.all_users = all_users
h.banned_users = banned_users
h.admins_list = admins_list
h.maper_ids = maper_ids
h.maper_id = maper_id
h.maper_orders = maper_orders
h.maper_done = maper_done
h.season_archived = season_archived
h.admin_log = admin_log
h.user_surveys = user_surveys
h.reviews = reviews
h.resources_data = resources_data
h.archive = archive
h.COUNTRIES_FILE = COUNTRIES_FILE
h.PENDING_FILE = PENDING_FILE
h.RESOURCES_FILE = RESOURCES_FILE
h.ARCHIVE_FILE = ARCHIVE_FILE
h.REVIEWS_FILE = REVIEWS_FILE
h.USERS_FILE = USERS_FILE
h.BANNED_FILE = BANNED_FILE
h.ADMINS_FILE = ADMINS_FILE
h.MAPER_FILE = MAPER_FILE
h.MAPER_ORDERS_FILE = MAPER_ORDERS_FILE
h.MAPER_DONE_FILE = MAPER_DONE_FILE
h.ADMIN_LOG_FILE = ADMIN_LOG_FILE
h.SURVEYS_FILE = SURVEYS_FILE

h.load_json = load_json
h.save_json = save_json
h.load_txt = load_txt
h.load_txt_full = load_txt_full
h.load_mechanics = load_mechanics
h.load_start_conditions = load_start_conditions
h.get_random_resources = get_random_resources
h.is_banned = is_banned

class Handler(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def log_message(self, format, *args): pass

def run_http():
    try: HTTPServer(('0.0.0.0', 10000), Handler).serve_forever()
    except: pass

def auto_backup():
    while True: time.sleep(3600); backup_files()

def main():
    threading.Thread(target=run_http, daemon=True).start()
    threading.Thread(target=auto_backup, daemon=True).start()
    time.sleep(2)

    while True:
        try:
            app = Application.builder().token(TOKEN).build()

            conv_handler = ConversationHandler(
                entry_points=[CallbackQueryHandler(h.start_create_country, pattern="^start_create$")],
                states={
                    h.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, h.get_name)],
                    h.SPAWN: [MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, h.get_spawn)],
                    h.FLAG: [MessageHandler(filters.PHOTO | filters.Document.ALL, h.get_flag)],
                    h.EXTRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, h.get_extra), CallbackQueryHandler(h.skip_extra, pattern="^skip_extra$")],
                    h.CONFIRM: [CallbackQueryHandler(h.change_menu, pattern="^change_something$"), CallbackQueryHandler(h.submit_to_admin, pattern="^submit_to_admin$")],
                    h.CHANGE_MENU: [CallbackQueryHandler(h.change_name_start, pattern="^change_name$"), CallbackQueryHandler(h.change_spawn_start, pattern="^change_spawn$"), CallbackQueryHandler(h.change_flag_start, pattern="^change_flag$"), CallbackQueryHandler(h.change_extra_start, pattern="^change_extra$"), CallbackQueryHandler(h.submit_to_admin, pattern="^submit_to_admin$")],
                    h.CHANGE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, h.change_name_done)],
                    h.CHANGE_SPAWN: [MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, h.change_spawn_done)],
                    h.CHANGE_FLAG: [MessageHandler(filters.PHOTO | filters.Document.ALL, h.change_flag_done)],
                    h.CHANGE_EXTRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, h.change_extra_done), CallbackQueryHandler(h.skip_extra_change, pattern="^skip_extra_change$")],
                    h.EDIT_COUNTRY: [CallbackQueryHandler(h.edit_name_start, pattern="^edit_name$"), CallbackQueryHandler(h.edit_flag_start, pattern="^edit_flag$")],
                    h.EDIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, h.edit_name_done)],
                    h.EDIT_FLAG: [MessageHandler(filters.PHOTO | filters.Document.ALL, h.edit_flag_done)],
                    h.ADMIN_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, h.broadcast_message)],
                    h.ADMIN_BROADCAST_CONFIRM: [CallbackQueryHandler(h.button_handler, pattern="^admin_broadcast_yes$"), CallbackQueryHandler(h.button_handler, pattern="^admin_broadcast_no$")],
                },
                fallbacks=[CallbackQueryHandler(h.cancel_create, pattern="^back_to_menu$"), CommandHandler("cancel", h.cancel_broadcast)],
            )

            review_handler = ConversationHandler(
                entry_points=[CallbackQueryHandler(h.write_review_start, pattern="^write_review$")],
                states={h.REVIEW_WRITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, h.review_received)], h.REVIEW_RATING: [CallbackQueryHandler(h.review_rating, pattern="^rate_")]},
                fallbacks=[CallbackQueryHandler(h.cancel_review, pattern="^reviews_menu$")],
            )

            app.add_handler(CommandHandler("start", h.start))
            app.add_handler(CommandHandler("admin", h.admin_command))
            app.add_handler(CommandHandler("adm", h.mod_command))
            app.add_handler(CommandHandler("map", h.maper_command))
            app.add_handler(CommandHandler("addadmin", h.addadmin_command))
            app.add_handler(CommandHandler("tempban", h.tempban_command))
            app.add_handler(CommandHandler("stata", h.stata_command))
            app.add_handler(CommandHandler("info", h.info_command))
            app.add_handler(CommandHandler("menu", h.menu_command))
            app.add_handler(ChatMemberHandler(h.welcome_new_member, chat_member_types=ChatMemberHandler.CHAT_MEMBER))
            app.add_handler(ChatMemberHandler(h.member_banned, chat_member_types=ChatMemberHandler.CHAT_MEMBER))
            app.add_handler(conv_handler)
            app.add_handler(review_handler)
            app.add_handler(CallbackQueryHandler(h.admin_approve, pattern="^approve_"))
            app.add_handler(CallbackQueryHandler(h.admin_reject_menu, pattern="^reject_menu_"))
            app.add_handler(CallbackQueryHandler(h.admin_reject_confirm, pattern="^reject_"))
            app.add_handler(CallbackQueryHandler(h.admin_cancel_reject, pattern="^cancel_reject_"))
            app.add_handler(CallbackQueryHandler(h.button_handler))

            try:
                app.job_queue.run_repeating(h.periodic_promo_personal, interval=14400, first=10)
                app.job_queue.run_repeating(h.periodic_promo_chat, interval=14400, first=30)
            except: pass

            print(f"Бот запущен! {season_name}")
            app.run_polling(drop_pending_updates=True)

        except Exception as e:
            print(f"Ошибка: {e}. Перезапуск через 10 сек...")
            time.sleep(10)

if __name__ == "__main__":
    main()

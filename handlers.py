import asyncio
import random
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

NAME, SPAWN, FLAG, EXTRA, CONFIRM, CHANGE_MENU, CHANGE_NAME, CHANGE_SPAWN, CHANGE_FLAG, CHANGE_EXTRA = range(10)
REVIEW_WRITE, REVIEW_RATING = 99, 100
ADMIN_BROADCAST = 200
ADMIN_BROADCAST_CONFIRM = 201
EDIT_COUNTRY, EDIT_NAME, EDIT_FLAG = 300, 301, 302

TOKEN = ""
CHAT_LINK = ""
SUPPORT_USERNAME = ""
ADMIN_ID = 0
REVIEW_CHAT_ID = 0
BOOST_LINK = ""
INVITE_LINK = ""
ALL_RESOURCES = []

season_number = 3
season_name = "Сезон 3 (2008)"
country_counter = {3: 0}
countries = {}
pending_countries = {}
all_users = {}
banned_users = set()
admins_list = set()
maper_ids = set()
maper_id = None
maper_orders = {}
maper_done = {}
season_archived = False
admin_log = []
user_surveys = {}

COUNTRIES_FILE = ""
PENDING_FILE = ""
RESOURCES_FILE = ""
ARCHIVE_FILE = ""
REVIEWS_FILE = ""
USERS_FILE = ""
BANNED_FILE = ""
ADMINS_FILE = ""
MAPER_FILE = ""
MAPER_ORDERS_FILE = ""
MAPER_DONE_FILE = ""
ADMIN_LOG_FILE = ""
SURVEYS_FILE = ""

reviews = {}
resources_data = {}
archive = {}

def load_json(filename): pass
def save_json(filename, data): pass
def load_txt(filename): return []
def load_txt_full(filename): return ""
def load_mechanics(): return ""
def load_start_conditions(): return ""
def get_random_resources(): return []
def is_banned(uid): return False

def season_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🪨 Мои ресурсы", callback_data="my_resources")],
        [InlineKeyboardButton("🏛 Моя страна", callback_data="my_country")],
        [InlineKeyboardButton("🌍 Ресурсы других", callback_data="other_resources")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_to_menu")]
    ])

def reviews_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ Написать отзыв", callback_data="write_review")],
        [InlineKeyboardButton("📋 Читать отзывы", callback_data="read_reviews")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
    ])

def rating_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton(str(i), callback_data=f"rate_{i}") for i in range(1, 6)]])

def admin_commands_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🪨 Ресурсы", callback_data="admin_resources")],
        [InlineKeyboardButton("🏛 Страны", callback_data="admin_all_countries")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast_start")],
        [InlineKeyboardButton("📦 Архив", callback_data="admin_archive_menu")],
        [InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("🚫 Бан-лист", callback_data="admin_banlist")],
        [InlineKeyboardButton("👥 Администрирование", callback_data="admin_control")],
        [InlineKeyboardButton("🗺 Работа мапера", callback_data="admin_maper_status")],
        [InlineKeyboardButton("📊 Откуда приходят", callback_data="admin_surveys")],
        [InlineKeyboardButton("📋 Все команды", callback_data="admin_all_commands")],
        [InlineKeyboardButton("🔙 Закрыть", callback_data="admin_close")]
    ])

def mod_commands_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Заявки", callback_data="mod_pending")],
        [InlineKeyboardButton("🏛 Страны", callback_data="mod_countries")],
        [InlineKeyboardButton("📊 Статистика", callback_data="mod_stats")],
        [InlineKeyboardButton("⚠️ Бан", callback_data="mod_tempban")],
        [InlineKeyboardButton("🚫 Бан-лист", callback_data="mod_banlist")],
        [InlineKeyboardButton("🔙 Закрыть", callback_data="mod_close")]
    ])

def maper_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Новые заказы", callback_data="maper_new_orders")],
        [InlineKeyboardButton("✅ Выполненные", callback_data="maper_done_orders")],
        [InlineKeyboardButton("🌍 Список стран", callback_data="maper_countries")],
        [InlineKeyboardButton("🚫 Бан-лист", callback_data="maper_banlist")],
        [InlineKeyboardButton("🔙 Закрыть", callback_data="maper_close")]
    ])

def stata_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌍 Список стран", callback_data="stata_countries")],
        [InlineKeyboardButton("📅 История сезонов", callback_data="stata_seasons")],
        [InlineKeyboardButton("🆘 Помощь", callback_data="stata_help")],
    ])

async def ban_msg(update):
    msg = load_txt_full("ban_msg.txt")
    if update.message: await update.message.reply_html(msg)
    elif update.callback_query: await update.callback_query.edit_message_text(msg, parse_mode="HTML")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global all_users, user_surveys
    uid = update.message.from_user.id
    if is_banned(uid): await ban_msg(update); return
    user_id = str(uid)
    username = update.message.from_user.username or f"user_{user_id}"
    if user_id not in all_users:
        all_users[user_id] = {"username": username, "date": datetime.now().strftime("%d.%m.%Y %H:%M"), "season": season_number}
        save_json(USERS_FILE, all_users)
        welcomes = load_txt("welcome_ls.txt")
        await update.message.reply_html(random.choice(welcomes) if welcomes else "Добро пожаловать в Яблочное РП!")
        if user_id not in user_surveys: context.job_queue.run_once(send_survey, 3600, chat_id=uid)
    text = f"🍎 <b>Яблочное РП!</b>\n\n📅 <b>{season_name}</b>\n\n⚔️ Создай страну!\n<i>Готов?</i>"
    kb = [[InlineKeyboardButton("📋 Меню", callback_data="back_to_menu")],[InlineKeyboardButton("🍏 Вход в РП", callback_data="enter_rp")],[InlineKeyboardButton("📖 О игре", callback_data="about_game")],[InlineKeyboardButton("🆘 Помощь", callback_data="help_menu")]]
    await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(kb))

async def send_survey(context: ContextTypes.DEFAULT_TYPE):
    try:
        kb = [[InlineKeyboardButton("📱 ТикТок", callback_data="survey_tiktok")],[InlineKeyboardButton("🎬 YouTube", callback_data="survey_youtube")],[InlineKeyboardButton("👥 Друг", callback_data="survey_friend")],[InlineKeyboardButton("📢 Реклама", callback_data="survey_ad")],[InlineKeyboardButton("💬 Другое", callback_data="survey_other")]]
        await context.bot.send_message(chat_id=context.job.chat_id, text="📋 Откуда узнали?", reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    except: pass

async def survey_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_surveys
    q = update.callback_query; await q.answer()
    m = {"survey_tiktok":"📱 ТикТок","survey_youtube":"🎬 YouTube","survey_friend":"👥 Друг","survey_ad":"📢 Реклама","survey_other":"💬 Другое"}
    user_surveys[str(q.from_user.id)] = m.get(q.data, q.data)
    save_json(SURVEYS_FILE, user_surveys)
    await q.edit_message_text("✅ Спасибо!")

async def stata_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_banned(update.message.from_user.id): await ban_msg(update); return
    await update.message.reply_html("🍎 <b>Я бот РП!</b>", reply_markup=stata_keyboard())

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_banned(update.message.from_user.id): await ban_msg(update); return
    args = context.args
    if args:
        try:
            num = int(args[0])
            found = next((c for c in countries.values() if c.get("number")==num), None)
            if found: text = f"🏛 №{found['number']}\n📛 {found['name']}\n👤 @{found['username']}\n📅 {found['date']}\n📝 {found.get('extra_info','Нет')}"
            else: text = "❌ Не найдена."
        except: text = "❌ /info или /info 3"
    else:
        text = "🌍 <b>Страны:</b>\n\n" + ("\n".join(f"🔢 №{c['number']} — 🏛 {c['name']} | 📅 {c['date']}" for c in countries.values()) if countries else "Нет стран.") + "\n\n💡 /info 1 — подробнее"
    await update.message.reply_html(text)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_banned(update.message.from_user.id): await ban_msg(update); return
    kb = [[InlineKeyboardButton("⚙️ Механика", callback_data="mechanics")],[InlineKeyboardButton("🏛 Основать страну", callback_data="create_country")],[InlineKeyboardButton("📋 Стартовые условия", callback_data="start_conditions")],[InlineKeyboardButton("⭐ Отзывы", callback_data="reviews_menu")],[InlineKeyboardButton("📞 Поддержка", callback_data="support")],[InlineKeyboardButton("📅 Сезон", callback_data="back_to_season")],[InlineKeyboardButton("📋 Команды", callback_data="public_commands")]]
    await update.message.reply_html(f"🍎 <b>Яблочное РП — {season_name}</b>", reply_markup=InlineKeyboardMarkup(kb))

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    await update.message.reply_html(f"👑 <b>ИМПЕРАТОР — {season_name}</b>", reply_markup=admin_commands_keyboard())

async def mod_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in admins_list and update.message.from_user.id != ADMIN_ID: return
    await update.message.reply_html("🛡 <b>Модератор</b>", reply_markup=mod_commands_keyboard())

async def maper_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in maper_ids: return
    await update.message.reply_html("🗺 <b>Мапер</b>", reply_markup=maper_menu_keyboard())

async def addadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    try: admins_list.add(int(context.args[0])); save_json(ADMINS_FILE, list(admins_list)); await update.message.reply_text("✅ Добавлен!")
    except: await update.message.reply_text("❌ /addadmin ID")

async def tempban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in admins_list and update.message.from_user.id != ADMIN_ID: return
    try: banned_users.add(int(context.args[0])); save_json(BANNED_FILE, list(banned_users)); await update.message.reply_text("🚫 Забанен!")
    except: await update.message.reply_text("❌ /tempban ID")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global season_archived, all_users, banned_users, admin_log
    q = update.callback_query; await q.answer()
    uid = q.from_user.id
    if is_banned(uid): await ban_msg(update); return
    if q.data.startswith("survey_"): await survey_handler(update, context); return

    d = q.data
    if d == "enter_rp": await q.edit_message_text("🤖 <b>Проверка</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Я не бот", callback_data="verify_human")],[InlineKeyboardButton("🔙", callback_data="back_to_start")]]), parse_mode="HTML")
    elif d == "verify_human": await q.edit_message_text("🎉 <b>Готово!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🍏 Чат РП", url=CHAT_LINK)],[InlineKeyboardButton("🔙 Меню", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "back_to_start": await q.edit_message_text(f"🍎 <b>{season_name}</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 Меню", callback_data="back_to_menu")],[InlineKeyboardButton("🍏 Вход", callback_data="enter_rp")],[InlineKeyboardButton("📖 О игре", callback_data="about_game")],[InlineKeyboardButton("🆘 Помощь", callback_data="help_menu")]]), parse_mode="HTML")
    elif d == "about_game": await q.edit_message_text("🍎 <b>Лучшее РП!</b>\n👑 ИМПЕРАТОР создал мир.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_start")]]), parse_mode="HTML")
    elif d == "help_menu": await q.edit_message_text(f"🆘 1. Вход\n2. Механика\n3. Страну\n👑 {SUPPORT_USERNAME}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_start")]]), parse_mode="HTML")
    elif d == "mechanics":
        text = load_mechanics()
        if len(text) > 4000:
            for i in range(0, len(text), 4000): await context.bot.send_message(chat_id=uid, text=text[i:i+4000], parse_mode="HTML")
            await q.edit_message_text("📖 Механика отправлена частями.", parse_mode="HTML")
        else: await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "create_country":
        if season_archived: await q.edit_message_text("📦 Архив.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_menu")]])); return
        if str(uid) in countries: await q.edit_message_text("⚠️ Уже есть страна!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑 Удалить", callback_data="delete_country")],[InlineKeyboardButton("🔙", callback_data="back_to_menu")]])); return
        await q.edit_message_text("🏛 Готов?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏁 Начать", callback_data="start_create")],[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "delete_country":
        if str(uid) in countries: await q.edit_message_text(f"⚠️ Удалить «{countries[str(uid)]['name']}»?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Да", callback_data="confirm_delete")],[InlineKeyboardButton("🔙 Нет", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "confirm_delete":
        sid = str(uid)
        if sid in countries:
            name = countries[sid]["name"]; del countries[sid]; save_json(COUNTRIES_FILE, countries)
            if sid in resources_data: del resources_data[sid]; save_json(RESOURCES_FILE, resources_data)
            admin_log.append({"action":"delete","user":sid,"name":name,"time":datetime.now().strftime("%d.%m.%Y %H:%M")}); save_json(ADMIN_LOG_FILE, admin_log)
            for aid in [ADMIN_ID]+list(admins_list)+list(maper_ids):
                try: await context.bot.send_message(chat_id=aid, text=f"🗑 «{name}» удалена.")
                except: pass
            await q.edit_message_text("✅ Удалена!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏛 Новая", callback_data="create_country")],[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "start_conditions": await q.edit_message_text(load_start_conditions(), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "support": await q.edit_message_text(f"📞 {SUPPORT_USERNAME}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "public_commands": await q.edit_message_text("/start /menu /stata /info", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "reviews_menu":
        avg = sum(r["rating"] for r in reviews.values() if "rating" in r) / max(len([r for r in reviews.values() if "rating" in r]), 1)
        await q.edit_message_text(f"⭐ Средняя: <b>{avg:.2f}</b>", reply_markup=reviews_menu_keyboard(), parse_mode="HTML")
    elif d == "read_reviews":
        text = "📋 <b>Отзывы:</b>\n\n" + "\n".join(f"👤 @{r['username']} {'⭐'*r.get('rating',0)}\n💬 {r['review']}\n📅 {r['date']}\n{'─'*20}" for r in reviews.values()) if reviews else "Нет отзывов."
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✍️ Написать", callback_data="write_review")],[InlineKeyboardButton("🔙", callback_data="reviews_menu")]]), parse_mode="HTML")
    elif d == "back_to_menu":
        kb = [[InlineKeyboardButton("⚙️ Механика", callback_data="mechanics")],[InlineKeyboardButton("🏛 Основать страну", callback_data="create_country")],[InlineKeyboardButton("📋 Стартовые условия", callback_data="start_conditions")],[InlineKeyboardButton("⭐ Отзывы", callback_data="reviews_menu")],[InlineKeyboardButton("📞 Поддержка", callback_data="support")],[InlineKeyboardButton("📅 Сезон", callback_data="back_to_season")],[InlineKeyboardButton("📋 Команды", callback_data="public_commands")]]
        await q.edit_message_text(f"🍎 <b>{season_name}</b>", reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    elif d == "back_to_season": await q.edit_message_text(f"📅 <b>{season_name}</b>", reply_markup=season_menu() if not season_archived else InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "my_resources":
        sid = str(uid)
        text = f"🪨 <b>Ресурсы:</b>\n\n" + "\n".join(f"• {r}" for r in resources_data.get(sid, [])) if sid in resources_data else "Нет ресурсов."
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_season")]]), parse_mode="HTML")
    elif d == "my_country":
        sid = str(uid)
        if sid in countries:
            c = countries[sid]
            text = f"🏛 <b>{c['name']}</b>\n🔢 №{c['number']}\n📅 {c['date']}\n🪨 " + ", ".join(resources_data.get(sid, []))
        else: text = "❌ Нет страны."
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✏️ Изменить", callback_data="edit_country")],[InlineKeyboardButton("🔙", callback_data="back_to_season")]]), parse_mode="HTML")
    elif d == "edit_country": await q.edit_message_text("✏️ Что?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏛 Название", callback_data="edit_name")],[InlineKeyboardButton("🏴 Флаг", callback_data="edit_flag")],[InlineKeyboardButton("🔙", callback_data="my_country")]]), parse_mode="HTML"); return EDIT_COUNTRY
    elif d == "other_resources":
        text = "🌍 <b>Ресурсы других:</b>\n\n" + "\n".join(f"🏛 {countries.get(uid,{}).get('name','?')}: {', '.join(res)}" for uid, res in resources_data.items() if uid != str(uid))
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_season")]]), parse_mode="HTML")
    elif d == "stata_countries": await q.edit_message_text("🌍 " + "\n".join(f"🏛 {c['name']} | 📅 {c['date']}" for c in countries.values()) if countries else "Нет.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="stata_back")]]), parse_mode="HTML")
    elif d == "stata_seasons": await q.edit_message_text("📅 Сезон 1 (1200)\nСезон 2 (1991)\nСезон 3 (2008)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="stata_back")]]), parse_mode="HTML")
    elif d == "stata_help": await q.edit_message_text("🆘 /start → меню\nКарта в «map»\n👑 ИМПЕРАТОР", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="stata_back")]]), parse_mode="HTML")
    elif d == "stata_back": await q.edit_message_text("🍎 <b>Я бот РП!</b>", reply_markup=stata_keyboard(), parse_mode="HTML")
    elif d == "admin_menu":
        if uid != ADMIN_ID: return
        await q.edit_message_text(f"👑 <b>ИМПЕРАТОР</b>", reply_markup=admin_commands_keyboard(), parse_mode="HTML")
    elif d == "admin_resources":
        if uid != ADMIN_ID: return
        text = "🪨 <b>Ресурсы:</b>\n\n" + "\n\n".join(f"🏛 {countries.get(u,{}).get('name','?')}\n" + "\n".join(f"• {r}" for r in res) for u, res in resources_data.items()) if resources_data else "Нет."
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_all_countries":
        if uid != ADMIN_ID: return
        await q.edit_message_text("🌍 " + "\n".join(f"🏛 {c['name']} | @{c['username']} | ID:{u}" for u, c in countries.items()) if countries else "Нет.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_broadcast_start":
        if uid != ADMIN_ID: return
        await q.edit_message_text("📢 Напиши сообщение.\n/cancel", parse_mode="HTML"); return ADMIN_BROADCAST
    elif d == "admin_broadcast_yes":
        if uid != ADMIN_ID: return
        msg = context.user_data.get("broadcast_msg",""); users = list(all_users.keys()); total = len(users); success = 0
        sm = await q.edit_message_text(f"📢 0/{total}...")
        for i, u in enumerate(users):
            try: await context.bot.send_message(chat_id=int(u), text=f"📢 <b>ИМПЕРАТОР:</b>\n\n{msg}", parse_mode="HTML"); success += 1
            except: pass
            if (i+1)%10==0: await sm.edit_text(f"📢 {success}/{total}...")
            await asyncio.sleep(0.3)
        await sm.edit_text(f"✅ {success}\n❌ {total-success}"); context.user_data.clear(); return ConversationHandler.END
    elif d == "admin_broadcast_no": await q.edit_message_text("❌ Отменено."); context.user_data.clear(); return ConversationHandler.END
    elif d == "admin_archive_menu":
        if uid != ADMIN_ID: return
        await q.edit_message_text(f"📦 Архив", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📥 Архивировать", callback_data="admin_archive_season")],[InlineKeyboardButton("📂 Смотреть", callback_data="admin_view_archive")],[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_archive_season":
        if uid != ADMIN_ID: return
        season_archived = True
        archive["seasons"] = archive.get("seasons",{})
        archive["seasons"][str(season_number)] = {"season":season_number,"name":season_name,"countries":countries.copy(),"resources":resources_data.copy(),"users":len(all_users),"archived_at":datetime.now().strftime("%d.%m.%Y %H:%M")}
        archive["season_3_archived"] = True; save_json(ARCHIVE_FILE, archive)
        await q.edit_message_text(f"✅ Архив!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_view_archive":
        if uid != ADMIN_ID: return
        text = "📂 " + "\n".join(f"Сезон {sn}: {sd.get('name','')}" for sn, sd in archive.get("seasons",{}).items()) if archive.get("seasons") else "Пусто."
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_archive_menu")]]), parse_mode="HTML")
    elif d == "admin_users":
        if uid != ADMIN_ID: return
        await q.edit_message_text(f"👥 {len(all_users)}\n" + "\n".join(f"• @{d['username']} | ID:{u}" for u, d in list(all_users.items())[:30]), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_stats":
        if uid != ADMIN_ID: return
        await q.edit_message_text(f"📊 👥{len(all_users)} 🏛{len(countries)} ⏳{len(pending_countries)} ⭐{len(reviews)} 🚫{len(banned_users)}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_banlist":
        if uid != ADMIN_ID: return
        text = "🚫 " + "\n".join(f"• @{all_users.get(str(u),{}).get('username',u)}" for u in banned_users) if banned_users else "Пусто."
        kb = [[InlineKeyboardButton(f"🔓 Разбанить {u}", callback_data=f"unban_{u}")] for u in list(banned_users)[:10]] + [[InlineKeyboardButton("🔙", callback_data="admin_menu")]]
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    elif d.startswith("unban_"):
        if uid != ADMIN_ID: return
        u = int(d.split("_")[1]); banned_users.discard(u); save_json(BANNED_FILE, list(banned_users))
        await q.edit_message_text(f"✅ {u} разбанен!"); await context.bot.send_message(chat_id=u, text="✅ Помилован!", parse_mode="HTML")
    elif d == "admin_control":
        if uid != ADMIN_ID: return
        text = "👥 " + "\n".join(f"• @{all_users.get(str(a),{}).get('username',a)}" for a in admins_list)
        kb = [[InlineKeyboardButton(f"❌ Снять {a}", callback_data=f"remove_admin_{a}")] for a in admins_list] + [[InlineKeyboardButton("🔙", callback_data="admin_menu")]]
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    elif d.startswith("remove_admin_"):
        if uid != ADMIN_ID: return
        a = int(d.replace("remove_admin_","")); admins_list.discard(a); save_json(ADMINS_FILE, list(admins_list))
        await q.edit_message_text(f"✅ Снят!")
    elif d == "admin_maper_status":
        if uid != ADMIN_ID: return
        text = "🗺 Ожидают:\n" + ("\n".join(f"• {d['name']}" for d in maper_orders.values()) or "Нет") + "\n\nГотово:\n" + ("\n".join(f"• {d['name']} ✅" for d in maper_done.values()) or "Нет")
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_surveys":
        if uid != ADMIN_ID: return
        counts = {}; [counts.update({v: counts.get(v,0)+1}) for v in user_surveys.values()]
        await q.edit_message_text("📊 " + "\n".join(f"• {k}: {v}" for k,v in counts.items()) if counts else "Нет.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_all_commands":
        if uid != ADMIN_ID: return
        await q.edit_message_text("👤 /start /menu /stata /info\n🛡 /adm\n🗺 /map\n👑 /admin /addadmin", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_close": await q.edit_message_text("Закрыто.")
    elif d == "maper_menu":
        if uid not in maper_ids: return
        await q.edit_message_text("🗺 <b>Мапер</b>", reply_markup=maper_menu_keyboard(), parse_mode="HTML")
    elif d == "maper_new_orders":
        if uid not in maper_ids: return
        text = "📋 " + "\n".join(f"🏛 {d['name']} | @{d['username']}" for d in maper_orders.values()) if maper_orders else "Нет."
        kb = [[InlineKeyboardButton(f"🖌 Беру: {d['name']}", callback_data=f"maper_start_{o}")] for o, d in maper_orders.items()] + [[InlineKeyboardButton("🔙", callback_data="maper_menu")]]
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    elif d.startswith("maper_start_"):
        if uid not in maper_ids: return
        oid = d.replace("maper_start_","")
        if oid in maper_orders:
            data = maper_orders.pop(oid); maper_done[oid] = data; maper_done[oid]["done_at"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            save_json(MAPER_ORDERS_FILE, maper_orders); save_json(MAPER_DONE_FILE, maper_done)
            await q.edit_message_text(f"✅ «{data['name']}» готово!")
            try: await context.bot.send_message(chat_id=int(oid), text=f"🗺 «{data['name']}» на карте!", parse_mode="HTML")
            except: pass
    elif d == "maper_done_orders":
        if uid not in maper_ids: return
        await q.edit_message_text("✅ " + "\n".join(f"🏛 {d['name']}" for d in maper_done.values()) if maper_done else "Нет.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="maper_menu")]]), parse_mode="HTML")
    elif d == "maper_countries":
        if uid not in maper_ids: return
        await q.edit_message_text("🌍 " + "\n".join(f"🏛 {c['name']} | @{c['username']}" for c in countries.values()) if countries else "Нет.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="maper_menu")]]), parse_mode="HTML")
    elif d == "maper_banlist":
        if uid not in maper_ids: return
        await q.edit_message_text("🚫 " + "\n".join(f"• @{all_users.get(str(u),{}).get('username',u)}" for u in banned_users) if banned_users else "Пусто.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="maper_menu")]]), parse_mode="HTML")
    elif d == "maper_close": await q.edit_message_text("Закрыто.")
    elif d == "mod_menu":
        if uid not in

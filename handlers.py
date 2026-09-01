import asyncio
import random
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

NAME, SPAWN, GOV, CONFIRM_GOV, RELIGION, CONFIRM_RELIGION, ATHEISM_MODE, CAPITAL, ETHNICITY, FLAG, CURRENCY, CURRENCY_RATE, EXTRA, CONFIRM, CHANGE_MENU, CHANGE_NAME, CHANGE_SPAWN, CHANGE_GOV, CHANGE_RELIGION, CHANGE_CAPITAL, CHANGE_ETHNICITY, CHANGE_FLAG, CHANGE_CURRENCY, CHANGE_EXTRA = range(24)
REVIEW_WRITE, REVIEW_RATING = 99, 100
ADMIN_BROADCAST = 200
ADMIN_BROADCAST_CONFIRM = 201
EDIT_COUNTRY, EDIT_NAME, EDIT_FLAG = 300, 301, 302
ANKETER_ADD = 400

GOV_TYPES = [
    "Абсолютная монархия", "Конституционная монархия", "Парламентская республика",
    "Президентская республика", "Полупрезидентская республика", "Теократия",
    "Диктатура", "Военная диктатура", "Олигархия", "Демократия",
    "Унитарное государство", "Федерация", "Конфедерация"
]

RELIGIONS = ["Христианство", "Ислам", "Буддизм", "Индуизм", "Иудаизм"]

ATHEISM_MODES = [
    "Светское государство — религия отделена от государства, но не запрещена",
    "Государственный атеизм — религия запрещена, как в СССР",
    "Антирелигиозная политика — активная борьба с религиозными организациями"
]

REJECT_REASONS = {
    "1": "📏 Слишком большой спавн. Уменьши территорию.",
    "2": "📛 Название не подходит. Выбери другое.",
    "3": "💩 Это не страна, а бред. Переделай нормально.",
    "4": "🏙 Столица не подходит. Укажи реальный город.",
    "5": "💱 Валюта не подходит. Придумай другую или напиши «авто».",
    "6": "🕌 Религия не подходит. Выбери из списка.",
    "7": "👥 Народ не указан или написан бред. Напиши нормально.",
    "8": "🏴 Флаг не подходит. Загрузи нормальное изображение.",
    "9": "🗺 Страна не существует или написана с ошибкой. Проверь название."
}

TOKEN = ""
CHAT_LINK = "https://t.me/applerp1"
SUPPORT_USERNAME = ""
ADMIN_ID = 0
REVIEW_CHAT_ID = 0
BOOST_LINK = ""
INVITE_LINK = ""
ALL_RESOURCES = []

season_number = 8
season_name = "Сезон 8 (2022)"
country_counter = {}
countries = {}
pending_countries = {}
all_users = {}
banned_users = set()
admins_list = set()
anketers = set()
maper_ids = set()
maper_id = None
maper_orders = {}
maper_done = {}
season_archived = False
admin_log = []
user_surveys = {}
bot_answers = {}

COUNTRIES_FILE = ""
PENDING_FILE = ""
RESOURCES_FILE = ""
ARCHIVE_FILE = ""
REVIEWS_FILE = ""
USERS_FILE = ""
BANNED_FILE = ""
ADMINS_FILE = ""
ANKETERS_FILE = ""
MAPER_FILE = ""
MAPER_ORDERS_FILE = ""
MAPER_DONE_FILE = ""
ADMIN_LOG_FILE = ""
SURVEYS_FILE = ""

reviews = {}
resources_data = {}
archive = {}

def load_json(filename): return {}
def save_json(filename, data): pass
def load_txt(filename): return []
def load_txt_full(filename): return ""
def load_mechanics(): return ""
def load_start_conditions(): return ""
def load_government(): return ""
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
        [InlineKeyboardButton("📋 Анкетчики", callback_data="admin_anketers")],
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

def gov_keyboard():
    kb = [[InlineKeyboardButton(g, callback_data=f"govpick_{g}")] for g in GOV_TYPES]
    kb.append([InlineKeyboardButton("ℹ️ Информация о госстроях", callback_data="gov_info")])
    return InlineKeyboardMarkup(kb)

def religion_keyboard():
    kb = [[InlineKeyboardButton(r, callback_data=f"relpick_{r}")] for r in RELIGIONS]
    kb.append([InlineKeyboardButton("🚫 Без религии", callback_data="relpick_atheism")])
    return InlineKeyboardMarkup(kb)

def atheism_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton(m, callback_data=f"atheism_{i}")] for i, m in enumerate(ATHEISM_MODES)])

def reject_keyboard(uid):
    return InlineKeyboardMarkup([[InlineKeyboardButton(reason, callback_data=f"reject_{uid}_{code}")] for code, reason in REJECT_REASONS.items()] + [[InlineKeyboardButton("🔙 Отмена", callback_data=f"cancel_reject_{uid}")]])

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
        if user_id not in user_surveys: context.job_queue.run_once(send_survey, 3600, chat_id=uid)
    text = (
        "🍎 <b>Яблочное РП</b>\n\n"
        "Если ты в РП впервые — переходи по ссылке:\n🔗 https://t.me/applerp1\n\n"
        "Если уже в РП — напиши /menu"
    )
    kb = [
        [InlineKeyboardButton("🍏 Вступить в РП", url="https://t.me/applerp1")],
        [InlineKeyboardButton("📋 Меню", callback_data="back_to_menu")]
    ]
    await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(kb))

async def send_survey(context: ContextTypes.DEFAULT_TYPE):
    try:
        kb = [
            [InlineKeyboardButton("📱 ТикТок", callback_data="survey_tiktok")],
            [InlineKeyboardButton("🎬 YouTube", callback_data="survey_youtube")],
            [InlineKeyboardButton("👥 Друг", callback_data="survey_friend")],
            [InlineKeyboardButton("📢 Реклама", callback_data="survey_ad")],
            [InlineKeyboardButton("💬 Другое", callback_data="survey_other")]
        ]
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
    await update.message.reply_html("🍎 Я бот Яблочного РП!", reply_markup=stata_keyboard())

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_banned(update.message.from_user.id): await ban_msg(update); return
    args = context.args
    if args:
        try:
            num = int(args[0])
            found = None; found_uid = None
            for u, c in countries.items():
                if c.get("number") == num: found = c; found_uid = u; break
            if found:
                text = f"🏛 №{found['number']}\n📛 {found['name']}\n👤 @{found['username']}\n📅 {found['date']}\n🏛 {found.get('gov','?')}\n🕌 {found.get('religion','?')}\n🏙 {found.get('capital','?')}\n👥 {found.get('ethnicity','?')}\n💱 {found.get('currency','?')}"
                await update.message.reply_html(text)
                if found_uid in resources_data: await update.message.reply_html("🪨\n" + "\n".join(f"• {r}" for r in resources_data[found_uid]))
                if found.get("spawn_photo"): await context.bot.send_photo(chat_id=update.message.chat_id, photo=found["spawn_photo"], caption="🗺 Спавн")
                if found.get("flag_photo"): await context.bot.send_photo(chat_id=update.message.chat_id, photo=found["flag_photo"], caption="🏴 Флаг")
            else: await update.message.reply_html("❌ Не найдена.")
        except: await update.message.reply_html("❌ /info 1")
    else:
        text = "🌍\n" + ("\n".join(f"🔢 №{c['number']} — 🏛 {c['name']}" for c in countries.values()) if countries else "Нет.") + "\n💡 /info 1"
        await update.message.reply_html(text)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_banned(update.message.from_user.id): await ban_msg(update); return
    kb = [
        [InlineKeyboardButton("⚙️ Механика", callback_data="mechanics")],
        [InlineKeyboardButton("🏛 Основать страну", callback_data="create_country")],
        [InlineKeyboardButton("📋 Стартовые условия", callback_data="start_conditions")],
        [InlineKeyboardButton("⭐ Отзывы", callback_data="reviews_menu")],
        [InlineKeyboardButton("📞 Поддержка", callback_data="support")],
        [InlineKeyboardButton("📅 Сезон", callback_data="back_to_season")],
        [InlineKeyboardButton("📋 Команды", callback_data="public_commands")]
    ]
    await update.message.reply_html(f"🍎 {season_name}", reply_markup=InlineKeyboardMarkup(kb))

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    await update.message.reply_html(f"👑 ИМПЕРАТОР — {season_name}", reply_markup=admin_commands_keyboard())

async def mod_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in admins_list and update.message.from_user.id != ADMIN_ID: return
    await update.message.reply_html("🛡 Модератор", reply_markup=mod_commands_keyboard())

async def maper_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in maper_ids: return
    await update.message.reply_html("🗺 Мапер", reply_markup=maper_menu_keyboard())

async def addadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    try: admins_list.add(int(context.args[0])); save_json(ADMINS_FILE, list(admins_list)); await update.message.reply_text("✅")
    except: await update.message.reply_text("❌ /addadmin ID")

async def tempban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in admins_list and update.message.from_user.id != ADMIN_ID: return
    try: banned_users.add(int(context.args[0])); save_json(BANNED_FILE, list(banned_users)); await update.message.reply_text("🚫")
    except: await update.message.reply_text("❌ /tempban ID")

async def chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if not update.message.reply_to_message: return
    text = update.message.text.lower()
    for keywords, responses in bot_answers.items():
        for kw in keywords.split("|"):
            if kw.strip() and kw.strip() in text:
                try: await update.message.reply_html(random.choice(responses))
                except: pass
                return

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global season_archived, all_users, banned_users, admin_log, anketers
    q = update.callback_query; await q.answer()
    uid = q.from_user.id
    if is_banned(uid): await ban_msg(update); return
    if q.data.startswith("survey_"): await survey_handler(update, context); return

    d = q.data
    if d == "enter_rp": await q.edit_message_text("🤖 Проверка", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Я не бот", callback_data="verify_human")],[InlineKeyboardButton("🔙", callback_data="back_to_start")]]), parse_mode="HTML")
    elif d == "verify_human": await q.edit_message_text("🎉 Готово!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🍏 Чат РП", url=CHAT_LINK)],[InlineKeyboardButton("🔙 Меню", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "back_to_start": await q.edit_message_text(f"🍎 {season_name}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 Меню", callback_data="back_to_menu")],[InlineKeyboardButton("🍏 Вход", callback_data="enter_rp")],[InlineKeyboardButton("📖 О игре", callback_data="about_game")],[InlineKeyboardButton("🆘 Помощь", callback_data="help_menu")]]), parse_mode="HTML")
    elif d == "about_game": await q.edit_message_text("🍎 Лучшее РП!\n👑 ИМПЕРАТОР создал мир.\n📅 2022 год.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_start")]]), parse_mode="HTML")
    elif d == "help_menu": await q.edit_message_text(f"🆘 1. Вход\n2. Механика\n3. Страну\n👑 {SUPPORT_USERNAME}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_start")]]), parse_mode="HTML")
    elif d == "mechanics":
        text = load_mechanics()
        if len(text) > 4000:
            for i in range(0, len(text), 4000): await context.bot.send_message(chat_id=uid, text=text[i:i+4000], parse_mode="HTML")
            await q.edit_message_text("📖 Отправлена.", parse_mode="HTML")
        else: await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "create_country":
        if season_archived: await q.edit_message_text("📦 Архив.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML"); return
        if str(uid) in countries: await q.edit_message_text("⚠️ Уже есть страна!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑 Удалить", callback_data="delete_country")],[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML"); return
        await q.edit_message_text("🏛 Готов?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏁 Начать", callback_data="start_create")],[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "delete_country":
        if str(uid) in countries: await q.edit_message_text(f"⚠️ Удалить «{countries[str(uid)]['name']}»?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Да", callback_data="confirm_delete")],[InlineKeyboardButton("🔙 Нет", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "confirm_delete":
        sid = str(uid)
        if sid in countries:
            name = countries[sid]["name"]; del countries[sid]; save_json(COUNTRIES_FILE, countries)
            if sid in resources_data: del resources_data[sid]; save_json(RESOURCES_FILE, resources_data)
            for aid in [ADMIN_ID]+list(admins_list)+list(maper_ids):
                try: await context.bot.send_message(chat_id=aid, text=f"🗑 «{name}» удалена.")
                except: pass
            await q.edit_message_text("✅ Удалена!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏛 Новая", callback_data="create_country")],[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "start_conditions": await q.edit_message_text(load_start_conditions(), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "support": await q.edit_message_text(f"📞 {SUPPORT_USERNAME}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "public_commands": await q.edit_message_text("/start /menu /stata /info", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "gov_info": await q.edit_message_text(load_government(), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="gov_back")]]), parse_mode="HTML")
    elif d == "reviews_menu":
        avg = sum(r["rating"] for r in reviews.values() if "rating" in r) / max(len([r for r in reviews.values() if "rating" in r]), 1)
        await q.edit_message_text(f"⭐ {avg:.2f}", reply_markup=reviews_menu_keyboard(), parse_mode="HTML")
    elif d == "read_reviews":
        text = "📋\n" + "\n".join(f"👤 @{r['username']} {'⭐'*r.get('rating',0)}\n💬 {r['review']}\n📅 {r['date']}\n" for r in reviews.values()) if reviews else "Нет."
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✍️", callback_data="write_review")],[InlineKeyboardButton("🔙", callback_data="reviews_menu")]]), parse_mode="HTML")
    elif d == "back_to_menu":
        kb = [[InlineKeyboardButton("⚙️ Механика", callback_data="mechanics")],[InlineKeyboardButton("🏛 Основать страну", callback_data="create_country")],[InlineKeyboardButton("📋 Стартовые условия", callback_data="start_conditions")],[InlineKeyboardButton("⭐ Отзывы", callback_data="reviews_menu")],[InlineKeyboardButton("📞 Поддержка", callback_data="support")],[InlineKeyboardButton("📅 Сезон", callback_data="back_to_season")],[InlineKeyboardButton("📋 Команды", callback_data="public_commands")]]
        await q.edit_message_text(f"🍎 {season_name}", reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    elif d == "back_to_season": await q.edit_message_text(f"📅 {season_name}", reply_markup=season_menu() if not season_archived else InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    elif d == "my_resources":
        sid = str(uid)
        text = "🪨\n" + "\n".join(f"• {r}" for r in resources_data.get(sid, [])) if sid in resources_data else "Нет."
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_season")]]), parse_mode="HTML")
    elif d == "my_country":
        sid = str(uid)
        if sid in countries:
            c = countries[sid]
            text = f"🏛 {c['name']}\n🔢 №{c['number']}\n📅 {c['date']}\n🏛 {c.get('gov','?')}\n🕌 {c.get('religion','?')}\n🏙 {c.get('capital','?')}\n👥 {c.get('ethnicity','?')}\n💱 {c.get('currency','?')}\n🪨 " + ", ".join(resources_data.get(sid, []))
        else: text = "❌ Нет страны."
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✏️", callback_data="edit_country")],[InlineKeyboardButton("🔙", callback_data="back_to_season")]]), parse_mode="HTML")
    elif d == "edit_country": await q.edit_message_text("✏️", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏛 Название", callback_data="edit_name")],[InlineKeyboardButton("🏴 Флаг", callback_data="edit_flag")],[InlineKeyboardButton("🔙", callback_data="my_country")]]), parse_mode="HTML"); return EDIT_COUNTRY
    elif d == "other_resources":
        text = "🌍\n" + "\n".join(f"🏛 {countries.get(u,{}).get('name','?')}: {', '.join(res)}" for u, res in resources_data.items() if u != str(uid))
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_season")]]), parse_mode="HTML")
    elif d == "stata_countries": await q.edit_message_text("🌍 " + "\n".join(f"🏛 {c['name']} | 📅 {c['date']}" for c in countries.values()) if countries else "Нет.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="stata_back")]]), parse_mode="HTML")
    elif d == "stata_seasons": await q.edit_message_text("📅 Сезон 1 (1200)\nСезон 2 (1991)\nСезон 3 (2008)\nСезон 4 (1991)\nСезон 5 (1698)\nСезон 6 (2008)\nСезон 7 (1936)\n🌍 Сезон 8 (2022) — текущий", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="stata_back")]]), parse_mode="HTML")
    elif d == "stata_help": await q.edit_message_text("🆘 /start → меню", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="stata_back")]]), parse_mode="HTML")
    elif d == "stata_back": await q.edit_message_text("🍎", reply_markup=stata_keyboard(), parse_mode="HTML")
    elif d == "admin_menu":
        if uid != ADMIN_ID: return
        await q.edit_message_text("👑", reply_markup=admin_commands_keyboard(), parse_mode="HTML")
    elif d == "admin_resources":
        if uid != ADMIN_ID: return
        text = "🪨\n" + "\n\n".join(f"🏛 {countries.get(u,{}).get('name','?')}\n" + "\n".join(f"• {r}" for r in res) for u, res in resources_data.items()) if resources_data else "Нет."
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_all_countries":
        if uid != ADMIN_ID: return
        text = "🌍\n" + "\n".join(f"🏛 {c['name']} | @{c['username']} | ID:{u}" for u, c in countries.items()) if countries else "Нет."
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_broadcast_start":
        if uid != ADMIN_ID: return
        await q.edit_message_text("📢 Напиши.\n/cancel", parse_mode="HTML"); return ADMIN_BROADCAST
    elif d == "admin_broadcast_yes":
        if uid != ADMIN_ID: return
        msg = context.user_data.get("broadcast_msg",""); users = list(all_users.keys()); total = len(users); success = 0
        sm = await q.edit_message_text(f"📢 0/{total}...")
        for i, u in enumerate(users):
            try: await context.bot.send_message(chat_id=int(u), text=f"📢 ИМПЕРАТОР:\n\n{msg}", parse_mode="HTML"); success += 1
            except: pass
            if (i+1)%10==0: await sm.edit_text(f"📢 {success}/{total}...")
            await asyncio.sleep(0.3)
        await sm.edit_text(f"✅ {success}\n❌ {total-success}"); context.user_data.clear(); return ConversationHandler.END
    elif d == "admin_broadcast_no": await q.edit_message_text("❌"); context.user_data.clear(); return ConversationHandler.END
    elif d == "admin_archive_menu":
        if uid != ADMIN_ID: return
        await q.edit_message_text("📦", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📥", callback_data="admin_archive_season")],[InlineKeyboardButton("📂", callback_data="admin_view_archive")],[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_archive_season":
        if uid != ADMIN_ID: return
        season_archived = True
        archive["seasons"] = archive.get("seasons",{})
        archive["seasons"][str(season_number)] = {"season":season_number,"name":season_name,"countries":countries.copy(),"resources":resources_data.copy(),"users":len(all_users),"archived_at":datetime.now().strftime("%d.%m.%Y %H:%M")}
        archive["season_8_archived"] = True; save_json(ARCHIVE_FILE, archive)
        await q.edit_message_text("✅", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_view_archive":
        if uid != ADMIN_ID: return
        text = "📂 " + "\n".join(f"Сезон {sn}: {sd.get('name','')}" for sn, sd in archive.get("seasons",{}).items()) if archive.get("seasons") else "Пусто."
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_archive_menu")]]), parse_mode="HTML")
    elif d == "admin_users":
        if uid != ADMIN_ID: return
        await q.edit_message_text(f"👥 {len(all_users)}\n" + "\n".join(f"• @{d['username']} | ID:{u}" for u, d in list(all_users.items())[:30]), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_stats":
        if uid != ADMIN_ID: return
        await q.edit_message_text(f"📊 👥{len(all_users)} 🏛{len(countries)} ⏳{len(pending_countries)}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
    elif d == "admin_banlist":
        if uid != ADMIN_ID: return
        text = "🚫 " + "\n".join(f"• @{all_users.get(str(u),{}).get('username',u)}" for u in banned_users) if banned_users else "Пусто."
        kb = [[InlineKeyboardButton(f"🔓 {u}", callback_data=f"unban_{u}")] for u in list(banned_users)[:10]] + [[InlineKeyboardButton("🔙", callback_data="admin_menu")]]
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    elif d.startswith("unban_"):
        if uid != ADMIN_ID: return
        u = int(d.split("_")[1]); banned_users.discard(u); save_json(BANNED_FILE, list(banned_users))
        await q.edit_message_text(f"✅ {u}"); await context.bot.send_message(chat_id=u, text="✅ Помилован!", parse_mode="HTML")
    elif d == "admin_control":
        if uid != ADMIN_ID: return
        text = "👥 " + "\n".join(f"• @{all_users.get(str(a),{}).get('username',a)}" for a in admins_list)
        kb = [[InlineKeyboardButton(f"❌ {a}", callback_data=f"remove_admin_{a}")] for a in admins_list] + [[InlineKeyboardButton("🔙", callback_data="admin_menu")]]
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    elif d.startswith("remove_admin_"):
        if uid != ADMIN_ID: return
        a = int(d.replace("remove_admin_","")); admins_list.discard(a); save_json(ADMINS_FILE, list(admins_list))
        await q.edit_message_text("✅")
    elif d == "admin_anketers":
        if uid != ADMIN_ID: return
        text = "📋 Анкетчики:\n\n" + "\n".join(f"• @{all_users.get(str(a),{}).get('username',a)} | ID:{a}" for a in anketers) if anketers else "Нет."
        kb = [[InlineKeyboardButton("➕ Добавить", callback_data="anketer_add")]]
        kb += [[InlineKeyboardButton(f"❌ {a}", callback_data=f"anketer_remove_{a}")] for a in anketers]
        kb.append([InlineKeyboardButton("🔙", callback_data="admin_menu")])
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    elif d == "anketer_add":
        if uid != ADMIN_ID: return
        await q.edit_message_text("📋 Отправь ID:", parse_mode="HTML"); return ANKETER_ADD
    elif d.startswith("anketer_remove_"):
        if uid != ADMIN_ID: return
        a = int(d.replace("anketer_remove_",""))
        await q.edit_message_text(f"⚠️ Убрать {a}?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Да", callback_data=f"anketer_confirm_remove_{a}")],[InlineKeyboardButton("❌ Нет", callback_data="admin_anketers")]]), parse_mode="HTML")
    elif d.startswith("anketer_confirm_remove_"):
        if uid != ADMIN_ID: return
        a = int(d.replace("anketer_confirm_remove_",""))
        anketers.discard(a); save_json(ANKETERS_FILE, list(anketers))
        await q.edit_message_text(f"✅ {a} убран!")
    elif d == "admin_maper_status":
        if uid != ADMIN_ID: return
        await q.edit_message_text("🗺 Ожидают:\n" + ("\n".join(f"• {d['name']}" for d in maper_orders.values()) or "Нет") + "\n\nГотово:\n" + ("\n".join(f"• {d['name']} ✅" for d in maper_done.values()) or "Нет"), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="admin_menu")]]), parse_mode="HTML")
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
        await q.edit_message_text("🗺", reply_markup=maper_menu_keyboard(), parse_mode="HTML")
    elif d == "maper_new_orders":
        if uid not in maper_ids: return
        text = "📋 " + "\n".join(f"🏛 {d['name']} | @{d['username']}" for d in maper_orders.values()) if maper_orders else "Нет."
        kb = [[InlineKeyboardButton(f"🖌 {d['name']}", callback_data=f"maper_start_{o}")] for o, d in maper_orders.items()] + [[InlineKeyboardButton("🔙", callback_data="maper_menu")]]
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    elif d.startswith("maper_start_"):
        if uid not in maper_ids: return
        oid = d.replace("maper_start_","")
        if oid in maper_orders:
            data = maper_orders.pop(oid); maper_done[oid] = data; maper_done[oid]["done_at"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            save_json(MAPER_ORDERS_FILE, maper_orders); save_json(MAPER_DONE_FILE, maper_done)
            await q.edit_message_text(f"✅ {data['name']}")
            try: await context.bot.send_message(chat_id=int(oid), text=f"🗺 {data['name']} на карте!", parse_mode="HTML")
            except: pass
    elif d == "maper_done_orders":
        if uid not in maper_ids: return
        await q.edit_message_text("✅ " + "\n".join(f"🏛 {d['name']}" for d in maper_done.values()) if maper_done else "Нет.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="maper_menu")]]), parse_mode="HTML")
    elif d == "maper_countries":
        if uid not in maper_ids: return
        if not countries: await q.edit_message_text("🌍 Нет.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="maper_menu")]]), parse_mode="HTML")
        else:
            kb = [[InlineKeyboardButton(f"🏛 {c['name']}", callback_data=f"maper_view_{u}")] for u, c in countries.items()] + [[InlineKeyboardButton("🔙", callback_data="maper_menu")]]
            await q.edit_message_text("🌍", reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    elif d.startswith("maper_view_"):
        if uid not in maper_ids: return
        u = d.replace("maper_view_","")
        if u in countries:
            c = countries[u]
            text = f"🏛 {c['name']}\n👤 @{c['username']}\n📅 {c['date']}\n🏛 {c.get('gov','?')}\n🕌 {c.get('religion','?')}\n🏙 {c.get('capital','?')}\n💱 {c.get('currency','?')}"
            await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="maper_countries")]]), parse_mode="HTML")
            if c.get("spawn_photo"): await context.bot.send_photo(chat_id=uid, photo=c["spawn_photo"], caption="🗺 Спавн")
            if c.get("flag_photo"): await context.bot.send_photo(chat_id=uid, photo=c["flag_photo"], caption="🏴 Флаг")
    elif d == "maper_banlist":
        if uid not in maper_ids: return
        await q.edit_message_text("🚫 " + "\n".join(f"• @{all_users.get(str(u),{}).get('username',u)}" for u in banned_users) if banned_users else "Пусто.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="maper_menu")]]), parse_mode="HTML")
    elif d == "maper_close": await q.edit_message_text("Закрыто.")
    elif d == "mod_menu":
        if uid not in admins_list: return
        await q.edit_message_text("🛡", reply_markup=mod_commands_keyboard(), parse_mode="HTML")
    elif d == "mod_pending":
        if uid not in admins_list: return
        text = "📋 " + "\n".join(f"🏛 {d['name']} | @{d['username']}" for d in pending_countries.values()) if pending_countries else "Нет."
        kb = [[InlineKeyboardButton(f"🏛 {d['name']}", callback_data=f"mod_view_{u}")] for u, d in pending_countries.items()] + [[InlineKeyboardButton("🔙", callback_data="mod_menu")]]
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    elif d.startswith("mod_view_"):
        if uid not in admins_list: return
        u = d.replace("mod_view_","")
        if u in pending_countries:
            data = pending_countries[u]
            text = f"📋 {data['name']}\n👤 @{data['username']}\n🏛 {data.get('gov','?')}\n🕌 {data.get('religion','?')}\n🏙 {data.get('capital','?')}\n💱 {data.get('currency','?')}"
            await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅", callback_data=f"approve_{u}"),InlineKeyboardButton("❌", callback_data=f"reject_menu_{u}")]]), parse_mode="HTML")
            if data.get("spawn_photo"): await context.bot.send_photo(chat_id=uid, photo=data["spawn_photo"], caption="🗺")
            if data.get("flag_photo"): await context.bot.send_photo(chat_id=uid, photo=data["flag_photo"], caption="🏴")
    elif d == "mod_countries":
        if uid not in admins_list: return
        await q.edit_message_text("🌍 " + "\n".join(f"🏛 {c['name']} | @{c['username']} | №{c['number']}" for c in countries.values()) if countries else "Нет.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="mod_menu")]]), parse_mode="HTML")
    elif d == "mod_stats":
        if uid not in admins_list: return
        await q.edit_message_text(f"📊 👥{len(all_users)} 🏛{len(countries)}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="mod_menu")]]), parse_mode="HTML")
    elif d == "mod_tempban":
        if uid not in admins_list: return
        await q.edit_message_text("⚠️ /tempban ID", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="mod_menu")]]), parse_mode="HTML")
    elif d == "mod_banlist":
        if uid not in admins_list: return
        await q.edit_message_text("🚫 " + "\n".join(f"• @{all_users.get(str(u),{}).get('username',u)}" for u in banned_users) if banned_users else "Пусто.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="mod_menu")]]), parse_mode="HTML")
    elif d == "mod_close": await q.edit_message_text("Закрыто.")

async def anketer_add_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global anketers
    if update.message.from_user.id != ADMIN_ID: return ConversationHandler.END
    try:
        new_id = int(update.message.text)
        anketers.add(new_id); save_json(ANKETERS_FILE, list(anketers))
        await update.message.reply_text(f"✅ {new_id} добавлен!")
    except: await update.message.reply_text("❌ Неверный ID")
    return ConversationHandler.END

async def edit_name_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("🏛 Новое название:", parse_mode="HTML"); return EDIT_NAME

async def edit_name_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sid = str(update.message.from_user.id)
    if sid in countries:
        countries[sid]["name"] = update.message.text; save_json(COUNTRIES_FILE, countries)
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"✏️ «{update.message.text}»")
    await update.message.reply_html("✅", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_menu")]])); return ConversationHandler.END

async def edit_flag_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("🏴 Новый флаг:", parse_mode="HTML"); return EDIT_FLAG

async def edit_flag_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html("✅", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_to_menu")]])); return ConversationHandler.END

async def write_review_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("✍️ Напиши отзыв:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="reviews_menu")]]), parse_mode="HTML"); return REVIEW_WRITE

async def review_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["review_text"] = update.message.text
    await update.message.reply_html("⭐ Оцени:", reply_markup=rating_keyboard()); return REVIEW_RATING

async def review_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    r = int(q.data.split("_")[1]); u = q.from_user; n = datetime.now().strftime("%d.%m.%Y %H:%M")
    reviews[str(u.id)] = {"username": u.username or f"user_{u.id}", "review": context.user_data.get("review_text",""), "rating": r, "date": n}
    save_json(REVIEWS_FILE, reviews)
    await q.edit_message_text(f"🌟 {'⭐'*r}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋", callback_data="read_reviews")],[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]), parse_mode="HTML")
    context.user_data.clear(); return ConversationHandler.END

async def cancel_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("⭐", reply_markup=reviews_menu_keyboard(), parse_mode="HTML"); return ConversationHandler.END

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.chat_member or not update.chat_member.new_chat_member: return
    nm = update.chat_member.new_chat_member
    if nm.status == "member" and not nm.user.is_bot:
        welcomes = load_txt("welcome_chat.txt")
        try: await context.bot.send_message(chat_id=update.chat_member.chat.id, text=random.choice(welcomes) if welcomes else "👑", parse_mode="HTML")
        except: pass

async def member_banned(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.chat_member or not update.chat_member.new_chat_member: return
    nm = update.chat_member.new_chat_member
    if nm.status == "kicked" and not nm.user.is_bot:
        banned_users.add(nm.user.id); save_json(BANNED_FILE, list(banned_users))

async def start_create_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if season_archived: await update.callback_query.edit_message_text("📦 Сезон в архиве"); return ConversationHandler.END
    await update.callback_query.edit_message_text("🏛 Шаг 1/8: Напиши название своей страны:", parse_mode="HTML"); return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["country_name"] = update.message.text
    await update.message.reply_html(
        "🗺 <b>Шаг 2/8:</b> Скинь спавн своей страны.\n\n"
        "<i>Если сезон Вирт — опиши территорию или отправь фото/карту.\n"
        "Если сезон Реал — напиши название страны, за которую играешь.</i>"
    )
    return SPAWN

async def get_spawn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["spawn_photo"] = update.message.photo[-1].file_id
        context.user_data["spawn_text"] = "(фото)"
    elif update.message.text:
        context.user_data["spawn_text"] = update.message.text
        context.user_data["spawn_photo"] = None
    else:
        await update.message.reply_html("❌ Отправь название страны или фото/карту!")
        return SPAWN
    await update.message.reply_html("🏛 <b>Шаг 3/8:</b> Выбери государственный строй:", reply_markup=gov_keyboard())
    return GOV

async def gov_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data["gov"] = q.data.replace("govpick_","")
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Подтвердить", callback_data="gov_confirm")],
        [InlineKeyboardButton("🔄 Выбрать другой", callback_data="gov_back")],
        [InlineKeyboardButton("ℹ️ Информация", callback_data="gov_info")]
    ])
    await q.edit_message_text(f"🏛 <b>{context.user_data['gov']}</b>", reply_markup=kb, parse_mode="HTML"); return CONFIRM_GOV

async def gov_info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(load_government(), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="gov_back")]]), parse_mode="HTML")
    return CONFIRM_GOV

async def gov_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text("🏛 Шаг 3/8:", reply_markup=gov_keyboard()); return GOV

async def gov_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(f"✅ {context.user_data.get('gov','?')}", parse_mode="HTML")
    await q.message.reply_html("🕌 Шаг 4/8: Выбери религию.\n<i>Основная религия страны.</i>", reply_markup=religion_keyboard())
    return RELIGION

async def rel_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    rel = q.data.replace("relpick_","")
    if rel == "atheism":
        context.user_data["religion"] = "Атеизм"
        await q.edit_message_text("🚫 Без религии.\n<i>Соц. связь ниже.</i>\nВыбери режим:", reply_markup=atheism_keyboard(), parse_mode="HTML")
        return ATHEISM_MODE
    context.user_data["religion"] = rel
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Подтвердить", callback_data="rel_confirm")],
        [InlineKeyboardButton("🔄 Другая", callback_data="rel_back")]
    ])
    await q.edit_message_text(f"🕌 <b>{rel}</b>", reply_markup=kb, parse_mode="HTML"); return CONFIRM_RELIGION

async def atheism_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    idx = int(q.data.replace("atheism_",""))
    context.user_data["religion"] = f"Атеизм ({ATHEISM_MODES[idx]})"
    await q.edit_message_text("✅", parse_mode="HTML")
    await q.message.reply_html("🏙 Шаг 5/8: Напиши столицу:")
    return CAPITAL

async def rel_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(f"✅ {context.user_data.get('religion','?')}", parse_mode="HTML")
    await q.message.reply_html("🏙 Шаг 5/8: Напиши столицу:")
    return CAPITAL

async def rel_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text("🕌 Выбери религию:", reply_markup=religion_keyboard()); return RELIGION

async def get_capital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["capital"] = update.message.text
    await update.message.reply_html("👥 Шаг 6/8: Напиши народ.")
    return ETHNICITY

async def get_ethnicity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ethnicity"] = update.message.text
    await update.message.reply_html("🏴 Шаг 7/8: Отправь флаг (ОБЯЗАТЕЛЬНО):")
    return FLAG

async def get_flag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["flag_photo"] = update.message.photo[-1].file_id
    elif update.message.document:
        context.user_data["flag_photo"] = update.message.document.file_id
    else:
        await update.message.reply_html("❌ Флаг обязателен!")
        return FLAG
    await update.message.reply_html("💱 Шаг 8/8: Напиши валюту.\n<i>Нельзя доллар. «авто» для автовалюты.</i>")
    return CURRENCY

async def get_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cur = update.message.text
    if cur.lower() == "авто":
        context.user_data["currency"] = "Автоматически"
        context.user_data["currency_rate"] = "—"
        await update.message.reply_html("📝 Дополнение или «Пропустить»:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏭ Пропустить", callback_data="skip_extra")]]))
        return EXTRA
    context.user_data["currency"] = cur
    await update.message.reply_html("💱 Курс к доллару (мин 10):")
    return CURRENCY_RATE

async def get_currency_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        rate = float(update.message.text.replace(",", "."))
        if rate < 10:
            await update.message.reply_html("❌ Минимум 10!")
            return CURRENCY_RATE
        context.user_data["currency_rate"] = str(rate)
    except:
        await update.message.reply_html("❌ Напиши число!")
        return CURRENCY_RATE
    await update.message.reply_html("📝 Дополнение или «Пропустить»:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏭ Пропустить", callback_data="skip_extra")]]))
    return EXTRA

async def get_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["extra_info"] = update.message.text if update.message.text else ""
    return await show_summary(update, context)

async def skip_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["extra_info"] = ""
    return await show_summary_callback(update.callback_query, context)

async def show_summary(update, context):
    text = f"📋 Проверь:\n🏛 {context.user_data.get('country_name','?')}\n🗺 {context.user_data.get('spawn_text','?')}\n🏛 {context.user_data.get('gov','?')}\n🕌 {context.user_data.get('religion','?')}\n🏙 {context.user_data.get('capital','?')}\n👥 {context.user_data.get('ethnicity','?')}\n🏴 {'✅' if context.user_data.get('flag_photo') else '❌'}\n💱 {context.user_data.get('currency','?')}"
    kb = [[InlineKeyboardButton("✏️ Исправить", callback_data="change_something")],[InlineKeyboardButton("📨 Отправить", callback_data="submit_to_admin")]]
    await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(kb)); return CONFIRM

async def show_summary_callback(query, context):
    text = f"📋 Проверь:\n🏛 {context.user_data.get('country_name','?')}\n🗺 {context.user_data.get('spawn_text','?')}\n🏛 {context.user_data.get('gov','?')}\n🕌 {context.user_data.get('religion','?')}\n🏙 {context.user_data.get('capital','?')}\n👥 {context.user_data.get('ethnicity','?')}\n🏴 {'✅' if context.user_data.get('flag_photo') else '❌'}\n💱 {context.user_data.get('currency','?')}"
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✏️", callback_data="change_something")],[InlineKeyboardButton("📨", callback_data="submit_to_admin")]]), parse_mode="HTML"); return CONFIRM

async def change_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("✏️ Что исправить?", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🏛 Название", callback_data="change_name")],
        [InlineKeyboardButton("🗺 Страна", callback_data="change_spawn")],
        [InlineKeyboardButton("🏛 Госстрой", callback_data="change_gov")],
        [InlineKeyboardButton("🕌 Религия", callback_data="change_religion")],
        [InlineKeyboardButton("🏙 Столица", callback_data="change_capital")],
        [InlineKeyboardButton("👥 Народ", callback_data="change_ethnicity")],
        [InlineKeyboardButton("🏴 Флаг", callback_data="change_flag")],
        [InlineKeyboardButton("💱 Валюта", callback_data="change_currency")],
        [InlineKeyboardButton("✅ ОК", callback_data="submit_to_admin")]
    ]), parse_mode="HTML"); return CHANGE_MENU

async def change_name_start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.callback_query.edit_message_text("🏛 Название:", parse_mode="HTML"); return CHANGE_NAME
async def change_name_done(update: Update, context: ContextTypes.DEFAULT_TYPE): context.user_data["country_name"] = update.message.text; return await show_summary(update, context)
async def change_spawn_start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.callback_query.edit_message_text("🗺 Страна:", parse_mode="HTML"); return CHANGE_SPAWN
async def change_spawn_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["spawn_photo"] = update.message.photo[-1].file_id
        context.user_data["spawn_text"] = "(фото)"
    elif update.message.text:
        context.user_data["spawn_text"] = update.message.text
        context.user_data["spawn_photo"] = None
    return await show_summary(update, context)
async def change_gov_start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.callback_query.edit_message_text("🏛 Госстрой:", reply_markup=gov_keyboard()); return CHANGE_GOV
async def change_gov_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data["gov"] = q.data.replace("govpick_","")
    return await show_summary_callback(q, context)
async def change_religion_start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.callback_query.edit_message_text("🕌 Религия:", reply_markup=religion_keyboard()); return CHANGE_RELIGION
async def change_religion_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    rel = q.data.replace("relpick_","")
    if rel == "atheism":
        await q.edit_message_text("🚫 Режим:", reply_markup=atheism_keyboard(), parse_mode="HTML")
        return CHANGE_RELIGION
    context.user_data["religion"] = rel
    return await show_summary_callback(q, context)
async def change_atheism_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    idx = int(q.data.replace("atheism_",""))
    context.user_data["religion"] = f"Атеизм ({ATHEISM_MODES[idx]})"
    return await show_summary_callback(q, context)
async def change_capital_start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.callback_query.edit_message_text("🏙 Столица:", parse_mode="HTML"); return CHANGE_CAPITAL
async def change_capital_done(update: Update, context: ContextTypes.DEFAULT_TYPE): context.user_data["capital"] = update.message.text; return await show_summary(update, context)
async def change_ethnicity_start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.callback_query.edit_message_text("👥 Народ:", parse_mode="HTML"); return CHANGE_ETHNICITY
async def change_ethnicity_done(update: Update, context: ContextTypes.DEFAULT_TYPE): context.user_data["ethnicity"] = update.message.text; return await show_summary(update, context)
async def change_flag_start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.callback_query.edit_message_text("🏴 Флаг:", parse_mode="HTML"); return CHANGE_FLAG
async def change_flag_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo: context.user_data["flag_photo"] = update.message.photo[-1].file_id
    elif update.message.document: context.user_data["flag_photo"] = update.message.document.file_id
    else: await update.message.reply_html("❌ Фото или документ!"); return CHANGE_FLAG
    return await show_summary(update, context)
async def change_currency_start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.callback_query.edit_message_text("💱 Валюта:", parse_mode="HTML"); return CHANGE_CURRENCY
async def change_currency_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["currency"] = update.message.text
    await update.message.reply_html("💱 Курс (мин 10):")
    return CURRENCY_RATE

async def submit_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer(); u = q.from_user
    data = {
        "username": u.username or f"user_{u.id}",
        "name": context.user_data.get("country_name","?"),
        "spawn_text": context.user_data.get("spawn_text",""),
        "spawn_photo": context.user_data.get("spawn_photo"),
        "gov": context.user_data.get("gov","Не указан"),
        "religion": context.user_data.get("religion","Не указана"),
        "capital": context.user_data.get("capital","Не указана"),
        "ethnicity": context.user_data.get("ethnicity","Не указан"),
        "flag_photo": context.user_data.get("flag_photo"),
        "currency": context.user_data.get("currency","Не указана"),
        "currency_rate": context.user_data.get("currency_rate","—"),
        "extra_info": context.user_data.get("extra_info",""),
        "date": datetime.now().strftime("%d.%m.%Y %H:%M")
    }
    pending_countries[str(u.id)] = data; save_json(PENDING_FILE, pending_countries)
    await q.edit_message_text("📨 Анкета отправлена!", parse_mode="HTML")

    if ADMIN_ID:
        try:
            admin_text = f"📢 НОВАЯ ЗАЯВКА\n👤 @{u.username}\n🏛 {data['name']}\n🗺 {data['spawn_text']}\n🏛 {data['gov']}\n🕌 {data['religion']}\n🏙 {data['capital']}\n👥 {data['ethnicity']}\n💱 {data['currency']} ({data['currency_rate']})\n📝 {data['extra_info'] or 'Нет'}"
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅", callback_data=f"approve_{u.id}"),InlineKeyboardButton("❌", callback_data=f"reject_menu_{u.id}")]]), parse_mode="HTML")
            if data.get("spawn_photo"): await context.bot.send_photo(chat_id=ADMIN_ID, photo=data["spawn_photo"], caption="🗺 Спавн")
            if data.get("flag_photo"): await context.bot.send_photo(chat_id=ADMIN_ID, photo=data["flag_photo"], caption="🏴 Флаг")
        except: pass

    for ank_id in anketers:
        try:
            await context.bot.send_message(chat_id=ank_id, text=f"📢 Заявка\n👤 @{u.username}\n🏛 {data['name']}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅", callback_data=f"approve_{u.id}"),InlineKeyboardButton("❌", callback_data=f"reject_menu_{u.id}")]]), parse_mode="HTML")
            if data.get("spawn_photo"): await context.bot.send_photo(chat_id=ank_id, photo=data["spawn_photo"], caption="🗺 Спавн")
            if data.get("flag_photo"): await context.bot.send_photo(chat_id=ank_id, photo=data["flag_photo"], caption="🏴 Флаг")
        except: pass

    context.user_data.clear(); return ConversationHandler.END

async def cancel_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query: await update.callback_query.edit_message_text("❌ Отменено.")
    else: await update.message.reply_html("❌ Отменено.")
    context.user_data.clear(); return ConversationHandler.END

async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global country_counter, admin_log
    q = update.callback_query; await q.answer(); uq = q.from_user.id
    if uq != ADMIN_ID and uq not in admins_list and uq not in anketers: return
    uid = q.data.split("_")[1]
    if uid not in pending_countries: await q.edit_message_text("❌ Не найдена."); return
    data = pending_countries.pop(uid); save_json(PENDING_FILE, pending_countries)
    country_counter[8] = country_counter.get(8,0) + 1; cn = country_counter[8]; now = datetime.now().strftime("%d.%m.%Y %H:%M")
    countries[uid] = {
        "name": data["name"], "number": cn, "username": data["username"], "date": now,
        "gov": data.get("gov",""), "religion": data.get("religion",""),
        "capital": data.get("capital",""), "ethnicity": data.get("ethnicity",""),
        "currency": data.get("currency",""), "currency_rate": data.get("currency_rate","—"),
        "spawn_photo": data.get("spawn_photo"), "flag_photo": data.get("flag_photo"),
        "extra_info": data.get("extra_info","")
    }
    save_json(COUNTRIES_FILE, countries)
    res = get_random_resources(); resources_data[uid] = res; save_json(RESOURCES_FILE, resources_data)
    admin_log.append({"action":"approve","admin":str(uq),"user":uid,"name":data["name"],"time":now}); save_json(ADMIN_LOG_FILE, admin_log)
    await q.edit_message_text(f"✅ {data['name']} (№{cn})\n🪨 {', '.join(res)}", parse_mode="HTML")
    try: await context.bot.send_message(chat_id=int(uid), text=f"🎉 {data['name']} создана!\n🔢 №{cn}\n🪨\n" + "\n".join(f"• {r}" for r in res), parse_mode="HTML")
    except: pass
    if maper_ids:
        maper_orders[uid] = data; maper_orders[uid]["date"] = now
        save_json(MAPER_ORDERS_FILE, maper_orders)
        for mid in maper_ids:
            try:
                await context.bot.send_message(chat_id=mid, text=f"🗺 Новая работа!\n🏛 {data['name']}\n👤 @{data['username']}\nНажми /map", parse_mode="HTML")
                if data.get("spawn_photo"): await context.bot.send_photo(chat_id=mid, photo=data["spawn_photo"], caption="🗺 Спавн")
                if data.get("flag_photo"): await context.bot.send_photo(chat_id=mid, photo=data["flag_photo"], caption="🏴 Флаг")
            except: pass
    if uq != ADMIN_ID: await context.bot.send_message(chat_id=ADMIN_ID, text=f"✅ @{q.from_user.username} одобрил «{data['name']}»")
    if REVIEW_CHAT_ID: await context.bot.send_message(chat_id=REVIEW_CHAT_ID, text=f"🎉 {data['name']} — новая страна!\n👤 @{data['username']}\n🔢 №{cn}", parse_mode="HTML")

async def admin_reject_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.from_user.id != ADMIN_ID and q.from_user.id not in admins_list and q.from_user.id not in anketers: return
    uid = q.data.split("_")[2]
    await q.edit_message_text("❌ Причина:", reply_markup=reject_keyboard(uid), parse_mode="HTML")

async def admin_reject_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global admin_log
    q = update.callback_query; await q.answer(); uq = q.from_user.id
    if uq != ADMIN_ID and uq not in admins_list and uq not in anketers: return
    parts = q.data.split("_"); uid = parts[1]; rc = parts[2]
    rt = REJECT_REASONS.get(rc, "Неизвестная причина")
    if uid in pending_countries:
        data = pending_countries.pop(uid); save_json(PENDING_FILE, pending_countries)
        admin_log.append({"action":"reject","admin":str(uq),"user":uid,"name":data["name"],"reason":rc,"time":datetime.now().strftime("%d.%m.%Y %H:%M")}); save_json(ADMIN_LOG_FILE, admin_log)
    await q.edit_message_text(f"❌ {rt}", parse_mode="HTML")
    try: await context.bot.send_message(chat_id=int(uid), text=f"❌ Отказано.\n{rt}", parse_mode="HTML")
    except: pass
    if uq != ADMIN_ID: await context.bot.send_message(chat_id=ADMIN_ID, text=f"❌ @{q.from_user.username} отклонил ({rt})")

async def admin_cancel_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer(); uid = q.data.split("_")[2]
    if uid in pending_countries:
        data = pending_countries[uid]
        await q.edit_message_text(f"📢 @{data['username']}\n🏛 {data['name']}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅", callback_data=f"approve_{uid}"),InlineKeyboardButton("❌", callback_data=f"reject_menu_{uid}")]]), parse_mode="HTML")

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return ConversationHandler.END
    msg = update.message.text; context.user_data["broadcast_msg"] = msg
    await update.message.reply_text(f"📢 Отправить {len(all_users)}?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Да", callback_data="admin_broadcast_yes")],[InlineKeyboardButton("❌ Нет", callback_data="admin_broadcast_no")]]), parse_mode="HTML")
    return ADMIN_BROADCAST_CONFIRM

async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("❌ Отменено."); context.user_data.clear(); return ConversationHandler.END

async def periodic_promo_personal(context: ContextTypes.DEFAULT_TYPE):
    lines = load_txt("promo_personal.txt") + load_txt("promo_donate.txt")
    if not lines: return
    msg = random.choice(lines)
    for uid in all_users:
        try: await context.bot.send_message(chat_id=int(uid), text=msg, parse_mode="HTML"); await asyncio.sleep(0.3)
        except: pass

async def periodic_promo_chat(context: ContextTypes.DEFAULT_TYPE):
    if not REVIEW_CHAT_ID: return
    lines = load_txt("promo_chat.txt") + [d+" | gift" for d in load_txt("promo_donate.txt")]
    if not lines: return
    chosen = random.choice(lines)
    text, btn = chosen.rsplit(" | ", 1) if " | " in chosen else (chosen, "review")
    btn = btn.strip()
    kb = [[InlineKeyboardButton("✍️ Отзыв", url=f"https://t.me/{context.bot.username}?start=review")]] if btn=="review" else [[InlineKeyboardButton("🔗 Чат", url=INVITE_LINK)]] if btn=="invite" else [[InlineKeyboardButton("⭐ Голос", url=BOOST_LINK)]] if btn=="boost" else [[InlineKeyboardButton("🎁 Подарок", url=f"https://t.me/{SUPPORT_USERNAME.replace('@','')}")]]
    try: await context.bot.send_message(chat_id=REVIEW_CHAT_ID, text=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    except: pass

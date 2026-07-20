import asyncio
import random
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

ADMIN_BROADCAST = 200
ADMIN_BROADCAST_CONFIRM = 201

async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers import countries, pending_countries, resources_data, country_counter, admin_log
    from handlers import maper_orders, maper_ids
    from handlers import ADMIN_ID, REVIEW_CHAT_ID
    from handlers import save_json, get_random_resources
    from handlers import COUNTRIES_FILE, PENDING_FILE, RESOURCES_FILE, MAPER_ORDERS_FILE, ADMIN_LOG_FILE

    q = update.callback_query; await q.answer()
    uq = q.from_user.id
    if uq != ADMIN_ID and uq not in admins_list: return

    uid = q.data.split("_")[1]
    if uid not in pending_countries: await q.edit_message_text("❌ Не найдена."); return

    data = pending_countries.pop(uid)
    save_json(PENDING_FILE, pending_countries)

    country_counter[3] = country_counter.get(3, 0) + 1
    cn = country_counter[3]
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    countries[uid] = {
        "name": data["name"],
        "number": cn,
        "username": data["username"],
        "date": now,
        "extra_info": data.get("extra_info", "")
    }
    save_json(COUNTRIES_FILE, countries)

    res = get_random_resources()
    resources_data[uid] = res
    save_json(RESOURCES_FILE, resources_data)

    admin_log.append({
        "action": "approve",
        "admin": str(uq),
        "user": uid,
        "name": data["name"],
        "time": now
    })
    save_json(ADMIN_LOG_FILE, admin_log)

    await q.edit_message_text(
        f"✅ <b>{data['name']}</b> одобрена! (№{cn})\n\n🪨 Ресурсы: {', '.join(res)}",
        parse_mode="HTML"
    )

    try:
        await context.bot.send_message(
            chat_id=int(uid),
            text=f"🎉 <b>Поздравляем!</b>\n\nТвоя страна «{data['name']}» создана!\n🔢 Номер: {cn}\n\n🪨 Ресурсы:\n" + "\n".join(f"• {r}" for r in res),
            parse_mode="HTML"
        )
    except: pass

    if maper_ids:
        maper_orders[uid] = {
            "name": data["name"],
            "username": data["username"],
            "spawn_text": data.get("spawn_text", ""),
            "spawn_photo": data.get("spawn_photo"),
            "flag_photo": data.get("flag_photo"),
            "extra_info": data.get("extra_info", ""),
            "date": now
        }
        save_json(MAPER_ORDERS_FILE, maper_orders)
        for mid in maper_ids:
            try:
                await context.bot.send_message(chat_id=mid, text=f"🗺 <b>Новая работа!</b>\n\n🏛 {data['name']}\n👤 @{data['username']}\nНажми /map", parse_mode="HTML")
                if data.get("spawn_photo"): await context.bot.send_photo(chat_id=mid, photo=data["spawn_photo"], caption="🗺 Спавн")
                elif data.get("spawn_text"): await context.bot.send_message(chat_id=mid, text=f"🗺 {data['spawn_text']}")
                if data.get("flag_photo"): await context.bot.send_photo(chat_id=mid, photo=data["flag_photo"], caption="🏴 Флаг")
            except: pass

    if uq != ADMIN_ID:
        try: await context.bot.send_message(chat_id=ADMIN_ID, text=f"✅ Админ @{q.from_user.username} одобрил «{data['name']}»")
        except: pass

    if REVIEW_CHAT_ID:
        try: await context.bot.send_message(chat_id=REVIEW_CHAT_ID, text=f"🎉 <b>{data['name']}</b> — новая страна!\n👤 @{data['username']}\n🔢 №{cn}", parse_mode="HTML")
        except: pass


async def admin_reject_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers import ADMIN_ID, admins_list

    q = update.callback_query; await q.answer()
    if q.from_user.id != ADMIN_ID and q.from_user.id not in admins_list: return

    uid = q.data.split("_")[2]
    keyboard = [
        [InlineKeyboardButton("📏 Слишком большой спавн", callback_data=f"reject_{uid}_1")],
        [InlineKeyboardButton("📛 Не подходит название", callback_data=f"reject_{uid}_2")],
        [InlineKeyboardButton("💩 Это не страна, а бред", callback_data=f"reject_{uid}_3")],
        [InlineKeyboardButton("🔙 Отмена", callback_data=f"cancel_reject_{uid}")]
    ]
    await q.edit_message_text("❌ <b>Выбери причину:</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")


async def admin_reject_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers import pending_countries, admin_log, ADMIN_ID, admins_list
    from handlers import save_json, PENDING_FILE, ADMIN_LOG_FILE

    q = update.callback_query; await q.answer()
    uq = q.from_user.id
    if uq != ADMIN_ID and uq not in admins_list: return

    parts = q.data.split("_")
    uid = parts[1]
    rc = parts[2]

    reasons = {
        "1": "📏 Слишком большой спавн. Уменьши территорию.",
        "2": "📛 Название не подходит. Выбери другое.",
        "3": "💩 Это не страна, а бред и понос. Переделай нормально."
    }

    if uid in pending_countries:
        data = pending_countries.pop(uid)
        save_json(PENDING_FILE, pending_countries)
        admin_log.append({
            "action": "reject",
            "admin": str(uq),
            "user": uid,
            "name": data["name"],
            "reason": rc,
            "time": datetime.now().strftime("%d.%m.%Y %H:%M")
        })
        save_json(ADMIN_LOG_FILE, admin_log)

    rt = reasons.get(rc, "Неизвестная причина")
    await q.edit_message_text(f"❌ Отказано.\n{rt}", parse_mode="HTML")

    try:
        await context.bot.send_message(
            chat_id=int(uid),
            text=f"❌ <b>В создании страны отказано.</b>\n\nПричина: {rt}\n\nИсправь и попробуй снова.",
            parse_mode="HTML"
        )
    except: pass

    if uq != ADMIN_ID:
        try: await context.bot.send_message(chat_id=ADMIN_ID, text=f"❌ Админ @{q.from_user.username} отклонил (причина: {rt})")
        except: pass


async def admin_cancel_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers import pending_countries

    q = update.callback_query; await q.answer()
    uid = q.data.split("_")[2]
    if uid in pending_countries:
        data = pending_countries[uid]
        keyboard = [
            [InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{uid}"),
             InlineKeyboardButton("❌ Отказать", callback_data=f"reject_menu_{uid}")]
        ]
        await q.edit_message_text(
            f"📢 Заявка от @{data['username']}\n🏛 {data['name']}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )


async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers import ADMIN_ID, all_users
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton

    if update.message.from_user.id != ADMIN_ID: return ConversationHandler.END
    msg = update.message.text
    context.user_data["broadcast_msg"] = msg
    await update.message.reply_text(
        f"📢 <b>Предпросмотр:</b>\n\n{msg}\n\nОтправить {len(all_users)} пользователям?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Да", callback_data="admin_broadcast_yes")],
            [InlineKeyboardButton("❌ Нет", callback_data="admin_broadcast_no")]
        ]),
        parse_mode="HTML"
    )
    return ADMIN_BROADCAST_CONFIRM


async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Рассылка отменена.")
    context.user_data.clear()
    return ConversationHandler.END


async def periodic_promo_personal(context: ContextTypes.DEFAULT_TYPE):
    from handlers import load_txt, all_users
    lines = load_txt("promo_personal.txt") + load_txt("promo_donate.txt")
    if not lines: return
    msg = random.choice(lines)
    for uid in all_users:
        try: await context.bot.send_message(chat_id=int(uid), text=msg, parse_mode="HTML"); await asyncio.sleep(0.3)
        except: pass


async def periodic_promo_chat(context: ContextTypes.DEFAULT_TYPE):
    from handlers import REVIEW_CHAT_ID, BOOST_LINK, INVITE_LINK, SUPPORT_USERNAME, load_txt
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton

    if not REVIEW_CHAT_ID: return
    lines = load_txt("promo_chat.txt") + [d + " | gift" for d in load_txt("promo_donate.txt")]
    if not lines: return
    chosen = random.choice(lines)
    text, btn = chosen.rsplit(" | ", 1) if " | " in chosen else (chosen, "review")
    btn = btn.strip()
    kb = [[InlineKeyboardButton("✍️ Отзыв", url=f"https://t.me/{context.bot.username}?start=review")]] if btn == "review" else \
         [[InlineKeyboardButton("🔗 Чат", url=INVITE_LINK)]] if btn == "invite" else \
         [[InlineKeyboardButton("⭐ Голос", url=BOOST_LINK)]] if btn == "boost" else \
         [[InlineKeyboardButton("🎁 Подарок", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")]]
    try: await context.bot.send_message(chat_id=REVIEW_CHAT_ID, text=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    except: pass

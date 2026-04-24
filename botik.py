import json
import os
import random
import re
import logging
import asyncio
import traceback
import requests
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path
import glob

# ========== AIOGRAM ИМПОРТЫ ==========
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    ChatPermissions, FSInputFile
)
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== КОНСТАНТЫ ==========
TOKEN = "8292078558:AAGKdz9_lZ6t-uXkqStchYk2YsHExnVmpCA"
ADMINS = [8470546248, 7248987280, 6418211439, 8300978131]
OWNER_ID = 7248987280
SPECIAL_USER_ID = 5424918085 
MODERATORS = [8186828207, 1319209818, 7683199888, 5626107304]  
SWEET_TOOTH_IDS = [8470546248, 8553136480, 6852129576, 5315371931, 7720525095, 7717551692]

HF_TOKEN = "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"
MODEL_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large" 
headers = {"Authorization": f"Bearer {HF_TOKEN}"}
user_sessions = {}
RAID_REQUESTS = {}  
user_chat_ids = set()
DATA_FILE = "bot_data.json"
USER_DATA_FILE = "user_data.json"
UNION_FILE = "unions.json"
UNION_REQUIREMENT = "#KXD"
EMOJI_LEAVE_ON = '🔔'
EMOJI_LEAVE_OFF = '🔕'
CHANNEL_USERNAME = "@KXDKISS" 
CHANNEL_ID = "@KXDKISS"  
CHANNEL_URL = "https://t.me/KXDKISS"
BAN_DATA_FILE = "ban_data.json"

LIMITED_CANDIES_TOTAL = 2006
LIMITED_CANDY_CHANCE = 0.02
LIMITED_CANDY_PRICE = 50

STARS_RATE = 2
MIN_STARS = 50

REPUTATION_PHOTOS = {
    "user_normal": "reputation_user_normal.jpg",
    "user_100": "reputation_user_100.jpg", 
    "admin_normal": "reputation_admin_normal.jpg",
    "admin_100": "reputation_admin_100.jpg",
    "owner": "reputation_owner.jpg",
    "favorite": "reputation_favorite.jpg",
    "special": "special_reputation_photo.jpg",
    "sweet_tooth": "reputation_sweet_tooth.jpg",
    "snus_eater": "reputation_snus_eater.jpg",
    "old_man": "reputation_old_man.jpg",
    "poop_eater": "reputation_poop_eater.jpg" 
}

COMMAND_TO_USERS = {
    "сладкоежек": ["@Moroz_Fimoz", "@SoplizhuiKXD", "@Tartar520"],
    "адм": ["@olvshkk", "@ttaayyyy", "@Fsubxsgjk", "@ELIKOSSEL", "@snowflake177"],
}

KABAN_FACTS = [
    "Около 90% всех новогодних ёлок в мире выращиваются на специальных фермах...",
    "Традиция дарить подарки на Новый год связана с древнеримским праздником Сатурналий...",
    "проект был создан 8 ферваля. нынешний канал - 12 сентебря"
]

KISS_ACTIONS = {
    'погладь': {'response': 'глажу {username} по голове', 'emoji': '😊💕'},
    'ударь': {'response': '🥊 {username} получил хороший удар по яйцам', 'emoji': '👊'},
    'успокой': {'response': 'успокаиваю колыбельной {username} ...', 'emoji': '💤'},
    'поцелуй': {'response': '*поцеловал в щечку {username}*', 'emoji': '💋'},
    'пни': {'response': 'пнул {username}', 'emoji': '👺'},
    'обними': {'response': 'крепко обнимаю {username}', 'emoji': '🤗💖'},
    'накорми': {'response': 'угощаю {username} вкусняшкой', 'emoji': '🍰🍕'},
    'напои': {'response': 'напоил до вздутия живота {username}.', 'emoji': '🥛'},
    'забань': {'response': 'я не забаню тебя пидорас иди нахуй...', 'emoji': '🤡'}
}

PHONE_PRICES = {"США": 160, "Великобритания": 300, "Украина": 560, "КЗ": 400, "Узбекистан": 120, "Германия": 310}
PHONE_EMOJIS = {"США": "🇺🇸", "Великобритания": "🇬🇧", "Украина": "🇺🇦", "КЗ": "🇵🇼", "Узбекистан": "🇺🇿", "Германия": "🇩🇪"}

VIRTUAL_PRICES = {"Мьянма": 50, "США": 60, "Канада": 70, "Япония": 400, "Индия": 70, "Марокко": 100, "Беларусь": 98, "Мексика": 80, "Ирак": 80, "Израиль": 40}
VIRTUAL_EMOJIS = {"Мьянма": "🇲🇲", "США": "🇺🇸", "Канада": "🇨🇦", "Япония": "🇯🇵", "Индия": "🇮🇳", "Марокко": "🇲🇦", "Беларусь": "🇧🇾", "Мексика": "🇲🇽", "Ирак": "🇮🇶", "Израиль": "🇮🇱"}

GIFT_PRICES = {"Мишка": 25, "Сердце": 25, "Роза": 45, "Подарок": 45, "Торт": 90, "Цветы": 90, "Ракета": 90, "Пиво": 90, "Колечко": 150, "Алмаз": 150, "Кубок": 150}
GIFT_EMOJIS = {"Мишка": "🧸", "Сердце": "💝", "Роза": "🌹", "Подарок": "🎁", "Торт": "🎂", "Цветы": "💐", "Ракета": "🚀", "Пиво": "🍺", "Колечко": "💍", "Алмаз": "💎", "Кубок": "🏆"}

# ========== FSM STATES ==========
class UserStates(StatesGroup):
    awaiting_sliv = State()
    awaiting_raid_request = State()
    awaiting_message_to_admins = State()
    awaiting_coins_amount = State()
    awaiting_stars_amount = State()
    awaiting_stars_recipient = State()
    awaiting_candy_request = State()
    editing_sliv = State()

class AdminStates(StatesGroup):
    replying_to_message = State()

# ========== КЛАСС BOTDATA ==========
class BotData:
    def __init__(self):
        self.data = {
            "SPAM_FILTER": {},
            "USER_DATA": {"join_dates": {}, "activity": {}},
            "UNION_HOUSES": {},
            "GAME_STATS": {},
            "REPUTATION": {},
            "ADMIN_MESSAGES": {},
            "REPUTATION_DATA": {},
            "REMINDERS": {},
            "USER_STATUS": {},
            "CANDIES": {},
            "REP_COOLDOWN": {},
            "CUSTOM_PHOTOS": {},
            "CUSTOM_PHOTOS_FILE_ID": {},
            "CUSTOM_PHRASES": {},
            "DEFAULT_PHRASE": "люблю тебя смирительная рубашка...",
            "LEAVE_NOTIFICATIONS": {},
            "LEAVE_MESSAGES": {},
            "RAID_REQUESTS": {},
            "LIMITED_CANDIES": {},
            "LIMITED_CANDIES_TOTAL_GIVEN": 0,
            "SLIV_STATUS": {},
            "USER_MESSAGES_TO_ADMINS": {},
            "CHANNEL_FOR_POSTS": None,
            "PENDING_CANDY_REQUESTS": {},
        }
        self.load_data()

    def load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.data.update(loaded_data)
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                    self.data["USER_DATA"].update(user_data.get("USER_DATA", {}))
            if os.path.exists(UNION_FILE):
                with open(UNION_FILE, 'r', encoding='utf-8') as f:
                    self.data["UNION_HOUSES"].update(json.load(f))
            if "SLIV_STATUS" not in self.data:
                self.data["SLIV_STATUS"] = {}
            if "PENDING_CANDY_REQUESTS" not in self.data:
                self.data["PENDING_CANDY_REQUESTS"] = {}
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")

    def save_data(self):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump({k: self.data[k] for k in ["SPAM_FILTER", "GAME_STATS", "REPUTATION", 
                "ADMIN_MESSAGES", "REPUTATION_DATA", "REMINDERS", "USER_STATUS", 
                "CANDIES", "REP_COOLDOWN", "CUSTOM_PHOTOS", "CUSTOM_PHOTOS_FILE_ID", 
                "CUSTOM_PHRASES", "DEFAULT_PHRASE", "LEAVE_NOTIFICATIONS", 
                "LEAVE_MESSAGES", "LIMITED_CANDIES", "LIMITED_CANDIES_TOTAL_GIVEN",
                "CHANNEL_FOR_POSTS", "PENDING_CANDY_REQUESTS"]}, f, ensure_ascii=False, indent=2)
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump({"USER_DATA": self.data["USER_DATA"]}, f, ensure_ascii=False, indent=2)
            with open(UNION_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data["UNION_HOUSES"], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")

bot_data = BotData()

# Глобальные переменные
USER_COOLDOWN = {}
FACT_COOLDOWN = {}
KMK_GAMES = {}
GUESS_NUMBER = {}
NOTIFY_LEAVES = {}
REMINDER_JOBS = {}
USER_MESSAGES_TO_ADMINS = {}
ADMIN_REPLIES = {}
ban_data = {"banned": {}, "muted": {}, "banned_users": {}}
user_chat_ids = set() 

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def is_sweet_tooth(user_id: int) -> bool:
    return user_id in SWEET_TOOTH_IDS

def is_admin_or_moderator(user_id: int) -> bool:
    return user_id in ADMINS or user_id in MODERATORS or user_id == OWNER_ID

def get_user_mention(user_id: int, first_name: str = None) -> str:
    if first_name:
        return f'<a href="tg://user?id={user_id}">{first_name}</a>'
    return f'<a href="tg://user?id={user_id}">Пользователь</a>'

def get_username_or_mention(user) -> str:
    if user.username:
        return f"@{user.username}"
    return get_user_mention(user.id, user.first_name)

def format_datetime(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y %H:%M:%S")

def save_ban_data(data: dict):
    try:
        with open(BAN_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения данных о банах: {e}")

def load_ban_data() -> dict:
    try:
        if os.path.exists(BAN_DATA_FILE):
            with open(BAN_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки данных о банах: {e}")
    return {"banned": {}, "muted": {}, "banned_users": {}}

def parse_time(time_str: str) -> Optional[timedelta]:
    try:
        time_str = time_str.lower().strip()
        total_seconds = 0
        
        # Дни
        days_match = re.search(r'(\d+)\s*[дd]', time_str)
        if days_match:
            total_seconds += int(days_match.group(1)) * 86400
            time_str = time_str.replace(days_match.group(0), '')
        
        # Часы
        hours_match = re.search(r'(\d+)\s*[чh]', time_str)
        if hours_match:
            total_seconds += int(hours_match.group(1)) * 3600
            time_str = time_str.replace(hours_match.group(0), '')
        
        # Минуты
        minutes_match = re.search(r'(\d+)\s*[мm]', time_str)
        if minutes_match:
            total_seconds += int(minutes_match.group(1)) * 60
            time_str = time_str.replace(minutes_match.group(0), '')
        
        # Секунды
        seconds_match = re.search(r'(\d+)\s*[сc]', time_str)
        if seconds_match:
            total_seconds += int(seconds_match.group(1))
        
        if total_seconds > 0:
            return timedelta(seconds=total_seconds)
        return None
    except Exception as e:
        logger.error(f"Ошибка parse_time: {e}")
        return None

def get_keyboard(chat_type: str = "private"):
    if chat_type != "private":
        return ReplyKeyboardRemove()
    buttons = [
        [KeyboardButton(text="Информация ❓"), KeyboardButton(text="Слить 🔥")],
        [KeyboardButton(text="Факт 😧"), KeyboardButton(text="👀 Материал 👀")],
        [KeyboardButton(text="Заказать рейд 💣"), KeyboardButton(text="КиссШоп 🎄")],
        [KeyboardButton(text="Написать нам 🖋"), KeyboardButton(text="Конфетки 🍬")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def initialize_user_reputation(user_id: int, is_admin: bool = False, is_owner: bool = False):
    user_id_str = str(user_id)
    if user_id_str not in bot_data.data["REPUTATION_DATA"]:
        if is_owner:
            reputation = 100.0
            candies = 9999
            coins = 0
            status = "владелец"
        elif is_admin:
            reputation = 60.0
            candies = 6
            coins = 0
            status = "админ"
        else:
            reputation = 10.0
            candies = 3
            coins = 0
            status = "киссмейт"
        
        bot_data.data["REPUTATION_DATA"][user_id_str] = {
            "reputation": reputation,
            "candies": candies,
            "coins": coins,
            "status": status,
            "original_photo": None
        }
        bot_data.save_data()

def get_reputation_photo(user_id: int, reputation: float, status: str) -> str:
    user_id_str = str(user_id)
    if user_id_str in bot_data.data["CUSTOM_PHOTOS_FILE_ID"]:
        return bot_data.data["CUSTOM_PHOTOS_FILE_ID"][user_id_str]
    if user_id == OWNER_ID:
        return REPUTATION_PHOTOS["owner"]
    if "сладкоежка" in status.lower():
        return REPUTATION_PHOTOS.get("sweet_tooth", REPUTATION_PHOTOS["user_normal"])
    elif "снюсоед" in status.lower():
        return REPUTATION_PHOTOS.get("snus_eater", REPUTATION_PHOTOS["user_normal"])
    elif "старик" in status.lower():
        return REPUTATION_PHOTOS.get("old_man", REPUTATION_PHOTOS["user_normal"])
    elif "говноед" in status.lower() or "говноедик" in status.lower():
        return REPUTATION_PHOTOS.get("poop_eater", REPUTATION_PHOTOS["user_normal"])
    if status in ["админ", "модер", "владелец"]:
        if reputation >= 100.0:
            return REPUTATION_PHOTOS["admin_100"]
        else:
            return REPUTATION_PHOTOS["admin_normal"]
    elif status == "любимчик 🍬":
        return REPUTATION_PHOTOS["favorite"]
    else:
        if reputation >= 100.0:
            return REPUTATION_PHOTOS["user_100"]
        else:
            return REPUTATION_PHOTOS["user_normal"]

def can_change_reputation(changer_id: int, target_id: int) -> bool:
    if changer_id in ADMINS:
        return True
    changer_str = str(changer_id)
    target_str = str(target_id)
    cooldown_key = f"{changer_str}_{target_str}"
    if cooldown_key in bot_data.data["REP_COOLDOWN"]:
        last_change = datetime.fromisoformat(bot_data.data["REP_COOLDOWN"][cooldown_key])
        if datetime.now() - last_change < timedelta(days=3):
            return False
    return True

def update_reputation_cooldown(changer_id: int, target_id: int):
    cooldown_key = f"{changer_id}_{target_id}"
    bot_data.data["REP_COOLDOWN"][cooldown_key] = datetime.now().isoformat()
    bot_data.save_data()

async def send_reminder(bot: Bot, user_id: int, reminder_text: str):
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"🚨 Тик-так!!! самое время {reminder_text}"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки напоминания: {e}")

# ========== ПРОВЕРКА ПОДПИСКИ ==========
async def check_subscription(user_id: int, bot: Bot) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Ошибка проверки подписки для {user_id}: {e}")
        return False

async def show_subscription_required(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перейти в канал 📢", url=CHANNEL_URL)],
        [InlineKeyboardButton(text="Готово ☃", callback_data="check_subscription")]
    ])
    await message.answer(
        "❄ Придется подписаться на наш канальчик\n\n"
        "Так же, рекомендую:\n"
        "@kyxna_kx @kabanNEWSxd @FLOODKXD @calendarXD\n\n"
        "Нажми на кнопку ниже, чтобы подписаться, а после нажми на 'готово ☃'",
        reply_markup=keyboard
    )

async def handle_subscription_check(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    user_id = callback.from_user.id
    
    is_subscribed = await check_subscription(user_id, bot)
    
    if is_subscribed:
        await callback.message.delete()
        await bot.send_message(
            chat_id=user_id,
            text="❄ Отлично! можешь продолжить.\n"
                 "!ПОМНИ : отправлять сливы повторно НЕ надо "
                 "(только если не было никакого ответа в течении 10-ти часов). "
                 "СЛИВ И РЕЙД ЭТО НЕ ОДНО И ТОЖЕ.",
            reply_markup=get_keyboard("private")
        )
    else:
        await callback.message.edit_text(
            text="❌ Ты уверен, что подписался? Попробуй еще раз!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Перейти в канал 📢", url=CHANNEL_URL)],
                [InlineKeyboardButton(text="Проверить снова 🔄", callback_data="check_subscription")]
            ])
        )

# ========== MIDDLEWARE ДЛЯ ПРОВЕРКИ ПОДПИСКИ ==========
async def subscription_middleware(handler, message: Message, bot: Bot):
    try:
        if message.chat.type == "private":
            user_id = message.from_user.id
            if user_id in ADMINS or user_id == OWNER_ID:
                return await handler(message, bot)
            if message.text and message.text.startswith('/start'):
                return await handler(message, bot)
            if not await check_subscription(user_id, bot):
                await show_subscription_required(message)
                return
        return await handler(message, bot)
    except Exception as e:
        logger.error(f"Ошибка в subscription_middleware: {e}")
        return await handler(message, bot)

# ========== MIDDLEWARE ДЛЯ ПРОВЕРКИ БАНА ==========
async def ban_middleware(handler, message: Message, bot: Bot):
    try:
        user_id = str(message.from_user.id)
        banned_users = ban_data.get("banned_users", {})
        
        if user_id in banned_users:
            await message.answer("🚫 Вы забанены в боте и не можете использовать команды.")
            return
        
        return await handler(message, bot)
    except Exception as e:
        logger.error(f"Ошибка в ban_middleware: {e}")
        return await handler(message, bot)

# ========== ОСНОВНАЯ КОМАНДА START ==========
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if message.chat.type == "private":
        if not await check_subscription(user_id, bot):
            await show_subscription_required(message)
            return

    user_chat_ids.add(chat_id)
    
    user_id_str = str(message.from_user.id)
    if user_id_str not in bot_data.data["USER_DATA"]["join_dates"]:
        bot_data.data["USER_DATA"]["join_dates"][user_id_str] = datetime.now().strftime("%d.%m.%Y")
        bot_data.save_data()

    initialize_user_reputation(
        message.from_user.id,
        message.from_user.id in ADMINS,
        message.from_user.id == OWNER_ID
    )
    
    await bot.send_sticker(
        chat_id=message.chat.id,
        sticker="CAACAgIAAxkBAAEQFD5pS9fp8NARJAdUA34jIyZiek1-wwAC8ZkAAv0_UErKSzEcLi40gDYE"
    )
    await message.answer(
        "Привет на 100 лет!",
        reply_markup=get_keyboard(message.chat.type)
    )
# ========== СИСТЕМА БАНОВ В ЛС ==========
async def cmd_ban_user(message: Message, bot: Bot):
    admin_id = message.from_user.id
    
    if admin_id not in ADMINS and admin_id != OWNER_ID:
        await message.answer("❌ У вас нет прав на использование этой команды!")
        return
    
    text = message.text.strip()
    parts = text.split(maxsplit=2)
    
    if len(parts) < 2:
        await message.answer("❌ Формат: /бан @username причина\nПример: /бан @username Спам в чате")
        return
    
    target_username = parts[1]
    reason = parts[2] if len(parts) > 2 else "Не указана"
    
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        target_username = f"@{target_user.username}" if target_user.username else target_user.first_name
        reason = text.replace("/бан", "").strip()
    
    clean_username = target_username.lstrip('@').lower()
    
    target_user_id = None
    target_name = None
    
    for user_id_str, user_data in bot_data.data["REPUTATION_DATA"].items():
        try:
            user_obj = await bot.get_chat(int(user_id_str))
            if user_obj.username and user_obj.username.lower() == clean_username:
                target_user_id = int(user_id_str)
                target_name = user_obj.first_name
                break
        except:
            continue
    
    if not target_user_id:
        await message.answer(f"❌ Не найден пользователь {target_username}")
        return
    
    if target_user_id == OWNER_ID or target_user_id in ADMINS:
        await message.answer("❌ Нельзя забанить администратора или владельца!")
        return
    
    global ban_data
    if "banned_users" not in ban_data:
        ban_data["banned_users"] = {}
    
    ban_data["banned_users"][str(target_user_id)] = {
        "user_id": target_user_id,
        "admin_id": admin_id,
        "reason": reason,
        "timestamp": datetime.now().timestamp(),
        "admin_name": message.from_user.first_name,
        "target_name": target_name
    }
    save_ban_data(ban_data)
    
    await message.answer(
        f"✅ Пользователь {target_username} забанен!\n"
        f"👤 Админ: {message.from_user.first_name}\n"
        f"📝 Причина: {reason}"
    )
    
    try:
        await bot.send_message(
            chat_id=target_user_id,
            text=f"🚫 Вы были забанены в боте!\nПричина: {reason}\nДля разблокировки обратитесь к администрации."
        )
    except:
        pass

async def cmd_unban_user(message: Message, bot: Bot):
    admin_id = message.from_user.id
    
    if admin_id not in ADMINS and admin_id != OWNER_ID:
        await message.answer("❌ У вас нет прав на использование этой команды!")
        return
    
    text = message.text.strip()
    parts = text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer("❌ Формат: /разбан @username")
        return
    
    target_username = parts[1].lstrip('@').lower()
    
    global ban_data
    found = None
    for user_id_str, ban_info in ban_data.get("banned_users", {}).items():
        try:
            user_obj = await bot.get_chat(int(user_id_str))
            if user_obj.username and user_obj.username.lower() == target_username:
                found = user_id_str
                break
        except:
            continue
    
    if found:
        del ban_data["banned_users"][found]
        save_ban_data(ban_data)
        await message.answer(f"✅ Пользователь {target_username} разбанен!")
    else:
        await message.answer(f"❌ Пользователь {target_username} не найден в бане")

async def cmd_banned_list(message: Message):
    admin_id = message.from_user.id
    
    if admin_id not in ADMINS and admin_id != OWNER_ID:
        await message.answer("❌ У вас нет прав на использование этой команды!")
        return
    
    global ban_data
    banned_users = ban_data.get("banned_users", {})
    
    if not banned_users:
        await message.answer("📋 Список забаненных пользователей пуст.")
        return
    
    text = "🚫 **Список забаненных пользователей:**\n\n"
    for user_id_str, ban_info in banned_users.items():
        text += f"• {ban_info.get('target_name', 'Неизвестно')} (ID: {user_id_str})\n"
        text += f"  Причина: {ban_info.get('reason', 'Не указана')}\n"
        text += f"  Забанил: {ban_info.get('admin_name', 'Неизвестно')}\n"
        text += f"  Дата: {format_datetime(ban_info.get('timestamp', 0))}\n\n"
    
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

# ========== КНОПКА "КОНФЕТКИ 🍬" ==========
async def candies_info(message: Message, state: FSMContext, bot: Bot):
    user = message.from_user
    user_id_str = str(user.id)
    
    initialize_user_reputation(user.id, user.id in ADMINS, user.id == OWNER_ID)
    
    rep_data = bot_data.data["REPUTATION_DATA"].get(user_id_str, {})
    candies = rep_data.get("candies", 0)
    limited_candies = bot_data.data["LIMITED_CANDIES"].get(user_id_str, 0)
    
    text = (
        f"🍬 **КОНФЕТКИ В KISSБОТЕ**\n\n"
        f"У вас обычных конфеток: `{candies}`\n"
        f"У вас лимитированных конфеток: `{limited_candies}`\n\n"
        f"**Как получить конфетки?**\n"
        f"• Активность в чате\n"
        f"• Выдача от сладкоежек\n"
        f"• Обмен лимитированных конфет командой `микс`\n\n"
        f"**Что можно сделать с конфетками?**\n"
        f"• Обменять на монетки командой `Лип [число]`\n"
        f"• Передать другому пользователю `конфетка [количество]`\n"
        f"• Купить подарки в КиссШопе\n\n"
        f"**Лимитированные конфеты ({LIMITED_CANDIES_TOTAL} всего)**\n"
        f"• Получить можно только от сладкоежек (шанс {LIMITED_CANDY_CHANCE*100}%)\n"
        f"• 1 лимитированная = 15-60 обычных конфет\n\n"
        f"Нажмите на кнопку ниже, чтобы запросить конфетки у сладкоежек!"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить конфетки ✅", callback_data="request_candies")]
    ])
    
    await message.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

async def handle_candy_request(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user = callback.from_user
    user_id = user.id
    
    last_request = bot_data.data["PENDING_CANDY_REQUESTS"].get(str(user_id), {}).get("timestamp", 0)
    if datetime.now().timestamp() - last_request < 3600:
        remaining = int(3600 - (datetime.now().timestamp() - last_request))
        minutes = remaining // 60
        await callback.answer(f"Подожди {minutes} минут перед следующим запросом!", show_alert=True)
        return
    
    await callback.answer()
    await callback.message.edit_text(
        "📸 **Отправьте скриншот вашей активности в чате**\n\n"
        "Это может быть скриншот ваших сообщений, статистики или любой другой активности.\n"
        "Сладкоежки рассмотрят ваш запрос и решат, сколько конфет выдать.\n\n"
        "Для отмены отправьте 'отмена'",
        parse_mode=ParseMode.MARKDOWN
    )
    
    await state.set_state(UserStates.awaiting_candy_request)
    await state.update_data(original_message_id=callback.message.message_id)

async def process_candy_request(message: Message, state: FSMContext, bot: Bot):
    user = message.from_user
    user_id = user.id
    
    if message.text and message.text.lower() == "отмена":
        await state.clear()
        await message.answer("❌ Запрос на получение конфет отменен.")
        return
    
    if not message.photo:
        await message.answer("❌ Пожалуйста, отправьте фото (скриншот)!")
        return
    
    initialize_user_reputation(user.id, user.id in ADMINS, user.id == OWNER_ID)
    rep_data = bot_data.data["REPUTATION_DATA"].get(str(user.id), {})
    reputation = rep_data.get("reputation", 0)
    
    request_id = str(uuid.uuid4())[:8]
    
    bot_data.data["PENDING_CANDY_REQUESTS"][str(user_id)] = {
        "request_id": request_id,
        "user_id": user_id,
        "username": user.username or user.first_name,
        "first_name": user.first_name,
        "reputation": reputation,
        "photo_file_id": message.photo[-1].file_id,
        "timestamp": datetime.now().timestamp(),
        "status": "pending",
        "message_id": message.message_id,
        "chat_id": message.chat.id
    }
    bot_data.save_data()
    
    user_link = f"@{user.username}" if user.username else user.first_name
    
    admin_message = (
        f"🍬 **НОВЫЙ ЗАПРОС НА КОНФЕТЫ**\n\n"
        f"👤 Юз: {user_link}\n"
        f"🆔 ID: `{user_id}`\n"
        f"📊 Репутация: {reputation:.1f}%\n"
        f"🆔 Запрос: `{request_id}`"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1 🍬", callback_data=f"candy_give_1_{request_id}"),
            InlineKeyboardButton(text="2 🍬", callback_data=f"candy_give_2_{request_id}"),
            InlineKeyboardButton(text="3 🍬", callback_data=f"candy_give_3_{request_id}")
        ],
        [
            InlineKeyboardButton(text="4 🍬", callback_data=f"candy_give_4_{request_id}"),
            InlineKeyboardButton(text="5 🍬", callback_data=f"candy_give_5_{request_id}"),
            InlineKeyboardButton(text="❌ Отказать", callback_data=f"candy_reject_{request_id}")
        ]
    ])
    
    for sweet_id in SWEET_TOOTH_IDS:
        try:
            await bot.send_photo(
                chat_id=sweet_id,
                photo=message.photo[-1].file_id,
                caption=admin_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка отправки сладкоежке {sweet_id}: {e}")
    
    await message.answer(
        "✅ **Ваш запрос отправлен сладкоежкам!**\n\n"
        "Ожидайте решения. Вам придет уведомление, когда сладкоежки примут решение.\n"
        "Обычно это занимает до 10 минут.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    data = await state.get_data()
    try:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=data.get("original_message_id"),
            text="🍬 **КОНФЕТКИ В KISSБОТЕ**\n\nВаш запрос отправлен! Ожидайте решения сладкоежек.",
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        pass
    
    await state.clear()

async def handle_candy_admin_response(callback: CallbackQuery, bot: Bot):
    data = callback.data
    sweet_id = callback.from_user.id
    
    if sweet_id not in SWEET_TOOTH_IDS:
        await callback.answer("❌ Только сладкоежки могут выдавать конфеты!", show_alert=True)
        return
    
    await callback.answer()
    
    parts = data.split("_")
    action = parts[1]
    amount = parts[2] if action == "give" else None
    request_id = parts[-1]
    
    pending_requests = bot_data.data["PENDING_CANDY_REQUESTS"]
    target_user_id = None
    request_data = None
    
    for uid, req in pending_requests.items():
        if req.get("request_id") == request_id:
            target_user_id = int(uid)
            request_data = req
            break
    
    if not request_data or request_data.get("status") != "pending":
        await callback.answer("❌ Запрос уже обработан!", show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=None)
        return
    
    sweet_name = callback.from_user.username or callback.from_user.first_name
    
    if action == "reject":
        request_data["status"] = "rejected"
        request_data["admin_id"] = sweet_id
        request_data["admin_name"] = sweet_name
        bot_data.save_data()
        
        try:
            await bot.send_message(
                chat_id=target_user_id,
                text=f"❌ **Вам отказали в выдаче конфет!**\n\nВаш запрос просмотрен, но сладкоежки решили не выдавать конфеты. Попробуйте позже или будьте активнее в чате!",
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            pass
        
        new_caption = callback.message.caption + f"\n\n✅ **Отказал:** @{sweet_name}"
        await callback.message.edit_caption(
            caption=new_caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=None
        )
        
        await callback.message.answer(f"❌ Отказано пользователю {request_data['username']}")
        
    else:
        candies_amount = int(amount)
        
        target_id_str = str(target_user_id)
        initialize_user_reputation(target_user_id, False, False)
        
        current_candies = bot_data.data["REPUTATION_DATA"].get(target_id_str, {}).get("candies", 0)
        bot_data.data["REPUTATION_DATA"][target_id_str]["candies"] = current_candies + candies_amount
        
        request_data["status"] = "processed"
        request_data["candies_given"] = candies_amount
        request_data["admin_id"] = sweet_id
        request_data["admin_name"] = sweet_name
        bot_data.save_data()
        
        try:
            await bot.send_message(
                chat_id=target_user_id,
                text=f"🍬 **Вам выдали конфетки!**\n\n✨ Сладкоежка @{sweet_name} выдал вам `{candies_amount}` конфет!\n\nПродолжайте быть активными в чате!",
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            pass
        
        new_caption = callback.message.caption + f"\n\n✅ **Выдал:** @{sweet_name} | {candies_amount} конфет"
        await callback.message.edit_caption(
            caption=new_caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=None
        )
        
        await callback.message.answer(f"✅ Выдано {candies_amount} конфет пользователю {request_data['username']}")

# ========== ПЕРЕДАЧА КОНФЕТОК (сладкоежки) ==========
async def give_candy(message: Message, bot: Bot):
    try:
        giver = message.from_user
        giver_id = str(giver.id)
        
        is_sweet_tooth_sender = is_sweet_tooth(giver.id)
        
        receiver = None
        receiver_id = None
        
        if message.reply_to_message:
            receiver = message.reply_to_message.from_user
            receiver_id = str(receiver.id)
        elif message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    mentioned_username = message.text[entity.offset:entity.offset + entity.length].lstrip('@')
                    try:
                        receiver_id = mentioned_username
                        receiver = type('User', (), {'id': receiver_id, 'first_name': mentioned_username})()
                    except:
                        await message.answer("❌ Не могу найти пользователя. Используйте ответ на сообщение.")
                        return
                    break
        
        if not receiver:
            await message.answer("❌ Ответьте на сообщение пользователя или укажите @username!")
            return
        
        message_text = message.text.lower()
        amount_match = re.search(r'конфетк[ау]\s*(\d+)', message_text)
        if amount_match:
            amount = int(amount_match.group(1))
        else:
            amount = 1

        if giver_id == receiver_id:
            await message.answer("❌ Нельзя передавать конфетки самому себе!")
            return

        initialize_user_reputation(giver.id, giver.id in ADMINS, giver.id == OWNER_ID)
        initialize_user_reputation(int(receiver_id), False, False)
        
        if amount <= 0:
            await message.answer("❌ Количество должно быть положительным!")
            return

        giver_candies = bot_data.data["REPUTATION_DATA"][giver_id]["candies"]
        if giver_candies < amount:
            await message.answer(f"😯 Ой, кажись у тебя нет столько конфеток! У тебя всего {giver_candies}.")
            return

        limited_given = False
        limited_message = ""
        
        if is_sweet_tooth_sender and random.random() < LIMITED_CANDY_CHANCE:
            if bot_data.data["LIMITED_CANDIES_TOTAL_GIVEN"] < LIMITED_CANDIES_TOTAL:
                if int(receiver_id) not in ADMINS or True:
                    receiver_id_str = str(receiver_id)
                    
                    if receiver_id_str not in bot_data.data["LIMITED_CANDIES"]:
                        bot_data.data["LIMITED_CANDIES"][receiver_id_str] = 0
                    
                    bot_data.data["LIMITED_CANDIES"][receiver_id_str] += 1
                    bot_data.data["LIMITED_CANDIES_TOTAL_GIVEN"] += 1
                    limited_given = True
                    
                    limited_message = (
                        f"\n\n <b>ЛИМИТИРОВАННАЯ КОНФЕТКА</b>\n"
                        f"<i>стоимость: {LIMITED_CANDY_PRICE} обычных конфет</i>"
                    )
                    
                    bot_data.save_data()

        bot_data.data["REPUTATION_DATA"][giver_id]["candies"] -= amount
        bot_data.data["REPUTATION_DATA"][receiver_id]["candies"] += amount
        bot_data.save_data()
        
        receiver_name = f'<a href="tg://user?id={receiver_id}">{receiver.first_name}</a>'
        
        if limited_given:
            final_message = (
                f"{limited_message}\n"
                f"\n<tg-emoji emoji-id=\"5445363209512976767\">🥰</tg-emoji> доверие Передано {amount} конфеток в знак благодарности {receiver_name}."
            )
        else:
            final_message = f"<tg-emoji emoji-id=\"5445363209512976767\">🥰</tg-emoji> Передано {amount} конфеток в знак благодарности {receiver_name}"
        
        await message.answer(final_message, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка в give_candy: {e}")
        await message.answer("❌ Ошибка при передаче конфеток")

# ========== ОБМЕН ЛИМИТИРОВАННОЙ КОНФЕТЫ ==========
async def mix_limited_candy(message: Message, state: FSMContext):
    try:
        user = message.from_user
        user_id_str = str(user.id)
        
        limited_candies = bot_data.data["LIMITED_CANDIES"].get(user_id_str, 0)
        
        if limited_candies <= 0:
            await message.answer("❌ У тебя нет лимитированных конфеток!")
            return
        
        await state.update_data(mixing_user=user_id_str, mixing_limited=1)
        
        text = (
            "⚡ <b>Переводим лимитированную конфетку в ? обычных конфет?</b>\n"
            "<i>учти, что может выпасть любое число, от 15 до 60.</i>"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🎰 Подтвердить", callback_data=f"mix_confirm_{user_id_str}"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="mix_cancel")
            ]
        ])
        
        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Ошибка в mix_limited_candy: {e}")
        await message.answer("❌ Ошибка при попытке обмена")

async def handle_mix_confirmation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    data = callback.data
    
    if data == "mix_cancel":
        await callback.message.edit_text("❌ Обмен лимитированной конфеты отменен")
        return
    
    if data.startswith("mix_confirm_"):
        user_id_str = data.split("_")[2]
        
        if str(callback.from_user.id) != user_id_str:
            await callback.answer("Это не твоя конфетка! 🍫", show_alert=True)
            return
        
        limited_candies = bot_data.data["LIMITED_CANDIES"].get(user_id_str, 0)
        
        if limited_candies <= 0:
            await callback.message.edit_text("❌ У тебя больше нет лимитированных конфеток!")
            return
        
        await callback.message.edit_text("🎰 Миксуем конфетку...")
        await asyncio.sleep(1.5)
        
        candies_amount = random.randint(15, 60)
        
        bot_data.data["LIMITED_CANDIES"][user_id_str] -= 1
        if bot_data.data["LIMITED_CANDIES"][user_id_str] <= 0:
            del bot_data.data["LIMITED_CANDIES"][user_id_str]
        
        if user_id_str not in bot_data.data["REPUTATION_DATA"]:
            initialize_user_reputation(int(user_id_str), False, False)
        
        current_candies = bot_data.data["REPUTATION_DATA"][user_id_str].get("candies", 0)
        bot_data.data["REPUTATION_DATA"][user_id_str]["candies"] = current_candies + candies_amount
        bot_data.save_data()
        
        user_name = callback.from_user.first_name
        
        result_text = (
            f"🎉 <b>Начислил {candies_amount} обычных конфет!</b> 🍫\n\n"
            f"Поздравляю, {user_name}! 🎊\n"
            f"Твоя лимитированная конфетка превратилась в {candies_amount} обычных конфет!"
        )
        
        await callback.message.edit_text(result_text, parse_mode="HTML")

# ========== РЕПУТАЦИЯ ==========
async def show_reputation(message: Message, bot: Bot):
    try:
        target_user = message.from_user
        
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
        
        user_id = target_user.id
        
        if user_id == SPECIAL_USER_ID:
            user_name = f'<a href="tg://user?id={target_user.id}">{target_user.first_name}</a>'
            
            special_text = (
                f"😈РЕПУТАЦИЯ ПОЛЬЗОВАТЕЛЯ🍵 {user_name}\n\n"
                f"🏆 активность: -1938\n"
                f"🥂 доверие: -470.89%\n" 
                f"🐱 статус: ???\n"
                f"🍫 конфеток: (хз)\n\n"
                f"ПТИЧКА СПОЙ ПЕСЕНКУ!😜"
            )
            
            try:
                if os.path.exists(REPUTATION_PHOTOS["special"]):
                    with open(REPUTATION_PHOTOS["special"], 'rb') as photo_file:
                        photo = FSInputFile(REPUTATION_PHOTOS["special"])
                        await message.answer_photo(photo=photo, caption=special_text, parse_mode="HTML")
                else:
                    await message.answer(special_text, parse_mode="HTML")
            except Exception as e:
                logger.error(f"Ошибка отправки специальной анкеты: {e}")
                await message.answer(special_text, parse_mode="HTML")
            return
        
        user_id_str = str(target_user.id)
        user_name = f'<a href="tg://user?id={target_user.id}">{target_user.first_name}</a>'
        
        initialize_user_reputation(
            target_user.id,
            target_user.id in ADMINS,
            target_user.id == OWNER_ID
        )
        
        rep_data = bot_data.data["REPUTATION_DATA"].get(user_id_str, {})
        reputation = rep_data.get("reputation", 10.0)
        candies = rep_data.get("candies", 3)
        status = rep_data.get("status", "киссмейт 🦇")
        activity = bot_data.data["USER_DATA"]["activity"].get(user_id_str, 0)
        limited_candies = bot_data.data["LIMITED_CANDIES"].get(user_id_str, 0)
        
        activity_str = f"{activity}"
        if activity > 1000:
            activity_str = f"{activity/1000:.1f}к".replace('.0к', 'к')
        
        user_phrase = bot_data.data["CUSTOM_PHRASES"].get(user_id_str, bot_data.data["DEFAULT_PHRASE"])

        reputation_text = (
            f"<b><tg-emoji emoji-id=\"5226928895189598791\">🥰</tg-emoji> РЕПУТАЦИЯ ПОЛЬЗОВАТЕЛЯ {user_name}</b>\n\n"
            f"<b><tg-emoji emoji-id=\"5884097155341226387\">🥰</tg-emoji> активность:</b> {activity_str}\n"
            f"<b><tg-emoji emoji-id=\"5217890643321300022\">🥰</tg-emoji> доверие:</b> {reputation:.2f}%\n"
            f"<b><tg-emoji emoji-id=\"5220053623211305785\">🥰</tg-emoji> статус:</b> {status}\n"
            f"<b><tg-emoji emoji-id=\"5445363209512976767\">🥰</tg-emoji> конфеток:</b> {candies}\n"
            f"<b><tg-emoji emoji-id=\"5463071033256848094\">🥰</tg-emoji> ЛИМИТИРОВАННЫЕ КОНФЕТКИ:</b> {limited_candies}\n"
            f"\n<i>{user_phrase}</i>"
        )

        photo = get_reputation_photo(target_user.id, reputation, status)
        photo_sent = False
        
        if photo and isinstance(photo, str):
            if photo.startswith(('CAAC', 'AgAD', 'BQAC')):
                try:
                    await message.answer_photo(photo=photo, caption=reputation_text, parse_mode="HTML")
                    photo_sent = True
                except Exception as e:
                    logger.error(f"Ошибка отправки photo по file_id: {e}")
            
            elif os.path.exists(photo):
                try:
                    photo_file = FSInputFile(photo)
                    await message.answer_photo(photo=photo_file, caption=reputation_text, parse_mode="HTML")
                    photo_sent = True
                except Exception as e:
                    logger.error(f"Ошибка отправки photo как файла: {e}")
        
        if not photo_sent:
            await message.answer(reputation_text, parse_mode="HTML")
            
    except Exception as e:
        logger.error(f"Ошибка в show_reputation: {e}")
        await message.answer("❌ Ошибка при показе репутации")

async def change_reputation(message: Message):
    try:
        changer = message.from_user
        changer_id = changer.id
        is_admin = changer_id in ADMINS
        
        target = None
        target_id = None
        
        if message.reply_to_message:
            target = message.reply_to_message.from_user
            target_id = target.id
        elif message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    mentioned_username = message.text[entity.offset:entity.offset + entity.length].lstrip('@')
                    try:
                        target_id = int(mentioned_username)  
                        target = type('User', (), {'id': target_id, 'first_name': mentioned_username})()
                    except ValueError:
                        await message.answer("❌ Не могу найти пользователя. Используйте ответ на сообщение.")
                        return
                    break
        
        if not target:
            await message.answer("❌ Ответьте на сообщение пользователя или укажите юз")
            return
        
        target_id = target.id
        target_str = str(target_id)
        
        if changer_id == target_id:
            await message.answer("🎄 Еще раз и в глаз")
            return
        
        if target_id == OWNER_ID:
            await message.answer("🐈‍ не,я люблю варусну")
            return
        
        initialize_user_reputation(target_id, target_id in ADMINS, target_id == OWNER_ID)
        
        message_text = message.text.lower()
        action = "increase" if message_text.startswith('+реп') else "decrease"
        
        change_amount = 1.02 if action == "increase" else -1.07
        
        if is_admin:
            percent_match = re.search(r'(\d+[,.]?\d*)%', message_text)
            if percent_match:
                try:
                    custom_amount = float(percent_match.group(1).replace(',', '.'))
                    change_amount = custom_amount if action == "increase" else -custom_amount
                except ValueError:
                    pass
        
        if not is_admin:
            if not can_change_reputation(changer_id, target_id):
                await message.answer("⏳ Подождешь 3 дня? нельзя так часто переобуваться")
                return
        
        current_rep = bot_data.data["REPUTATION_DATA"][target_str]["reputation"]
        new_rep = current_rep + change_amount
        
        if new_rep > 100.0:
            new_rep = 100.0
        elif new_rep < 0.0:
            new_rep = 0.0
        
        bot_data.data["REPUTATION_DATA"][target_str]["reputation"] = new_rep
        bot_data.save_data()
        
        if not is_admin:
            update_reputation_cooldown(changer_id, target_id)
        
        target_name = f'<a href="tg://user?id={target_id}">{target.first_name}</a>'
        
        if action == "increase":
            if is_admin and abs(change_amount) > 5:
                await message.answer(f"✨ Репутация {target_name} повышена на {abs(change_amount):.2f}%!!!", parse_mode="HTML")
            else:
                await message.answer(f"❤️‍🔥 Репутация {target_name} повышена на {abs(change_amount):.2f}%!", parse_mode="HTML")
        else:
            if is_admin and abs(change_amount) > 5:
                await message.answer(f"⚰️ Репутация {target_name} понижена на {abs(change_amount):.2f}% ...", parse_mode="HTML")
            else:
                await message.answer(f"🗿 Репутация {target_name} понижена на {abs(change_amount):.2f}% ...", parse_mode="HTML")
            
    except Exception as e:
        logger.error(f"Ошибка в change_reputation: {e}")
        await message.answer("❌ Ошибка при изменении репутации")

async def show_reputation_top(message: Message, bot: Bot):
    try:
        users_data = []
        for user_id, data in bot_data.data["REPUTATION_DATA"].items():
            try:
                user_obj = await bot.get_chat(int(user_id))
                user_name = user_obj.first_name
                users_data.append({
                    'id': int(user_id),
                    'name': user_name,
                    'reputation': data.get('reputation', 10.0),
                    'status': data.get('status', 'кабанчик')
                })
            except:
                continue
        
        users_data.sort(key=lambda x: x['reputation'], reverse=True)

        respect_users = [u for u in users_data if u['reputation'] >= 70]
        middle_users = [u for u in users_data if 15 <= u['reputation'] < 70]
        low_users = [u for u in users_data if u['reputation'] < 15]
        
        top_text = "🥂 <b>ТОП РЕПУТАЦИИ ПОЛЬЗОВАТЕЛЕЙ</b> 🥂\n_\n\n"
        
        top_text += "<b>КРУТЫЕ:</b>\n"
        for i, user in enumerate(respect_users[:2], 1):
            user_link = f'<a href="tg://user?id={user["id"]}">{user["name"]}</a>'
            top_text += f"{i}. {user_link} : {user['reputation']:.1f}%\n"
        top_text += "___\n\n"
        
        top_text += "<b>СРЕДНЕ:</b>\n"
        for i, user in enumerate(middle_users[:2], 3):
            user_link = f'<a href="tg://user?id={user["id"]}">{user["name"]}</a>'
            top_text += f"{i}. {user_link} : {user['reputation']:.1f}%\n"
        top_text += "_\n\n"
        
        top_text += "<b>НЕДОВЕРИЕ:</b>\n"
        for i, user in enumerate(low_users[:2], 5):
            user_link = f'<a href="tg://user?id={user["id"]}">{user["name"]}</a>'
            top_text += f"{i}. {user_link} : {user['reputation']:.1f}%\n"
        
        await message.answer(top_text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка в show_reputation_top: {e}")
        await message.answer("❌ Ошибка при формировании топа..")
# ========== КИССШОП И НОМЕРА ==========
async def kiss_shop(message: Message, bot: Bot):
    user = message.from_user
    user_id_str = str(user.id)

    initialize_user_reputation(user.id, user.id in ADMINS, user.id == OWNER_ID)
    
    rep_data = bot_data.data["REPUTATION_DATA"].get(user_id_str, {})
    coins = rep_data.get("coins", 0)
    candies = rep_data.get("candies", 0)
    
    text = (
        "🎄 *KISS SHOP*\n\n"
        f"❄ Монетки: {coins}\n"
        f"🍫 Конфетки: {candies}\n\n"
        "Чтобы обменять конфетки в монетки, напишите команду: Лип [число]\n"
        "подробнее в этой [статье](https://teletype.in/@var1sna/kiss-shop)"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="пополнить 🌟", callback_data="buy_coins_start"),
            InlineKeyboardButton(text="📞 Номера", callback_data="phone_numbers_start")
        ],
        [
            InlineKeyboardButton(text="Подарки в ТГ 💝", callback_data="gifts_start"),
            InlineKeyboardButton(text="Звезды 🌟", callback_data="stars_start")
        ]
    ])
    
    await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=keyboard)

# ========== НОМЕРА ТЕЛЕФОНОВ ==========
async def handle_phone_numbers_start(callback: CallbackQuery):
    await callback.answer()
    text = "📲 *Выберите, какой номер хотите приобрести.*"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Физ.", callback_data="phone_physical")],
        [InlineKeyboardButton(text="💻 Вирт.", callback_data="phone_virtual")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_shop")]
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def handle_phone_physical(callback: CallbackQuery):
    await callback.answer()
    text = "🎮 *Отлично! значит берем физ номер.*\n\nСтраны: США, Великобритания, Украина, КЗ"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇸 США (160🪙)", callback_data="country_USA")],
        [InlineKeyboardButton(text="🇬🇧 Великобритания (300🪙)", callback_data="country_UK")],
        [InlineKeyboardButton(text="🇺🇦 Украина (560🪙)", callback_data="country_Ukraine")],
        [InlineKeyboardButton(text="🇵🇼 КЗ (400🪙)", callback_data="country_KZ")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="phone_numbers_start")]
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def handle_phone_virtual_start(callback: CallbackQuery):
    await callback.answer()
    text = "💻 *Отлично! значит берем вирт номер.*\n\nСтраны: Мьянма, США, Канада, Япония, Индия, Марокко"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇲🇲 Мьянма (50🪙)", callback_data="vcountry_Мьянма")],
        [InlineKeyboardButton(text="🇺🇸 США (60🪙)", callback_data="vcountry_США")],
        [InlineKeyboardButton(text="🇨🇦 Канада (70🪙)", callback_data="vcountry_Канада")],
        [InlineKeyboardButton(text="🇯🇵 Япония (400🪙)", callback_data="vcountry_Япония")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="phone_numbers_start")]
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def handle_country_selection(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    country_map = {"USA": "США", "UK": "Великобритания", "Ukraine": "Украина", "KZ": "КЗ"}
    country = country_map.get(callback.data.split("_")[1])
    price = PHONE_PRICES.get(country)
    
    await state.update_data(selected_country=country, selected_price=price, purchase_type="phone")
    
    text = f"🎬 Значит берем физ *{country}*\n\n*К оплате:* {price} 🪙"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить ✅", callback_data=f"pay_phone_{country}")],
        [InlineKeyboardButton(text="Отмена ✖", callback_data="phone_numbers_start")]
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def handle_virtual_country_selection(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    country = callback.data[9:]
    price = VIRTUAL_PRICES.get(country)
    
    await state.update_data(selected_country=country, selected_price=price, purchase_type="virtual")
    
    text = f"🎬 Значит берем вирт *{country}*\n\n*К оплате:* {price} 🪙"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить ✅", callback_data=f"pay_virtual_{country}")],
        [InlineKeyboardButton(text="Отмена ✖", callback_data="phone_numbers_start")]
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def handle_payment_confirmation(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    user = callback.from_user
    data = await state.get_data()
    
    country = data.get("selected_country")
    price = data.get("selected_price")
    purchase_type = data.get("purchase_type")
    
    user_id_str = str(user.id)
    initialize_user_reputation(user.id, user.id in ADMINS, user.id == OWNER_ID)
    current_coins = bot_data.data["REPUTATION_DATA"].get(user_id_str, {}).get("coins", 0)
    
    if current_coins < price:
        await callback.message.edit_text(f"❌ Недостаточно монет! Нужно: {price}, У вас: {current_coins}")
        return
    
    bot_data.data["REPUTATION_DATA"][user_id_str]["coins"] = current_coins - price
    bot_data.save_data()
    
    await callback.message.edit_text(
        f"✅ *Успешно!*\n\nВ течении часа вам напишет @VAR1SNA.\nТип: {purchase_type} номер\nСтрана: {country}",
        parse_mode="Markdown"
    )
    
    await bot.send_message(OWNER_ID, f"🛒 *НОВАЯ ПОКУПКА НОМЕРА*\n👤 {user.first_name}\n🌍 {country}\n💰 {price}🪙", parse_mode="Markdown")

# ========== ПОДАРКИ ==========
async def handle_gifts_start(callback: CallbackQuery):
    await callback.answer()
    text = "🧸 *Подарки в ТГ*\n\n- Мишка/Сердце: 25🪙\n- Роза/Подарок: 45🪙\n- Торт/Цветы/Ракета/Пиво: 90🪙\n- Колечко/Алмаз/Кубок: 150🪙"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 25🪙", callback_data="gift_category_25")],
        [InlineKeyboardButton(text="🎁 45🪙", callback_data="gift_category_45")],
        [InlineKeyboardButton(text="🎁 90🪙", callback_data="gift_category_90")],
        [InlineKeyboardButton(text="💎 150🪙", callback_data="gift_category_150")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_shop")]
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def handle_gift_category_25(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мишка 🧸", callback_data="gift_buy_Мишка")],
        [InlineKeyboardButton(text="Сердце 💝", callback_data="gift_buy_Сердце")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="gifts_start")]
    ])
    await callback.message.edit_text("Выберите подарок (25🪙):", reply_markup=keyboard)

async def handle_gift_category_45(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Роза 🌹", callback_data="gift_buy_Роза")],
        [InlineKeyboardButton(text="Подарок 🎁", callback_data="gift_buy_Подарок")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="gifts_start")]
    ])
    await callback.message.edit_text("Выберите подарок (45🪙):", reply_markup=keyboard)

async def handle_gift_category_90(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Торт 🎂", callback_data="gift_buy_Торт")],
        [InlineKeyboardButton(text="Цветы 💐", callback_data="gift_buy_Цветы")],
        [InlineKeyboardButton(text="Ракета 🚀", callback_data="gift_buy_Ракета")],
        [InlineKeyboardButton(text="Пиво 🍺", callback_data="gift_buy_Пиво")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="gifts_start")]
    ])
    await callback.message.edit_text("Выберите подарок (90🪙):", reply_markup=keyboard)

async def handle_gift_category_150(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Колечко 💍", callback_data="gift_buy_Колечко")],
        [InlineKeyboardButton(text="Алмаз 💎", callback_data="gift_buy_Алмаз")],
        [InlineKeyboardButton(text="Кубок 🏆", callback_data="gift_buy_Кубок")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="gifts_start")]
    ])
    await callback.message.edit_text("Выберите подарок (150🪙):", reply_markup=keyboard)

async def handle_gift_purchase(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    gift_type = callback.data.replace("gift_buy_", "")
    user = callback.from_user
    price = GIFT_PRICES.get(gift_type)
    
    user_id_str = str(user.id)
    initialize_user_reputation(user.id, user.id in ADMINS, user.id == OWNER_ID)
    current_coins = bot_data.data["REPUTATION_DATA"].get(user_id_str, {}).get("coins", 0)
    
    if current_coins < price:
        await callback.message.edit_text(f"❌ Недостаточно монет! Нужно: {price}")
        return
    
    bot_data.data["REPUTATION_DATA"][user_id_str]["coins"] = current_coins - price
    bot_data.save_data()
    
    emoji = GIFT_EMOJIS.get(gift_type, "🎁")
    await callback.message.edit_text(f"🥰 Хорошо! Жди.\nподарок {gift_type} {emoji} будет отправлен в течении 15 минут.")
    
    await bot.send_message(OWNER_ID, f"🎁 *НОВАЯ ПОКУПКА ПОДАРКА*\n👤 {user.first_name}\n🎁 {gift_type}\n💰 {price}🪙", parse_mode="Markdown")

# ========== ЗВЕЗДЫ ==========
async def handle_stars_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(stars_data={})
    text = f"✨ *Звездочки в Telegram*\n\nкурс: {STARS_RATE}🪙 за звездочку.\n\nУкажите количество звезд (минимум {MIN_STARS}):"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Указать кол-во 🖋", callback_data="stars_enter_amount")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_shop")]
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def handle_stars_enter_amount(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(UserStates.awaiting_stars_amount)
    await callback.message.edit_text("Напишите количество звезд цифрой:")

async def handle_stars_amount_input(message: Message, state: FSMContext, bot: Bot):
    try:
        stars_amount = int(message.text.strip())
        if stars_amount < MIN_STARS:
            await message.answer(f"❌ Минимум {MIN_STARS} звезд")
            return
        
        coins_needed = int(stars_amount * STARS_RATE)
        user_id_str = str(message.from_user.id)
        current_coins = bot_data.data["REPUTATION_DATA"].get(user_id_str, {}).get("coins", 0)
        
        await state.update_data(stars_data={
            "stars_amount": stars_amount,
            "coins_needed": coins_needed,
            "current_coins": current_coins,
            "has_enough": current_coins >= coins_needed
        })
        
        text = f"☺ *Окей, берем {stars_amount} звезд.*\n💰 Стоимость: {coins_needed}🪙\n💳 Ваш баланс: {current_coins}🪙\n\nКому отправляем?"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Купить себе 😎", callback_data="stars_buy_for_self")],
            [InlineKeyboardButton(text="Назад 🔙", callback_data="stars_start")]
        ])
        await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
        await state.set_state(UserStates.awaiting_stars_recipient)
        
    except ValueError:
        await message.answer("❌ Введите число!")

async def handle_stars_buy_for_self(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    stars_data = data.get("stars_data", {})
    stars_data["recipient"] = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.first_name
    await state.update_data(stars_data=stars_data)
    
    text = f"🖋 *Подтверждение*\n\nЗвезд: {stars_data['stars_amount']}\nПолучатель: {stars_data['recipient']}\nК оплате: {stars_data['coins_needed']}🪙\n\nВсе верно?"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data="stars_confirm")],
        [InlineKeyboardButton(text="❌ Нет", callback_data="stars_start")]
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def handle_stars_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    data = await state.get_data()
    stars_data = data.get("stars_data", {})
    user = callback.from_user
    
    if not stars_data.get("has_enough", False):
        await callback.message.edit_text("❌ Недостаточно монет!")
        return
    
    user_id_str = str(user.id)
    current_coins = bot_data.data["REPUTATION_DATA"].get(user_id_str, {}).get("coins", 0)
    
    if current_coins < stars_data["coins_needed"]:
        await callback.message.edit_text("❌ Баланс изменился, недостаточно монет!")
        return
    
    bot_data.data["REPUTATION_DATA"][user_id_str]["coins"] = current_coins - stars_data["coins_needed"]
    bot_data.save_data()
    
    await callback.message.edit_text("🎉 Отлично! отправляю...")
    
    await bot.send_message(OWNER_ID, 
        f"🌟🌟🌟 *НОВАЯ ПОКУПКА ЗВЕЗД* 🌟🌟🌟\n"
        f"👤 Покупатель: @{user.username or user.first_name}\n"
        f"🎯 Получатель: {stars_data['recipient']}\n"
        f"💫 Звезд: {stars_data['stars_amount']}\n"
        f"💰 Стоимость: {stars_data['coins_needed']}🪙",
        parse_mode="Markdown")
    
    await state.clear()

async def handle_stars_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await handle_stars_start(callback, state)

# ========== ВСПОМОГАТЕЛЬНЫЕ CALLBACK ==========
async def back_to_shop(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    # Создадим новое сообщение как при kiss_shop
    user = callback.from_user
    user_id_str = str(user.id)
    rep_data = bot_data.data["REPUTATION_DATA"].get(user_id_str, {})
    coins = rep_data.get("coins", 0)
    candies = rep_data.get("candies", 0)
    
    text = f"🎄 *KISS SHOP*\n\n❄ Монетки: {coins}\n🍫 Конфетки: {candies}\n\nЧтобы обменять конфетки в монетки, напишите команду: Лип [число]"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="пополнить 🌟", callback_data="buy_coins_start")],
        [InlineKeyboardButton(text="📞 Номера", callback_data="phone_numbers_start")],
        [InlineKeyboardButton(text="Подарки в ТГ 💝", callback_data="gifts_start")],
        [InlineKeyboardButton(text="Звезды 🌟", callback_data="stars_start")]
    ])
    await callback.message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

async def buy_coins_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(UserStates.awaiting_coins_amount)
    await callback.message.edit_text("🦆 Сколько монет хотите получить? Напишите число:")

async def handle_coins_amount_input(message: Message, state: FSMContext):
    try:
        coins_amount = int(message.text.strip())
        if coins_amount <= 0 or coins_amount > 1000000:
            await message.answer("❌ Введите число от 1 до 1,000,000")
            return
        
        rubles = coins_amount
        text = f"🎄 Прекрасно!\nПокупка на: {coins_amount} монет\nК оплате: {rubles}р\n\nВыберите способ оплаты:"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="банковской картой 💳", url="https://pay.cloudtips.ru/p/921f9727")]
        ])
        await message.answer(text, reply_markup=keyboard)
        await state.clear()
    except ValueError:
        await message.answer("❌ Введите число!")

# ========== ИНФОРМАЦИЯ ==========
async def info(message: Message):
    text = """
<b>ИНФОРМАЦИЯ О КИССМЕЙТАХ</b> <tg-emoji emoji-id="5350762341455660111">🥰</tg-emoji>

<tg-emoji emoji-id="5350773791838472343">🥰</tg-emoji> <b>: Конфетки —</b> @candysKXD
<tg-emoji emoji-id="5188701955383394589">🥰</tg-emoji><b>: Новости —</b> @kabanNEWSxd
<tg-emoji emoji-id="5348339241166342555">🥰</tg-emoji> <b>: Кухня —</b> @kyxna_kx

<i>Чтобы слить ссылку/юз нажмите на кнопку «Слить 🔥»</i>
<b>В <a href="https://teletype.in/@var1sna/jK_E1gO5kIS">статье</a></b> мы рассказали про то, как правильно слить ссылку, правила чата, как попасть в союзы и т.д
<tg-emoji emoji-id="5213396711665322724">🥰</tg-emoji> <i>Всех любим, целуем, обожаем!</i>
    """
    await message.answer(text, parse_mode="HTML")


async def process_sliv(message: Message, state: FSMContext, bot: Bot):
    """Обрабатывает отправленный слив"""
    user_id = message.from_user.id
    
    current_state = await state.get_state()
    if current_state != UserStates.awaiting_sliv:
        return
    
    if message.text and message.text.lower() == "отмена":
        await state.set_state(None)
        await message.answer("❌ Слив отменен")
        return
    
    username = message.from_user.username or ""
    text = message.caption or message.text or ""
    if username and f"@{username.lower()}" in text.lower():
        await message.answer("❌ Подозрение на самослив!")
        await state.set_state(None)
        return
    
    admin_text = (
        f"📨 *НОВЫЙ СЛИВ*\n"
        f"👤 От: @{username}\n"
        f"🆔 ID: `{user_id}`\n"
        f"📝 Текст: {text if text else 'Без текста'}\n"
        f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m')}"
    )
    
    sent = False
    for admin_id in ADMINS:
        try:
            if message.photo:
                await bot.send_photo(
                    chat_id=admin_id,
                    photo=message.photo[-1].file_id,
                    caption=admin_text,
                    parse_mode="Markdown"
                )
            elif message.video:
                await bot.send_video(
                    chat_id=admin_id,
                    video=message.video.file_id,
                    caption=admin_text,
                    parse_mode="Markdown"
                )
            else:
                await bot.send_message(
                    chat_id=admin_id,
                    text=admin_text,
                    parse_mode="Markdown"
                )
            sent = True
        except Exception as e:
            logger.error(f"Ошибка отправки админу {admin_id}: {e}")
    
    if sent:
        await message.answer("✅ Слив отправлен админам! Ожидайте.")
        USER_COOLDOWN[user_id] = datetime.now() + timedelta(minutes=5)
    else:
        await message.answer("❌ Ошибка при отправке. Попробуйте позже.")
    
    await state.set_state(None)

# ========== СЛИВ ==========
async def sliv(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.clear()
    username = message.from_user.username or ""
    
    if username.lower() in bot_data.data["SPAM_FILTER"]:
        reason = bot_data.data["SPAM_FILTER"][username.lower()]
        await message.answer(f"❗ Вы в спам-фильтре, сожалеем. причина: {reason}. для разблокировки обращайтесь к рыцарям")
        return

    if user_id in USER_COOLDOWN and datetime.now() < USER_COOLDOWN[user_id]:
        remaining = (USER_COOLDOWN[user_id] - datetime.now()).seconds // 60
        await message.answer(f"⏳ Жди {remaining} минут!")
        return

    if await state.get_state() == UserStates.awaiting_raid_request:
        await state.set_state(None)

    current_state = await state.get_state()
    if current_state is not None:
        logger.info(f"Пользователь {user_id} уже в состоянии {current_state}, сбрасываю")
        await state.clear()

    await state.set_state(UserStates.awaiting_sliv)
    logger.info(f"Установлен awaiting_sliv для пользователя {user_id}")
    
    text = """
<tg-emoji emoji-id="5242474396173475303">🥰</tg-emoji> <b>Сейчас вы можете отправить 1 сообщение администрации с ссылкой/юзом.</b> 
Соблюдайте правила!

<tg-emoji emoji-id="5348096498204682843">🥰</tg-emoji> <b> Правила </b>
1. если вы сливаете юз, не забудьте написать причину и доки
2. кидать исключительно одно медиа доказательство 
3. без спама и самослива

<tg-emoji emoji-id="5370831009937890906">🥰</tg-emoji> <b>Перед отправкой вы должны быть ознакомлены с тем, что:</b> 
— сообщения из канала не удаляются (кроме экстренных случаев). <tg-emoji emoji-id="5240111691714301066">🥰</tg-emoji>
— мы не несем ответственности за ваши будущие взаимоотношения с чатом/человеком. <tg-emoji emoji-id="5343566686391930577">🥰</tg-emoji>
— ваши данные не будут раскрыты. <tg-emoji emoji-id="5375506335242661284">🥰</tg-emoji>

Если передумали сливать, напишите слово отмена.
"""
    await message.answer(text, parse_mode="HTML")
# ========== ПЕРЕСЫЛКА АДМИНАМ ==========
async def forward_to_admins(message: Message, state: FSMContext, bot: Bot):
    """Пересылает слив админам"""
    user_id = message.from_user.id
    logger.info(f"=== forward_to_admins вызван для {user_id} ===")

    user = message.from_user
    text = message.caption or message.text or ""
    username = user.username or str(user.id)
    
    # Проверка на самослив
    if (user.username and f"@{user.username.lower()}" in text.lower()):
        await message.answer("❌ Подозрение на самослив!")
        await state.set_state(None)
        return

    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    sliv_id = str(uuid.uuid4())[:8]
    
    admin_msg = f"❄ СЛИВ ОТ: @{username}\nID: <code>{user.id}</code>\n\n{text if text else 'Без текста'}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Слито!", callback_data=f"sliv_confirm_{user.id}_{sliv_id}"),
            InlineKeyboardButton(text="👻 Просмотрено", callback_data=f"sliv_viewed_{user.id}_{sliv_id}")
        ]
    ])

    media_info = {}
    if message.photo:
        media_info = {"type": "photo", "file_id": message.photo[-1].file_id}
    elif message.video:
        media_info = {"type": "video", "file_id": message.video.file_id}
    elif message.document:
        media_info = {"type": "document", "file_id": message.document.file_id}
    else:
        media_info = {"type": "text", "file_id": None}

    message_ids = {}
    for admin_id in ADMINS:
        try:
            if message.photo:
                sent_msg = await bot.send_photo(
                    chat_id=admin_id,
                    photo=message.photo[-1].file_id,
                    caption=admin_msg,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            elif message.video:
                sent_msg = await bot.send_video(
                    chat_id=admin_id,
                    video=message.video.file_id,
                    caption=admin_msg,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            elif message.document:
                sent_msg = await bot.send_document(
                    chat_id=admin_id,
                    document=message.document.file_id,
                    caption=admin_msg,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            else:
                sent_msg = await bot.send_message(
                    chat_id=admin_id,
                    text=admin_msg,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            message_ids[str(admin_id)] = sent_msg.message_id
        except Exception as e:
            logger.error(f"Ошибка отправки админу {admin_id}: {e}")

    if message_ids:
        bot_data.data["ADMIN_MESSAGES"][str(user.id)] = {
            "sliv_id": sliv_id,
            "message_ids": message_ids,
            "text": admin_msg,
            "media": media_info,
            "original_sender": user.id,
            "original_message_id": message.message_id,
            "original_chat_id": message.chat.id,
            "status": "not_viewed",
            "viewed_by": None,
            "confirmed_by": None,
            "sent_time": current_time,
            "edited": False,
            "edit_time": None
        }
        
        bot_data.data["SLIV_STATUS"][sliv_id] = {
            "user_id": user.id,
            "status": "not_viewed",
            "admin_message_ids": message_ids,
            "sent_time": current_time,
            "original_message_id": message.message_id,
            "original_chat_id": message.chat.id,
            "edited": False,
            "edit_time": None,
            "user_message_id": None
        }
        
        user_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Редактировать ✍🏻", callback_data=f"edit_sliv_{sliv_id}"),
                InlineKeyboardButton(text="Удалить ❌", callback_data=f"delete_sliv_{sliv_id}")
            ]
        ])
        
        user_msg = await message.answer(
            f"🥳 *Отправил админам!*\n\n*Статус твоего слива:* не прочитано \n*Отправлен:* {current_time}",
            parse_mode="Markdown",
            reply_markup=user_keyboard
        )
        
        bot_data.data["SLIV_STATUS"][sliv_id]["user_message_id"] = user_msg.message_id
        bot_data.data["ADMIN_MESSAGES"][str(user.id)]["user_message_id"] = user_msg.message_id
        bot_data.data["ADMIN_MESSAGES"][str(user.id)]["user_chat_id"] = message.chat.id
        
        bot_data.save_data()
        USER_COOLDOWN[user.id] = datetime.now() + timedelta(minutes=5)
    else:
        await message.answer("❌ Ошибка при отправке. Попробуйте сделать покороче текст.")

    await state.set_state(None)

# ========== ОБРАБОТЧИК КНОПОК СЛИВА ==========
async def handle_sliv_buttons(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    
    data = callback.data
    parts = data.split("_")
    
    if len(parts) < 4:
        try:
            await callback.message.edit_text("❌ Ошибка данных")
        except:
            pass
        return
    
    action = parts[1]
    user_id = int(parts[2])
    sliv_id = parts[3]
    admin_id = callback.from_user.id
    admin_name = callback.from_user.username or callback.from_user.first_name

    sliv_data = None
    message_data = None
    
    if sliv_id in bot_data.data["SLIV_STATUS"]:
        sliv_data = bot_data.data["SLIV_STATUS"][sliv_id]
    
    if str(user_id) in bot_data.data["ADMIN_MESSAGES"]:
        message_data = bot_data.data["ADMIN_MESSAGES"][str(user_id)]
        if message_data.get("sliv_id") != sliv_id:
            message_data = None
    
    if not message_data and not sliv_data:
        try:
            await callback.message.edit_text("❌ Сообщение не найдено")
        except:
            pass
        return

    if action == "confirm":
        new_text = f"✅ Слито админом: [{admin_name}](tg://user?id={admin_id})\n\n{message_data['text'] if message_data else 'Сообщение не найдено'}"
        
        await publish_post_to_channel(bot, message_data, admin_name, admin_id)
        
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"✅ *Ваш слив был подтвержден админом {admin_name} и отправлен в канал!*",
                parse_mode="Markdown"
            )
            
            if sliv_id in bot_data.data["SLIV_STATUS"]:
                bot_data.data["SLIV_STATUS"][sliv_id]["status"] = "confirmed"
                bot_data.data["SLIV_STATUS"][sliv_id]["confirmed_by"] = admin_id
                
                try:
                    await bot.edit_message_text(
                        chat_id=user_id,
                        message_id=sliv_data.get("user_message_id"),
                        text=f"🥳 *Отправил админам!*\n\n*Статус твоего слива:* ✅ Слито [{admin_name}](tg://user?id={admin_id})\n*Отправлен:* {sliv_data.get('sent_time', 'Неизвестно')}",
                        parse_mode="Markdown",
                        reply_markup=None
                    )
                except:
                    pass
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления пользователю {user_id}: {e}")
            
    elif action == "viewed":
        new_text = f"👻 Просмотрено админом: [{admin_name}](tg://user?id={admin_id})\n\n{message_data['text'] if message_data else 'Сообщение не найдено'}"
        
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"👻 *Ваше сообщение просмотрел админ {admin_name}, но не отправили в канал.*\n\nПроверьте, что ваше сообщение содержит причину, доказательства и юзернейм/ссылку.",
                parse_mode="Markdown"
            )
            
            if sliv_id in bot_data.data["SLIV_STATUS"]:
                bot_data.data["SLIV_STATUS"][sliv_id]["status"] = "viewed"
                bot_data.data["SLIV_STATUS"][sliv_id]["viewed_by"] = admin_id
                
                try:
                    await bot.edit_message_text(
                        chat_id=user_id,
                        message_id=sliv_data.get("user_message_id"),
                        text=f"🥳 *Отправил админам!*\n\n*Статус твоего слива:* 👻 Просмотрено [{admin_name}](tg://user?id={admin_id})\n*Отправлен:* {sliv_data.get('sent_time', 'Неизвестно')}",
                        parse_mode="Markdown",
                        reply_markup=None
                    )
                except:
                    pass
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления пользователю {user_id}: {e}")

    if message_data:
        for admin_id_str, msg_id in message_data["message_ids"].items():
            try:
                admin_id_int = int(admin_id_str)
                if message_data["media"]["type"] == "photo":
                    await bot.edit_message_caption(
                        chat_id=admin_id_int,
                        message_id=msg_id,
                        caption=new_text,
                        parse_mode="Markdown"
                    )
                elif message_data["media"]["type"] in ["video", "document"]:
                    await bot.edit_message_caption(
                        chat_id=admin_id_int,
                        message_id=msg_id,
                        caption=new_text,
                        parse_mode="Markdown"
                    )
                else:
                    await bot.edit_message_text(
                        chat_id=admin_id_int,
                        message_id=msg_id,
                        text=new_text,
                        parse_mode="Markdown"
                    )

                try:
                    await bot.edit_message_reply_markup(
                        chat_id=admin_id_int,
                        message_id=msg_id,
                        reply_markup=None
                    )
                except:
                    pass
            except Exception as e:
                logger.error(f"Ошибка обновления сообщения у админа {admin_id_str}: {e}")

        if str(user_id) in bot_data.data["ADMIN_MESSAGES"]:
            bot_data.data["ADMIN_MESSAGES"][str(user_id)]["status"] = "confirmed" if action == "confirm" else "viewed"
            if action == "confirm":
                bot_data.data["ADMIN_MESSAGES"][str(user_id)]["confirmed_by"] = admin_id
            else:
                bot_data.data["ADMIN_MESSAGES"][str(user_id)]["viewed_by"] = admin_id
            
        bot_data.save_data()

async def publish_post_to_channel(bot: Bot, sliv_data: dict, admin_name: str, admin_id: int):
    """Публикует подтвержденный слив в привязанный канал"""
    channel_id = bot_data.data.get("CHANNEL_FOR_POSTS")
    if not channel_id:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text="⚠️ Канал для публикаций не привязан. Используйте `!привязать` в ЛС с ботом.",
                parse_mode="Markdown"
            )
        except:
            pass
        return

    media_info = sliv_data.get('media', {})
    media_type = media_info.get('type')
    file_id = media_info.get('file_id')
    
    # Проверяем, есть ли медиа (только фото/видео публикуем)
    if not file_id or media_type == 'text':
        try:
            await bot.send_message(
                chat_id=admin_id,
                text="⚠️ Пост НЕ опубликован в канал, так как в сливе отсутствуют фото/видео.\nВ канал автоматически публикуются только посты с медиафайлами."
            )
        except:
            pass
        return

    # Извлекаем ТОЛЬКО текст пользователя (без служебной информации)
    original_admin_text = sliv_data.get('text', '')
    
    # Получаем чистый текст пользователя
    user_text = ""
    # Ищем текст после "❄ СЛИВ ОТ:" и "ID:"
    match = re.search(r'❄ СЛИВ ОТ:.*?\nID:.*?\n\n(.*?)(?:\n\n|$)', original_admin_text, re.DOTALL | re.IGNORECASE)
    if match:
        user_text = match.group(1).strip()
    else:
        # Если не нашли по шаблону, берем всё что после первых двух строк
        lines = original_admin_text.split('\n')
        if len(lines) > 2:
            user_text = '\n'.join(lines[2:]).strip()
            # Убираем возможные служебные надписи в конце
            user_text = re.sub(r'\n\n✅ Слито админом:.*$', '', user_text, flags=re.IGNORECASE)
            user_text = re.sub(r'\n\n👻 Просмотрено админом:.*$', '', user_text, flags=re.IGNORECASE)
            user_text = re.sub(r'\n\n🔄 Оригинал был отредактирован:.*$', '', user_text, flags=re.IGNORECASE)
    
    # Если текст пустой, ставим значение по умолчанию
    if not user_text:
        user_text = "Без текста"

    # Форматируем заголовок (ссылка синим цветом)
    # <a href="ссылка">текст</a> - это автоматически делает текст синим в Telegram
    caption = (
        '🤯 <b><a href="https://t.me/kisskxd_bot">КИССБОТ</a></b> ||\n'
        '<i>конфетки: @candysKXD</i>\n\n'
        f'{user_text}'
    )

    try:
        if media_type == 'photo' and file_id:
            await bot.send_photo(
                chat_id=channel_id,
                photo=file_id,
                caption=caption,
                parse_mode='HTML'
            )
            logger.info(f"Пост с фото опубликован в канал {channel_id}")
            
        elif media_type == 'video' and file_id:
            await bot.send_video(
                chat_id=channel_id,
                video=file_id,
                caption=caption,
                parse_mode='HTML'
            )
            logger.info(f"Пост с видео опубликован в канал {channel_id}")
            
        elif media_type == 'document' and file_id:
            await bot.send_document(
                chat_id=channel_id,
                document=file_id,
                caption=caption,
                parse_mode='HTML'
            )
            logger.info(f"Пост с документом опубликован в канал {channel_id}")
        
        # Уведомляем админа об успехе
        await bot.send_message(
            chat_id=admin_id,
            text="✅ Пост успешно опубликован в привязанный канал."
        )

    except Exception as e:
        logger.error(f"Ошибка публикации поста в канал {channel_id}: {e}")
        await bot.send_message(
            chat_id=admin_id,
            text=f"❌ Не удалось опубликовать пост в канал. Ошибка: {e}\nПроверь, что бот до сих пор является админом канала."
        )

# ========== РЕЙДЫ ==========
async def order_raid(message: Message, state: FSMContext):
    user = message.from_user
    if await state.get_state() == UserStates.awaiting_sliv:
        await state.set_state(None)
    
    await state.set_state(UserStates.awaiting_raid_request)
    
    instruction_text = """
<b>🐈‍⬛ BONJOUR</b>, сейчас твоя задача описать полностью проблему, скинуть юз владельца чата (ну или кому писать по поводу вступления), скинуть доказательства в одном видео или одном фото!! (если сделаешь больше — сообщение не придет нормально). Так же убедись, что именно ТВОЯ причина достойна, именно ЭТОТ чат должен быть снесен. 🖤 

Причины по типу "адм кусаются" или "меня выгнали" — ДАЖЕ НЕ БУДУТ РАССМАТРИВАТЬСЯ.

🐦‍⬛ Если тебе нужен пример сообщения, то можешь посмотреть его <a href="https://telegra.ph/PRIMER-SOOBSHCHENIYA-NA-REJD-09-22">здесь</a>
Узнать, что будет на рейде можно <a href="https://telegra.ph/CHTO-BUDET-NA-REJDE-09-22">здесь</a>

💣 Напиши сейчас свое сообщение с фото/видео или текстом. Для отмены напиши "отмена".
    """
    
    await message.answer(instruction_text, parse_mode="HTML")

async def handle_raid_request(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username or ""

    if username.lower() in bot_data.data["SPAM_FILTER"]:
        reason = bot_data.data["SPAM_FILTER"][username.lower()]
        await message.answer(f"вы в спам фильтрееее)) причина: {reason}")
        await state.set_state(None)
        return
    
    if message.text and message.text.lower() == "отмена":
        await state.set_state(None)
        await message.answer("🐈‍⬛ Окей, отменил отправку админам =)")
        return
    
    user = message.from_user
    username = user.username or user.first_name
    
    await message.answer("🐈‍⬛ Отправлено, ожидай")

    raid_text = message.caption or message.text or "Без текста"
    
    admin_message = f"🖤<b>ЗАКАЗИК ОТ:</b> @{username}\n"
    admin_message += f"<b>ID:</b> <code>{user.id}</code>\n\n"
    admin_message += f"{raid_text}\n\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Отказ", callback_data=f"raid_reject_{user.id}"),
            InlineKeyboardButton(text="✅ Я иду", callback_data=f"raid_accept_{user.id}")
        ]
    ])
    
    all_recipients = list(set(ADMINS + MODERATORS))
    message_ids = {}
    
    for recipient_id in all_recipients:
        try:
            if message.photo:
                sent_msg = await bot.send_photo(
                    chat_id=recipient_id,
                    photo=message.photo[-1].file_id,
                    caption=admin_message,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            elif message.video:
                sent_msg = await bot.send_video(
                    chat_id=recipient_id,
                    video=message.video.file_id,
                    caption=admin_message,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            elif message.document:
                sent_msg = await bot.send_document(
                    chat_id=recipient_id,
                    document=message.document.file_id,
                    caption=admin_message,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            else:
                sent_msg = await bot.send_message(
                    chat_id=recipient_id,
                    text=admin_message,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            
            message_ids[str(recipient_id)] = sent_msg.message_id
            
        except Exception as e:
            logger.error(f"Ошибка отправки заявки на рейд {recipient_id}: {e}")
    
    RAID_REQUESTS[str(user.id)] = {
        "message_ids": message_ids,
        "admin_message": admin_message,
        "media": {
            "type": "photo" if message.photo else "video" if message.video else "document" if message.document else "text",
            "file_id": message.photo[-1].file_id if message.photo else message.video.file_id if message.video else message.document.file_id if message.document else None
        },
        "accepted_by": [],  
        "rejected_by": None,
        "user_id": user.id
    }
    
    await state.set_state(None)

async def handle_raid_buttons(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    
    data = callback.data
    admin = callback.from_user
    admin_name = admin.username or admin.first_name
    
    if data.startswith("raid_reject_"):
        user_id = data.split("_")[2]
        await process_raid_rejection(user_id, admin, admin_name, bot, callback)
        
    elif data.startswith("raid_accept_"):
        user_id = data.split("_")[2]
        await process_raid_acceptance(user_id, admin, admin_name, bot, callback)

async def process_raid_rejection(user_id: str, admin, admin_name: str, bot: Bot, callback: CallbackQuery):
    if user_id not in RAID_REQUESTS:
        await bot.send_message(admin.id, "❌ Заявка не найдена")
        return
    
    raid_data = RAID_REQUESTS[user_id]
    raid_data["rejected_by"] = admin.id

    new_text = f"👻<b>ОТКАЗАЛ АДМИН:</b> @{admin_name}\n\n{raid_data['admin_message']}"
    
    for recipient_id, msg_id in raid_data["message_ids"].items():
        try:
            if raid_data["media"]["type"] == "photo":
                await bot.edit_message_caption(
                    chat_id=int(recipient_id),
                    message_id=msg_id,
                    caption=new_text,
                    parse_mode="HTML",
                    reply_markup=None
                )
            elif raid_data["media"]["type"] in ["video", "document"]:
                await bot.edit_message_caption(
                    chat_id=int(recipient_id),
                    message_id=msg_id,
                    caption=new_text,
                    parse_mode="HTML",
                    reply_markup=None
                )
            else:
                await bot.edit_message_text(
                    chat_id=int(recipient_id),
                    message_id=msg_id,
                    text=new_text,
                    parse_mode="HTML",
                    reply_markup=None
                )
        except Exception as e:
            logger.error(f"Ошибка обновления сообщения у {recipient_id}: {e}")
    
    try:
        await bot.send_message(
            chat_id=int(user_id),
            text="💣 Ваше сообщение просмотрели и решили отказать. Может..чет не так в обращении?"
        )
    except Exception as e:
        logger.error(f"Ошибка уведомления пользователя {user_id}: {e}")
    
    del RAID_REQUESTS[user_id]

async def process_raid_acceptance(user_id: str, admin, admin_name: str, bot: Bot, callback: CallbackQuery):
    if user_id not in RAID_REQUESTS:
        await bot.send_message(admin.id, "❌ Заявка не найдена")
        return
    
    raid_data = RAID_REQUESTS[user_id]
    
    if raid_data["rejected_by"]:
        await bot.send_message(admin.id, "❌ По этой заявке уже отказали")
        return
    
    if admin.id not in raid_data["accepted_by"]:
        raid_data["accepted_by"].append(admin.id)
    
    accepted_count = len(raid_data["accepted_by"])
    
    if accepted_count == 1:
        new_text = f"{raid_data['admin_message']}\n\n<b>ИДЕТ НА ЗАКАЗ:</b> @{admin_name} 1/2"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я иду", callback_data=f"raid_accept_{user_id}")]
        ])
        reply_markup = keyboard
        
    elif accepted_count == 2:
        admin_names = []
        for admin_id in raid_data["accepted_by"]:
            try:
                admin_chat = await bot.get_chat(admin_id)
                admin_names.append(f"@{admin_chat.username}" if admin_chat.username else admin_chat.first_name)
            except:
                admin_names.append(f"ID:{admin_id}")
        
        new_text = f"✅ <b>НА ЗАКАЗ ИДУТ:</b> {' '.join(admin_names)}\n\n{raid_data['admin_message']}"
        reply_markup = None  
        
        del RAID_REQUESTS[user_id]
    else:
        return 
    
    for recipient_id, msg_id in raid_data["message_ids"].items():
        try:
            if raid_data["media"]["type"] == "photo":
                await bot.edit_message_caption(
                    chat_id=int(recipient_id),
                    message_id=msg_id,
                    caption=new_text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            elif raid_data["media"]["type"] in ["video", "document"]:
                await bot.edit_message_caption(
                    chat_id=int(recipient_id),
                    message_id=msg_id,
                    caption=new_text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            else:
                await bot.edit_message_text(
                    chat_id=int(recipient_id),
                    message_id=msg_id,
                    text=new_text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
        except Exception as e:
            logger.error(f"Ошибка обновления сообщения у {recipient_id}: {e}")

# ========== НАПИСАТЬ НАМ (СООБЩЕНИЯ АДМИНАМ) ==========
async def start_write_to_admins(message: Message, state: FSMContext):
    user = message.from_user
    
    await state.set_state(UserStates.awaiting_message_to_admins)
    
    instruction_text = """
📩 *Привет!*

Сейчас ты можешь написать любое сообщение админам и, возможно, тебе ответят.

Ты можешь отправить фото, чем то поделиться, задать вопрос и т.п. Но не злоупотребляй функцией.

*Напиши свое сообщение ниже:* (для отмены напиши "отмена")
"""
    
    await message.answer(instruction_text, parse_mode="Markdown")

async def handle_message_to_admins(message: Message, state: FSMContext, bot: Bot):
    user = message.from_user
    user_id = user.id
    
    current_state = await state.get_state()
    if current_state != UserStates.awaiting_message_to_admins:
        return
    
    if message.text and message.text.lower() == "отмена":
        await state.set_state(None)
        await message.answer("❌ Отправка сообщения админам отменена.")
        return
    
    username = user.username or user.first_name
    user_link = f"@{username}" if user.username else username
    
    message_text = message.text or message.caption or "Без текста"
    
    admin_message_text = (
        f"🤡 *СООБЩЕНИЕ ОТ:* {user_link}\n"
        f"*ID:* `{user_id}`\n\n"
        f"{message_text}"
    )
    
    import time
    msg_id = f"user_msg_{user_id}_{int(time.time())}"
    
    media_info = {}
    file_id = None
    
    if message.photo:
        file_id = message.photo[-1].file_id
        media_info = {"type": "photo", "file_id": file_id}
    elif message.video:
        file_id = message.video.file_id
        media_info = {"type": "video", "file_id": file_id}
    elif message.document:
        file_id = message.document.file_id
        media_info = {"type": "document", "file_id": file_id}
    else:
        media_info = {"type": "text", "file_id": None}
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="ОК ✨", callback_data=f"admin_ok_{msg_id}"),
            InlineKeyboardButton(text="Ответить 🖋", callback_data=f"admin_reply_{msg_id}")
        ]
    ])
    
    USER_MESSAGES_TO_ADMINS[msg_id] = {
        "user_id": user_id,
        "user_username": username,
        "user_link": user_link,
        "message_text": message_text,
        "media_info": media_info,
        "original_message_id": message.message_id,
        "original_chat_id": message.chat.id,
        "admin_message_ids": {},
        "status": "new",
        "admin_replied": None,
        "reply_text": None
    }
    
    message_ids = {}
    for admin_id in ADMINS:
        try:
            if message.photo and file_id:
                sent_msg = await bot.send_photo(
                    chat_id=admin_id,
                    photo=file_id,
                    caption=admin_message_text,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            elif message.video and file_id:
                sent_msg = await bot.send_video(
                    chat_id=admin_id,
                    video=file_id,
                    caption=admin_message_text,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            elif message.document and file_id:
                sent_msg = await bot.send_document(
                    chat_id=admin_id,
                    document=file_id,
                    caption=admin_message_text,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            else:
                sent_msg = await bot.send_message(
                    chat_id=admin_id,
                    text=admin_message_text,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            
            message_ids[str(admin_id)] = sent_msg.message_id
            
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения админу {admin_id}: {e}")
    
    USER_MESSAGES_TO_ADMINS[msg_id]["admin_message_ids"] = message_ids
    
    await message.answer(
        "✅ *Сообщение отправлено админам!*\n\n"
        "Если админы сочтут нужным, они могут ответить тебе. "
        "Ожидай ответ в этом чате.",
        parse_mode="Markdown"
    )
    
    await state.set_state(None)

async def handle_admin_buttons(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    
    data = callback.data
    admin_id = callback.from_user.id
    admin_name = callback.from_user.username or callback.from_user.first_name
    
    if data.startswith("admin_ok_"):
        message_id = data.replace("admin_ok_", "")
        await handle_admin_ok(callback, message_id, admin_id, admin_name, bot)
    
    elif data.startswith("admin_reply_"):
        message_id = data.replace("admin_reply_", "")
        await handle_admin_reply_start(callback, state, message_id, admin_id, admin_name, bot)

async def handle_admin_ok(callback: CallbackQuery, message_id: str, admin_id: int, admin_name: str, bot: Bot):
    if message_id not in USER_MESSAGES_TO_ADMINS:
        await callback.message.edit_text("❌ Сообщение не найдено или уже обработано")
        return
    
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
        pass
    
    await callback.answer("✅ Кнопки убраны")

async def handle_admin_reply_start(callback: CallbackQuery, state: FSMContext, message_id: str, admin_id: int, admin_name: str, bot: Bot):
    if message_id not in USER_MESSAGES_TO_ADMINS:
        await callback.message.edit_text("❌ Сообщение не найдено или уже обработано")
        return
    
    msg_data = USER_MESSAGES_TO_ADMINS[message_id]
    
    if msg_data["status"] == "replied":
        await callback.answer("❌ На это сообщение уже ответили", show_alert=True)
        return
    
    await state.update_data(replying_to_message=message_id, replying_admin_id=admin_id, replying_admin_name=admin_name)
    await state.set_state(AdminStates.replying_to_message)
    
    try:
        reply_text = (
            f"🖋 *Хорошо, давай ответим.*\n\n"
            f"Отправь текст ответа пользователю {msg_data['user_link']}.\n"
            f"Можно прикрепить фото/видео.\n\n"
            f"Для отмены напиши 'отмена'."
        )
        
        await callback.message.edit_text(reply_text, parse_mode="Markdown")
    except:
        await bot.send_message(
            chat_id=admin_id,
            text=reply_text,
            parse_mode="Markdown"
        )

async def handle_admin_reply_message(message: Message, state: FSMContext, bot: Bot):
    admin_id = message.from_user.id
    
    current_state = await state.get_state()
    if current_state != AdminStates.replying_to_message:
        return
    
    data = await state.get_data()
    message_id = data.get("replying_to_message")
    
    if message_id not in USER_MESSAGES_TO_ADMINS:
        await message.answer("❌ Сообщение не найдено")
        await state.set_state(None)
        return
    
    if message.text and message.text.lower() == "отмена":
        await message.answer("❌ Ответ отменен")
        await state.set_state(None)
        return
    
    msg_data = USER_MESSAGES_TO_ADMINS[message_id]
    user_id = msg_data["user_id"]
    
    admin_name = data.get("replying_admin_name", "Админ")
    
    reply_text = message.text or message.caption or ""
    admin_link = f"[{admin_name}](tg://user?id={admin_id})"
    
    user_message_text = (
        f"👑 **Вам ответил админ:** {admin_link}\n\n"
        f"{reply_text}"
    )
    
    try:
        if message.photo:
            await bot.send_photo(
                chat_id=user_id,
                photo=message.photo[-1].file_id,
                caption=user_message_text,
                parse_mode="Markdown"
            )
        elif message.video:
            await bot.send_video(
                chat_id=user_id,
                video=message.video.file_id,
                caption=user_message_text,
                parse_mode="Markdown"
            )
        elif message.document:
            await bot.send_document(
                chat_id=user_id,
                document=message.document.file_id,
                caption=user_message_text,
                parse_mode="Markdown"
            )
        else:
            await bot.send_message(
                chat_id=user_id,
                text=user_message_text,
                parse_mode="Markdown"
            )
        
        USER_MESSAGES_TO_ADMINS[message_id]["status"] = "replied"
        USER_MESSAGES_TO_ADMINS[message_id]["admin_replied"] = admin_id
        USER_MESSAGES_TO_ADMINS[message_id]["reply_text"] = reply_text
        
        updated_admin_message = (
            f"✅ *Ответил админ:* {admin_name}\n"
            f"🤡 *СООБЩЕНИЕ ОТ:* {msg_data['user_link']}\n"
            f"*ID:* `{msg_data['user_id']}`\n\n"
            f"{msg_data['message_text']}"
        )
        
        for admin_id_str, msg_id in msg_data["admin_message_ids"].items():
            try:
                admin_id_int = int(admin_id_str)
                
                if msg_data["media_info"]["type"] == "photo" and msg_data["media_info"]["file_id"]:
                    await bot.edit_message_caption(
                        chat_id=admin_id_int,
                        message_id=msg_id,
                        caption=updated_admin_message,
                        parse_mode="Markdown",
                        reply_markup=None
                    )
                elif msg_data["media_info"]["type"] in ["video", "document"] and msg_data["media_info"]["file_id"]:
                    await bot.edit_message_caption(
                        chat_id=admin_id_int,
                        message_id=msg_id,
                        caption=updated_admin_message,
                        parse_mode="Markdown",
                        reply_markup=None
                    )
                else:
                    await bot.edit_message_text(
                        chat_id=admin_id_int,
                        message_id=msg_id,
                        text=updated_admin_message,
                        parse_mode="Markdown",
                        reply_markup=None
                    )
            except Exception as e:
                logger.error(f"Ошибка обновления у админа {admin_id_str}: {e}")
        
        await message.answer("✅ Ответ отправлен пользователю!")
        
    except Exception as e:
        logger.error(f"Ошибка отправки ответа пользователю: {e}")
        await message.answer("❌ Не удалось отправить ответ. Возможно, пользователь заблокировал бота.")
    
    await state.set_state(None)

# ========== РЕДАКТИРОВАНИЕ И УДАЛЕНИЕ СЛИВА ==========
async def handle_edit_sliv(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    sliv_id = callback.data.replace("edit_sliv_", "")
    
    sliv_data = None
    user_id = None
    
    if sliv_id in bot_data.data["SLIV_STATUS"]:
        sliv_data = bot_data.data["SLIV_STATUS"][sliv_id]
        user_id = sliv_data["user_id"]
    elif str(callback.from_user.id) in bot_data.data["ADMIN_MESSAGES"]:
        for uid, data in bot_data.data["ADMIN_MESSAGES"].items():
            if data.get("sliv_id") == sliv_id:
                sliv_data = data
                user_id = int(uid)
                break
    
    if not sliv_data:
        await callback.message.edit_text("❌ Слив не найден или уже был обработан")
        return
    
    if callback.from_user.id != user_id:
        await callback.answer("Это не ваш слив!", show_alert=True)
        return
    
    if sliv_data.get("status") != "not_viewed":
        await callback.message.edit_text("❌ Этот слив уже был просмотрен админами, редактирование невозможно")
        return
    
    await state.update_data(
        editing_sliv_id=sliv_id,
        editing_user_id=user_id,
        editing_message_id=callback.message.message_id,
        editing_chat_id=callback.message.chat.id
    )
    await state.set_state(UserStates.editing_sliv)
    
    edit_text = """
🖋 *Редакция слива*

⚠️ Важно: не стоит изменять орфографические или грамматические ошибки. 
В основном лучше использовать эту функцию для добавления какой-то информации или что-то убрать, поменять ссылку / юзернейм.

✉️ Отправьте новый вид слива. Вы можете его исправить только 1 раз.
"""
    
    await callback.message.edit_text(edit_text, parse_mode="Markdown", reply_markup=None)

async def handle_edited_sliv(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    
    current_state = await state.get_state()
    if current_state != UserStates.editing_sliv:
        return
    
    data = await state.get_data()
    editing_sliv_id = data.get("editing_sliv_id")
    editing_user_id = data.get("editing_user_id")
    
    if user_id != editing_user_id:
        return
    
    sliv_data = bot_data.data["SLIV_STATUS"].get(editing_sliv_id)
    if not sliv_data:
        await message.answer("❌ Данные слива не найдены")
        await state.set_state(None)
        return
    
    user = message.from_user
    text = message.caption or message.text or ""
    username = user.username or str(user.id)
    
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    admin_msg = f"❄ СЛИВ ОТ: @{username}\nID: <code>{user.id}</code>\n\n{text if text else 'Без текста'}\n\n🔄 Оригинал был отредактирован: {current_time}"
    
    media_info = {}
    if message.photo:
        media_info = {"type": "photo", "file_id": message.photo[-1].file_id}
    elif message.video:
        media_info = {"type": "video", "file_id": message.video.file_id}
    elif message.document:
        media_info = {"type": "document", "file_id": message.document.file_id}
    else:
        media_info = {"type": "text", "file_id": None}
    
    message_ids = sliv_data.get("admin_message_ids", {})
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Слито!", callback_data=f"sliv_confirm_{user.id}_{editing_sliv_id}"),
            InlineKeyboardButton(text="👻 Просмотрено", callback_data=f"sliv_viewed_{user.id}_{editing_sliv_id}")
        ]
    ])
    
    for admin_id_str, msg_id in message_ids.items():
        try:
            admin_id_int = int(admin_id_str)
            
            try:
                await bot.delete_message(chat_id=admin_id_int, message_id=msg_id)
            except:
                pass
            
            if message.photo:
                sent_msg = await bot.send_photo(
                    chat_id=admin_id_int,
                    photo=message.photo[-1].file_id,
                    caption=admin_msg,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            elif message.video:
                sent_msg = await bot.send_video(
                    chat_id=admin_id_int,
                    video=message.video.file_id,
                    caption=admin_msg,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            elif message.document:
                sent_msg = await bot.send_document(
                    chat_id=admin_id_int,
                    document=message.document.file_id,
                    caption=admin_msg,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            else:
                sent_msg = await bot.send_message(
                    chat_id=admin_id_int,
                    text=admin_msg,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            
            message_ids[admin_id_str] = sent_msg.message_id
            
        except Exception as e:
            logger.error(f"Ошибка обновления сообщения у админа {admin_id_str}: {e}")
    
    user_id_str = str(user.id)
    if user_id_str in bot_data.data["ADMIN_MESSAGES"]:
        bot_data.data["ADMIN_MESSAGES"][user_id_str].update({
            "text": admin_msg,
            "media": media_info,
            "message_ids": message_ids,
            "edited": True,
            "edit_time": current_time
        })
    
    if editing_sliv_id in bot_data.data["SLIV_STATUS"]:
        bot_data.data["SLIV_STATUS"][editing_sliv_id]["admin_message_ids"] = message_ids
        bot_data.data["SLIV_STATUS"][editing_sliv_id]["edited"] = True
        bot_data.data["SLIV_STATUS"][editing_sliv_id]["edit_time"] = current_time
    
    bot_data.save_data()
    
    success_message = f"""🎉 *Отлично!*

*Статус твоего слива:* не прочитано 
*Отправлен:* {sliv_data.get('sent_time', 'Неизвестно')}
*Отредактирован:* {current_time}

Вы по-прежнему можете удалить свой слив."""

    user_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Удалить ❌", callback_data=f"delete_sliv_{editing_sliv_id}")]
    ])
    
    try:
        await bot.edit_message_text(
            chat_id=data.get("editing_chat_id"),
            message_id=data.get("editing_message_id"),
            text=success_message,
            parse_mode="Markdown",
            reply_markup=user_keyboard
        )
    except:
        await bot.send_message(
            chat_id=data.get("editing_chat_id"),
            text=success_message,
            parse_mode="Markdown",
            reply_markup=user_keyboard
        )
    
    await state.set_state(None)

async def handle_delete_sliv(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    
    sliv_id = callback.data.replace("delete_sliv_", "")
    
    sliv_data = None
    user_id = None
    
    if sliv_id in bot_data.data["SLIV_STATUS"]:
        sliv_data = bot_data.data["SLIV_STATUS"][sliv_id]
        user_id = sliv_data["user_id"]
    elif str(callback.from_user.id) in bot_data.data["ADMIN_MESSAGES"]:
        for uid, data in bot_data.data["ADMIN_MESSAGES"].items():
            if data.get("sliv_id") == sliv_id:
                sliv_data = data
                user_id = int(uid)
                break
    
    if not sliv_data:
        await callback.message.edit_text("❌ Слив не найден или уже был обработан")
        return
    
    if callback.from_user.id != user_id:
        await callback.answer("Это не ваш слив!", show_alert=True)
        return
    
    if sliv_data.get("status") != "not_viewed":
        await callback.message.edit_text("❌ Этот слив уже был просмотрен админами, удаление невозможно")
        return
    
    deleted_count = 0
    if "admin_message_ids" in sliv_data:
        for admin_id, msg_id in sliv_data["admin_message_ids"].items():
            try:
                await bot.delete_message(chat_id=int(admin_id), message_id=msg_id)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Ошибка удаления сообщения у админа {admin_id}: {e}")
    
    if sliv_id in bot_data.data["SLIV_STATUS"]:
        del bot_data.data["SLIV_STATUS"][sliv_id]
    
    for uid in list(bot_data.data["ADMIN_MESSAGES"].keys()):
        if bot_data.data["ADMIN_MESSAGES"][uid].get("sliv_id") == sliv_id:
            del bot_data.data["ADMIN_MESSAGES"][uid]
            break
    
    bot_data.save_data()
    
    await callback.message.edit_text("🎉 Слив удален.")
    
    logger.info(f"Слив {sliv_id} удален пользователем {user_id}. Удалено у {deleted_count} админов")

# ========== ФАКТЫ И МАТЕРИАЛЫ ==========
async def random_fact(message: Message):
    user_id = message.from_user.id
    now = datetime.now()
    
    if user_id in FACT_COOLDOWN and (now - FACT_COOLDOWN[user_id]).seconds < 300:
        await message.answer("⏳ Новый факт через 5 минут!")
        return

    await message.answer(f"📌 КИСС-ФАКТ:\n\n{random.choice(KABAN_FACTS)}")
    FACT_COOLDOWN[user_id] = now

async def show_materials(message: Message):
    text = """
<b>🥰 МАТЕРИАЛ ДЛЯ СПАМА</b>

<b>🥰 1. Стикер-пак:</b> <a href="https://t.me/addstickers/kab1nxdsex_by_TgEmodziBot">забрать</a>
<b>🥰 2. Еще пак:</b> <a href="https://t.me/addstickers/KxdExtraPack_by_TgEmodziBot">забрать</a>

<b> НЕ ДЛЯ СПАМА:</b>

1. <i>Стикеры:</i> <a href="https://t.me/addstickers/KissNovogodnij">забрать</a>
2. <i>Адаптив:</i> <a href="https://t.me/addstickers/AvettiKXD">забрать</a>

<i>🥰 Просьба не спамить стикерами НЕ для спама</i> 
    """
    await message.answer(text, parse_mode="HTML")

# ========== СПАМ-ФИЛЬТР ==========
async def spam_filter_add(message: Message):
    if message.from_user.id not in ADMINS:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Формат: /spam_filter @username причина")
        return
    
    username = args[1].lstrip('@').lower()
    reason = ' '.join(args[2:]) or "не указана"
    
    bot_data.data["SPAM_FILTER"][username] = reason
    bot_data.save_data()
    await message.answer(f"✅ @{username} добавлен в спам-фильтр. Причина: «{reason}»")

async def spam_filter_remove(message: Message):
    if message.from_user.id not in ADMINS:
        return
    
    username = ""
    if message.reply_to_message:
        username = message.reply_to_message.from_user.username or ""
    else:
        args = message.text.split()
        if len(args) > 1 and args[1].startswith('@'):
            username = args[1][1:].lower()
    
    if not username:
        await message.answer("❌ Формат: /unspam @username или ответ на сообщение")
        return
    
    if username in bot_data.data["SPAM_FILTER"]:
        del bot_data.data["SPAM_FILTER"][username]
        bot_data.save_data()
        await message.answer(f"✅ @{username} удалён из спам-фильтра")
    else:
        await message.answer("❌ Пользователь не в спам-фильтре")

async def show_lists(message: Message):
    if message.from_user.id not in ADMINS:
        return

    if not bot_data.data["SPAM_FILTER"]:
        await message.answer("🗒️ Список СФ пуст")
        return

    text = "🗒️ Список СФ \n\n"
    
    for i, (username, reason) in enumerate(bot_data.data["SPAM_FILTER"].items(), 1):
        user_link = f"[{username}](tg://user?id={username})"
        text += f"{i}. {user_link} | {reason}\n"

    await message.answer(text, parse_mode="Markdown")

# ========== СОЮЗЫ ==========
async def add_union(message: Message):
    if message.from_user.id not in ADMINS:
        return
    
    try:
        args = message.text.split()
        name = args[1]
        chat_id = int(args[2])
        admin_id = int(args[3])
        username = args[4] if len(args) > 4 else ""
        
        bot_data.data["UNION_HOUSES"][name] = {
            "chat_id": chat_id,
            "admin_id": admin_id,
            "username": username,
            "violation_reported": False
        }
        bot_data.save_data()
        await message.answer(f"✅ Чат {name} добавлен в союзные!")
    except:
        await message.answer("❌ Формат: /addunion название id_чата id_админа [username]")

async def list_unions(message: Message):
    if not bot_data.data["UNION_HOUSES"]:
        await message.answer("Список союзных чатов пуст.")
        return
    
    text = "✨ Список союзных чатов:\n\n"
    for name, data in bot_data.data["UNION_HOUSES"].items():
        text += f"{name} | ID: {data['chat_id']} | Админ: {data['admin_id']}\n"
    await message.answer(text)

async def check_chat_description(bot: Bot):
    for name, data in bot_data.data["UNION_HOUSES"].items():
        try:
            chat = await bot.get_chat(data["chat_id"])
            if UNION_REQUIREMENT not in chat.description:
                await notify_union_violation(bot, name, chat)
            elif data.get("violation_reported"):
                for admin_id in ADMINS:
                    await bot.send_message(admin_id, f"🔥 Чат \"{name}\" вернул приписку!")
                data["violation_reported"] = False
                bot_data.save_data()
        except Exception as e:
            logger.error(f"Ошибка проверки чата {name}: {e}")

async def notify_union_violation(bot: Bot, house_name: str, chat):
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=f"union_confirm_{chat.id}"),
            InlineKeyboardButton(text="Нет", callback_data=f"union_cancel_{chat.id}")
        ]
    ])
    await bot.send_message(
        chat_id=chat.id,
        text=f"🕵️‍♀️ Вы убрали приписку \"{UNION_REQUIREMENT}\" из описания. Расторгаем договор?",
        reply_markup=buttons
    )
    
    admin_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Перейти в ЛС", url=f"tg://user?id={bot_data.data['UNION_HOUSES'][house_name]['admin_id']}"),
            InlineKeyboardButton(text="Расторгнуть", callback_data=f"union_break_{chat.id}")
        ]
    ])
    
    for admin_id in ADMINS:
        await bot.send_message(
            admin_id,
            f"👮‍♂️ Чат \"{house_name}\" убрал приписку!\nID: {chat.id}",
            reply_markup=admin_buttons
        )

async def union_button_handler(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    data = callback.data
    
    if data.startswith("union_confirm_"):
        chat_id = int(data.split("_")[2])
        
        house_data = None
        house_name = None
        for name, data in bot_data.data["UNION_HOUSES"].items():
            if data["chat_id"] == chat_id:
                house_data = data
                house_name = name
                break
        
        if not house_data:
            await callback.message.edit_text("❌ Чат не найден в союзах")
            return
        
        if callback.from_user.id != house_data["admin_id"]:
            await callback.answer("ало, ты не влд...", show_alert=True)
            return
            
        await callback.message.edit_text(f"😿 Чат {house_name} расторгнул союз.")
        bot_data.data["UNION_HOUSES"][house_name]["violation_reported"] = True
        bot_data.save_data()
        
    elif data.startswith("union_cancel_"):
        chat_id = int(data.split("_")[2])
        
        house_data = None
        house_name = None
        for name, data in bot_data.data["UNION_HOUSES"].items():
            if data["chat_id"] == chat_id:
                house_data = data
                house_name = name
                break
        
        if not house_data:
            await callback.message.edit_text("❌ Чат не найден в союзах")
            return

        if callback.from_user.id != house_data["admin_id"]:
            await callback.answer("ало, ты не влд ...", show_alert=True)
            return
            
        await callback.message.edit_text("✅ Договор сохранён. Верните приписку в описание!")
        
    elif data.startswith("union_break_"):
        chat_id = int(data.split("_")[2])
        house_name = None
        for k, v in bot_data.data["UNION_HOUSES"].items():
            if v["chat_id"] == chat_id:
                house_name = k
                break
        
        if house_name:
            await bot.send_message(chat_id, "😣 Администрация расторгла договор. Покидаю чат!")
            await bot.leave_chat(chat_id)
            del bot_data.data["UNION_HOUSES"][house_name]
            bot_data.save_data()
            
            for admin_id in ADMINS:
                await bot.send_message(admin_id, f"💢 Союз с {house_name} расторгнут!")

# ========== УВЕДОМЛЕНИЯ О ВЫХОДАХ ==========
async def toggle_leave_notifications(message: Message):
    chat_id = str(message.chat.id)
    command = message.text.lower().strip()

    if command == "+ув":
        bot_data.data["LEAVE_NOTIFICATIONS"][chat_id] = True
        bot_data.save_data()
        await message.answer(f"{EMOJI_LEAVE_ON} Уведомления о выходах работают")
    elif command == "-ув":
        bot_data.data["LEAVE_NOTIFICATIONS"][chat_id] = False
        bot_data.save_data()
        await message.answer(f"{EMOJI_LEAVE_OFF} Уведомления о выходах выключены")

async def set_custom_leave_message(message: Message):
    try:
        chat_id = str(message.chat.id)
        message_text = message.text
        
        if not message_text.startswith('+фув ') or len(message_text) < 6:
            await message.answer("❌ Формат: +фув ваш текст сообщения")
            return
        
        new_message = message_text[5:].strip()
        if not new_message:
            await message.answer("❌ Сообщение не может быть пустым!")
            return

        bot_data.data["LEAVE_MESSAGES"][chat_id] = new_message
        bot_data.save_data()
        
        example_message = f'<a href="tg://user?id={message.from_user.id}">Username</a> {new_message}'
        
        await message.answer(
            f"✌️😗 Хорошо, буду так прощаться\n\nПример:\n{example_message}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка в set_custom_leave_message: {e}")

async def handle_left_member(message: Message, bot: Bot):
    try:
        if not message.left_chat_member:
            return
            
        chat_id = str(message.chat.id)
        left_user = message.left_chat_member

        if left_user.id == bot.id:
            return  

        if not bot_data.data["LEAVE_NOTIFICATIONS"].get(chat_id, False):
            return

        leave_message = bot_data.data["LEAVE_MESSAGES"].get(chat_id, "✌️😗 прощаааааййй {username}...пора..пока..завтра будет лучше чем ВЧЕРА!")
        
        user_name = left_user.first_name
        if left_user.username:
            user_name = f"@{left_user.username}"

        formatted_message = leave_message.replace("{user_link}", user_name)
        formatted_message = formatted_message.replace("{username}", user_name)
        
        try:
            chat = await bot.get_chat(int(chat_id))
            if chat.get_members_count() > 100:
                clean_message = re.sub(r'<[^>]+>', '', formatted_message)
                await bot.send_message(chat_id=int(chat_id), text=clean_message)
            else:
                await bot.send_message(chat_id=int(chat_id), text=formatted_message, parse_mode="HTML")
        except Exception as e:
            try:
                clean_message = re.sub(r'<[^>]+>', '', formatted_message)
                await bot.send_message(chat_id=int(chat_id), text=clean_message)
            except Exception as inner_e:
                logger.error(f"Не удалось отправить уведомление о выходе: {inner_e}")
    except Exception as e:
        logger.error(f"Ошибка в handle_left_member: {e}")

# ========== ИГРЫ ==========
async def guess_number_start(message: Message):
    chat_id = message.chat.id
    GUESS_NUMBER[chat_id] = {
        "target": random.randint(1, 100),
        "attempts": 5,
        "last_guess": None
    }
    await message.answer(
        "🎯 Игра началась! Я загадал число от 1 до 100. "
        "Попробуй угадать за 5 попыток!"
    )

async def guess_number_play(message: Message):
    chat_id = message.chat.id
    
    if chat_id not in GUESS_NUMBER:
        return

    if not message.text.strip().isdigit():
        return

    try:
        guess = int(message.text.strip())
        game = GUESS_NUMBER[chat_id]
        
        if guess == game["target"]:
            await message.answer(
                f"🎉 НУ НАКОНЕЦ-ТО, ПОЗДРАВЛЯЮ, {message.from_user.first_name}! "
                f"Ты угадал число {game['target']}!"
            )
            del GUESS_NUMBER[chat_id]
            return
            
        game["attempts"] -= 1
        
        if game["attempts"] <= 0:
            await message.answer(
                f"💀 Игра окончена, ЛОШАРА! Число было {game['target']}. "
                "Попробуй ещё раз!"
            )
            del GUESS_NUMBER[chat_id]
        else:
            hint = "Большеееее!!!!" if guess < game["target"] else "МеньшеЕЕЕ!!"
            await message.answer(
                f"{hint}! Осталось попыток: {game['attempts']}"
            )
    except Exception as e:
        logger.error(f"Ошибка в guess_number_play: {e}")

async def kmk_game(message: Message):
    try:
        text = message.text
        options = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+[\.\)\-]\s*.+', line):
                option_text = re.sub(r'^\d+[\.\)\-]\s*', '', line).strip()
                if option_text:
                    options.append(option_text)
        
        if len(options) < 3:
            await message.answer("❌ Нужно минимум 3 варианта в формате:\n1. Вариант1\n2. Вариант2\n3. Вариант3")
            return
        
        shuffled = random.sample(options, 3)
        response = (
            "💌  Я выбираю... \n\n"
            f"💋 Поцеловать: {shuffled[0]}\n"
            f"💍 Брак: {shuffled[1]}\n"
            f"🔪 Убить: {shuffled[2]}"
        )
        await message.answer(response, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка в KMK игре: {e}")
        await message.answer("❌ Не могу разобрать варианты")

# ========== RP КОМАНДЫ ==========
async def rp_command(message: Message):
    try:
        command = message.text.split()[0][1:].lower()
        target = None
        
        if len(message.text.split()) > 1:
            target = message.text.split()[1].lstrip('@')
        elif message.reply_to_message:
            target = message.reply_to_message.from_user.username or str(message.reply_to_message.from_user.id)
        
        if not target:
            await message.answer("❌ Укажите цель: '/команда @username' или ответьте на сообщение")
            return

        from_user = message.from_user
        from_name = f"@{from_user.username}" if from_user.username else from_user.first_name
        to_name = f"@{target}" if not target.isdigit() else f"user_{target}"
        
        actions = {
            "убить": f"{from_name} убил(а) беспощадно {to_name} ☠️",
            "найти": f"{from_name} нашёл(а) данные {to_name} 🕵️",
            "заспамить": f"{from_name} заспамил(а) чат {to_name} 📢",
            "торт": f"{from_name} кинул(а) торт в {to_name} 🎂",
            "забыть": f"{from_name} забыл(а) {to_name} 🧠",
            "купить": f"{from_name} купил(а) {to_name} за $100к 💰",
            "влюбить": f"{from_name} влюбил(а) {to_name} 💘"
        }

        await message.answer(
            actions.get(command, "❌ Неизвестная команда"),
            reply_markup=get_keyboard(message.chat.type)
        )
    except Exception as e:
        logger.error(f"Ошибка в RP команде: {e}")
        await message.answer("❌ Ошибка. Используйте: /команда @username")

# ========== KISS КОМАНДЫ ==========
async def handle_kiss_command(message: Message):
    message_text = message.text.lower()
    user = message.from_user
    mentioned_user = None
    mentioned_user_id = None

    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mentioned_username = message_text[entity.offset:entity.offset + entity.length]
                mentioned_user = mentioned_username
                if message.reply_to_message:
                    mentioned_user_id = message.reply_to_message.from_user.id
                break
    
    match = re.match(r'кисс,\s*(\w+)\s*(?:меня|@?\w+)', message_text)
    
    if match:
        action = match.group(1)
        
        if action in KISS_ACTIONS:
            if mentioned_user and mentioned_user_id:
                target = f'<a href="tg://user?id={mentioned_user_id}">{mentioned_user}</a>'
            else:
                target = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
            
            action_data = KISS_ACTIONS[action]

            response = (
                f"<i>Хорошо!</i>\n"
                f"<b>{action_data['response'].format(username=target)}</b> {action_data['emoji']}"
            )
            
            await message.answer(response, parse_mode='HTML', disable_web_page_preview=True)

async def handle_whoami_command(message: Message):
    user = message.from_user
    
    random_responses = [
        "рейдер", "бомжара", "нищий", "говноед", "фанат", "кумир", "чья-то мама", "гей", 
        "лесбиянка", "под спайсом", "учитель", "майор", "сопля", "котогусеница", "ведьма", 
        "никто", "жирный", "АНТИрейдер", "президент", "повар", "дед", "Тарталья", "мизуки", 
        "кокоми", "душа елены Владимировны", "печенька", "солнышко", "зайка", "котенок", 
        "обкуренный", "книголюб", "изгой", "король", "лидер", "аластор", "манипулятор", "куколд"
    ]
    
    random_response = random.choice(random_responses)
    user_link = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
    
    response = f"<i>Сегодня</i> {user_link} <b>{random_response}</b>! <i>Гордись этим.</i>"
    await message.answer(response, parse_mode='HTML', disable_web_page_preview=True)

async def handle_poll_command(message: Message, bot: Bot):
    message_text = message.text
    parts = message_text.split('|')
    
    if len(parts) < 3:
        await message.answer(
            "📊 <b>Формат создания опроса:</b>\n"
            "<code>кисс, опрос Вопрос? | Вариант 1 | Вариант 2 | Вариант 3</code>",
            parse_mode='HTML'
        )
        return
    
    question = parts[0].replace('кисс, опрос', '').strip()
    options = [opt.strip() for opt in parts[1:4]]
    
    await bot.send_poll(
        chat_id=message.chat.id,
        question=question,
        options=options,
        is_anonymous=False
    )

async def handle_compliment_command(message: Message):
    user = message.from_user
    target_user = user 
    target_user_id = user.id

    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mentioned_username = message.text[entity.offset:entity.offset + entity.length]
                try:
                    if message.reply_to_message:
                        target_user = message.reply_to_message.from_user
                        target_user_id = target_user.id
                except:
                    target_user = user
                break
    
    target_link = f'<a href="tg://user?id={target_user_id}">{target_user.first_name}</a>'
    
    compliments = [
        f"{target_link} - просто солнышко! 🌟",
        f"{target_link} сегодня невероятно прекрасн! ✨",
        f"У {target_link} самые красивые глаза в этом чате! 👀💫",
        f"{target_link} умнее всех! 🧠",
        f"{target_link} - источник вдохновения! 💖"
    ]
    
    response = f"{random.choice(compliments)}"
    await message.answer(response, parse_mode='HTML', disable_web_page_preview=True)

async def handle_insult_command(message: Message):
    user = message.from_user
    target_user = user.first_name
    
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                target_user = message.text[entity.offset:entity.offset + entity.length]
                break
    
    insults = [
        f"{target_user} сегодня похож на мокрую курицу! 🐔",
        f"{target_user} - ходячая катастрофа! 🌪️",
        f"У {target_user} вкус как у таксиста! 🚕",
        f"{target_user} - причина, почему у инструкторов есть кнопка 'паника'! 🚨"
    ]
    
    response = f"<i>С удовольствием!</i>\n{random.choice(insults)} 😈"
    await message.answer(response, parse_mode='HTML')

async def handle_calc_command(message: Message):
    message_text = message.text
    expression = message_text.replace('кисс, посчитай', '').strip()
    
    try:
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Недопустимые символы")
        
        result = eval(expression)
        response = f"<i>Решаю...</i>\n<b>{expression} = {result}</b> 🧮"
    except Exception as e:
        response = "<i>Не могу посчитать!</i> 😅\n<b>Формат:</b> <code>кисс, посчитай 5+10</code>"
    
    await message.answer(response, parse_mode='HTML')

async def handle_gossip_command(message: Message, bot: Bot):
    chat_id = message.chat.id
    
    try:
        chat_members = []
        async for member in bot.get_chat_members(chat_id):
            if not member.user.is_bot and member.user.username:
                chat_members.append(member.user)
        
        if len(chat_members) < 1:
            await message.answer("<i>В чате нет участников для сплетен!</i> 😅", parse_mode='HTML')
            return
        
        gossip_templates = [
            "@{user1} тайно страпонит @{user2} 💞",
            "@{user1} прогулял(а) алгебру с @{user2} в туалете, где курили ашки. 🤡",
            "в школьной туалете нашли тест на беременность, оттуда последним выходила @{user1} ✨"
        ]
        
        selected_gossip = random.choice(gossip_templates)
        
        if selected_gossip.count('{user') == 1:
            selected_users = random.sample(chat_members, 1)
            user1 = selected_users[0]
            gossip_text = selected_gossip.format(user1=user1.username, user2="")
        else:
            if len(chat_members) >= 2:
                selected_users = random.sample(chat_members, 2)
                user1, user2 = selected_users[0], selected_users[1]
                gossip_text = selected_gossip.format(user1=user1.username, user2=user2.username)
            else:
                user1 = chat_members[0]
                gossip_text = selected_gossip.format(user1=user1.username, user2="неизвестный_участник")
        
        response = f"<b>СПЛЕТНЯ ДНЯ</b>\n\n{gossip_text}"
    except Exception as e:
        logger.error(f"Ошибка в сплетнях: {e}")
        response = "<i>Что-то пошло не так со сплетнями!</i> 😅"
    
    await message.answer(response, parse_mode='HTML', disable_web_page_preview=True)

# ========== НАПОМИНАНИЯ ==========
async def add_reminder(message: Message, bot: Bot):
    try:
        message_text = message.text
        parts = message_text.split()
        
        if len(parts) < 3:
            await message.answer("❌ Формат: +нп время текст_напоминания\nПример: +нп 1ч 12м вытащить курицу из духовки")
            return

        time_parts = []
        reminder_parts = []
        found_time = False
        
        for part in parts[1:]:
            if re.search(r'(\d+[чмдс])', part.lower()) and not found_time:
                time_parts.append(part)
            else:
                found_time = True
                reminder_parts.append(part)
        
        if not time_parts:
            await message.answer("❌ Неверный формат времени.")
            return
        
        time_str = ' '.join(time_parts)
        reminder_text = ' '.join(reminder_parts).strip()
        
        if not reminder_text:
            await message.answer("❌ Укажите текст напоминания!")
            return
        
        time_delta = parse_time(time_str)
        
        if not time_delta:
            await message.answer("❌ Неверный формат времени.")
            return

        delay_seconds = time_delta.total_seconds()
        
        # ✅ ИСПРАВЛЕНО - правильный способ создать отложенную задачу
        async def reminder_job():
            await asyncio.sleep(delay_seconds)
            await send_reminder(bot, message.from_user.id, reminder_text)
        
        asyncio.create_task(reminder_job())
        
        await message.answer(f"⏳ Хорошо, я напомню тебе '{reminder_text}' через {time_str} ...")
    except Exception as e:
        logger.error(f"Ошибка в add_reminder: {e}")
        await message.answer("❌ Ошибка при создании напоминания")

# ========== КАСТОМНЫЕ ФОТО И ФРАЗЫ ==========
async def set_custom_photo(message: Message):
    try:
        user = message.from_user
        user_id = str(user.id)
        
        initialize_user_reputation(user.id, user.id in ADMINS, user.id == OWNER_ID)
        
        user_data = bot_data.data["REPUTATION_DATA"].get(user_id, {})
        user_status = user_data.get("status", "кабанчик")
        
        if user_status not in ["любимчик", "админ", "модер", "владелец"]:
            await message.answer("❌ Только любимчики и выше могут менять фото!")
            return
        
        if not message.photo:
            await message.answer("❌ Прикрепите фото к команде!")
            return

        photo_id = message.photo[-1].file_id
        bot_data.data["CUSTOM_PHOTOS_FILE_ID"][user_id] = photo_id
        bot_data.save_data()
        
        await message.answer("📸 Отличный снимок! Добавил его тебе в репутацию")
    except Exception as e:
        logger.error(f"Ошибка в set_custom_photo: {e}")
        await message.answer("❌ Ошибка при установке фото")

async def remove_custom_photo(message: Message):
    try:
        user = message.from_user
        user_id = str(user.id)
        
        if user_id in bot_data.data["CUSTOM_PHOTOS_FILE_ID"]:
            del bot_data.data["CUSTOM_PHOTOS_FILE_ID"][user_id]
            bot_data.save_data()
            await message.answer("📷 Я вернул обычное фото")
        else:
            await message.answer("❌ У вас нет установленного кастомного фото")
    except Exception as e:
        logger.error(f"Ошибка в remove_custom_photo: {e}")
        await message.answer("❌ Ошибка при удалении фото")

async def set_custom_phrase(message: Message):
    try:
        user = message.from_user
        user_id = str(user.id)
        
        message_text = message.text
        if not message_text.startswith('+фр ') or len(message_text) < 5:
            await message.answer("❌ Формат: +фр ваш текст фразы")
            return
        
        new_phrase = message_text[4:].strip()
        if not new_phrase:
            await message.answer("❌ Фраза не может быть пустой!")
            return

        bot_data.data["CUSTOM_PHRASES"][user_id] = new_phrase
        bot_data.save_data()
        await message.answer("🎤 Фраза была добавлена =)")
    except Exception as e:
        logger.error(f"Ошибка в set_custom_phrase: {e}")
        await message.answer("❌ Ошибка при установке фразы")

async def reset_custom_phrase(message: Message):
    try:
        user = message.from_user
        user_id = str(user.id)
        
        if user_id in bot_data.data["CUSTOM_PHRASES"]:
            del bot_data.data["CUSTOM_PHRASES"][user_id]
            bot_data.save_data()
            await message.answer("🎤 Фраза сброшена на стандартную =)")
        else:
            await message.answer("❌ У вас нет установленной кастомной фразы")
    except Exception as e:
        logger.error(f"Ошибка в reset_custom_phrase: {e}")
        await message.answer("❌ Ошибка при сбросе фразы")

# ========== ПРОЧИЕ КОМАНДЫ ==========
async def kxd_response(message: Message):
    text = message.text.lower()
    responses = {
        "kxd!": "к сливам готов 😸",
        "кхд!": "к сливам готов 😽",
        "kxd": "в порядке 😾",
        "кхд": "в порядке 🙀"
    }
    await message.answer(responses.get(text, "да, кхд"))

async def tezy_response(message: Message):
    await message.answer("пошел нахуй")

async def handle_kaban_hello(message: Message):
    text = message.text.lower().strip()
    triggers = ["кисс, как дела", "кисс как дела"]
    
    if any(trigger in text for trigger in triggers):
        responses = [
            "Привет! Всё хорошо, а у тебя? 👀",
            "🎶 Я очень рад, Я депутат. послушный верный солдаат",
            "У меня всё плохо, я умираю ... 😭"
        ]
        await message.answer(random.choice(responses))

async def random_hello_response(message: Message):
    responses = [
        ("привет! все хорошо, а у тебя что? 👀", 30),
        (".................................", 5),
        ("у меня все плохо я умираю...", 20)
    ]
    response = random.choices(*zip(*responses))[0]
    await message.answer(response)

async def call_users(message: Message):
    message_text = message.text.lower()
    user = message.from_user
    
    call_type = None
    for key in COMMAND_TO_USERS:
        if f"позвать {key}" in message_text:
            call_type = key
            break
    
    if not call_type:
        return
    
    users_to_mention = COMMAND_TO_USERS[call_type]
    mentions = ' '.join(users_to_mention) + ' 👋\n'
    caller_info = f"😈 Созыв от: [{user.full_name}](tg://user?id={user.id})"
    final_message = mentions + caller_info
    
    await message.answer(text=final_message, parse_mode='Markdown', disable_web_page_preview=True)

# ========== МОДЕРАЦИЯ В ГРУППАХ ==========
async def ban_command(message: Message, bot: Bot):
    """Блокирует пользователя в чате"""
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("❌ Эта команда работает только в группах!")
        return
    
    user = message.from_user
    if not is_admin_or_moderator(user.id):
        await message.answer("❌ У вас нет прав на использование этой команды!")
        return
    
    target_user = None
    reason = ""
    
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            reason = parts[1].strip()
    else:
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    username = message.text[entity.offset:entity.offset + entity.length].lstrip('@')
                    try:
                        chat = message.chat
                        async for member in bot.get_chat_administrators(chat.id):
                            if member.user.username and member.user.username.lower() == username.lower():
                                target_user = member.user
                                break
                    except:
                        pass
                    break
        
        if not target_user:
            await message.answer("❌ Ответьте на сообщение пользователя или укажите @username")
            return
    
    if not target_user:
        await message.answer("❌ Не удалось определить пользователя")
        return
    
    if target_user.id == bot.id:
        await message.answer("❌ Не могу забанить самого себя!")
        return
    
    chat_id = message.chat.id
    
    try:
        bot_member = await message.chat.get_member(bot.id)
        if bot_member.status not in ['administrator', 'creator'] or not bot_member.can_restrict_members:
            await message.answer("❌ У бота нет прав банить участников!")
            return
        
        await bot.ban_chat_member(chat_id, target_user.id)
        
        global ban_data
        chat_id_str = str(chat_id)
        user_id_str = str(target_user.id)
        
        if chat_id_str not in ban_data["banned"]:
            ban_data["banned"][chat_id_str] = {}
        
        ban_data["banned"][chat_id_str][user_id_str] = {
            "user_id": target_user.id,
            "admin_id": user.id,
            "reason": reason,
            "timestamp": datetime.now().timestamp(),
            "admin_name": user.full_name,
            "target_name": target_user.full_name
        }
        save_ban_data(ban_data)
        
        target_mention = get_user_mention(target_user.id, target_user.first_name)
        admin_mention = get_user_mention(user.id, user.first_name)
        
        if reason:
            message_text = f"""
<tg-emoji emoji-id="4999015678238262018">🥰</tg-emoji> <b>Пользователь {target_mention} забанен</b>
Причина: {reason}
<tg-emoji emoji-id="5253780051471642059">🥰</tg-emoji> Админ: {admin_mention}
"""
        else:
            message_text = f"""
<tg-emoji emoji-id="4999015678238262018">🥰</tg-emoji> <b>Пользователь {target_mention} забанен</b>
<tg-emoji emoji-id="5253780051471642059">🥰</tg-emoji> Админ: {admin_mention}
"""
        await message.answer(message_text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка при бане: {e}")
        await message.answer(f"❌ Не удалось забанить пользователя: {e}")

async def unban_command(message: Message, bot: Bot):
    """Разблокирует пользователя в чате"""
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("❌ Эта команда работает только в группах!")
        return
    
    user = message.from_user
    if not is_admin_or_moderator(user.id):
        await message.answer("❌ У вас нет прав на использование этой команды!")
        return
    
    target_user = None
    
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    else:
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    await message.answer("❌ Для разбана используйте ответ на сообщение пользователя")
                    return
    
    if not target_user:
        await message.answer("❌ Ответьте на сообщение пользователя")
        return
    
    chat_id = message.chat.id
    
    try:
        bot_member = await message.chat.get_member(bot.id)
        if bot_member.status not in ['administrator', 'creator'] or not bot_member.can_restrict_members:
            await message.answer("❌ У бота нет прав разбанивать участников!")
            return
        
        await bot.unban_chat_member(chat_id, target_user.id)
        
        global ban_data
        chat_id_str = str(chat_id)
        user_id_str = str(target_user.id)
        
        if chat_id_str in ban_data["banned"] and user_id_str in ban_data["banned"][chat_id_str]:
            del ban_data["banned"][chat_id_str][user_id_str]
            if not ban_data["banned"][chat_id_str]:
                del ban_data["banned"][chat_id_str]
            save_ban_data(ban_data)
        
        target_mention = get_user_mention(target_user.id, target_user.first_name)
        admin_mention = get_user_mention(user.id, user.first_name)
        
        message_text = f"<b>Пользователь {target_mention} разбанен</b>\nАдмин: {admin_mention}"
        await message.answer(message_text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка при разбане: {e}")
        await message.answer(f"❌ Не удалось разбанить пользователя: {e}")

async def mute_command(message: Message, bot: Bot):
    """Ограничивает возможность писать в чат на определенное время"""
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("❌ Эта команда работает только в группах!")
        return
    
    user = message.from_user
    if not is_admin_or_moderator(user.id):
        await message.answer("❌ У вас нет прав на использование этой команды!")
        return
    
    target_user = None
    reason = ""
    mute_duration = timedelta(hours=1)
    
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        
        text_without_command = message.text
        if text_without_command.startswith('/мут'):
            text_without_command = text_without_command[4:].strip()
        elif text_without_command.startswith('мут'):
            text_without_command = text_without_command[3:].strip()
        
        if text_without_command:
            words = text_without_command.split()
            time_str = ""
            reason_parts = []
            
            for word in words:
                if re.search(r'\d+[чмд]', word.lower()):
                    time_str += " " + word
                else:
                    reason_parts.append(word)
            
            if time_str:
                parsed_time = parse_time(time_str)
                if parsed_time:
                    mute_duration = parsed_time
            
            if reason_parts:
                reason = " ".join(reason_parts)
    else:
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    await message.answer("❌ Для мута используйте ответ на сообщение пользователя")
                    return
    
    if not target_user:
        await message.answer("❌ Ответьте на сообщение пользователя")
        return
    
    if target_user.id == bot.id:
        await message.answer("❌ Не могу замутить самого себя!")
        return
    
    chat_id = message.chat.id
    
    try:
        bot_member = await message.chat.get_member(bot.id)
        if bot_member.status not in ['administrator', 'creator'] or not bot_member.can_restrict_members:
            await message.answer("❌ У бота нет прав мутить участников!")
            return
        
        until_date = datetime.now() + mute_duration
        
        await bot.restrict_chat_member(
            chat_id,
            target_user.id,
            until_date=until_date,
            permissions=ChatPermissions(can_send_messages=False)
        )
        
        global ban_data
        chat_id_str = str(chat_id)
        user_id_str = str(target_user.id)
        
        if chat_id_str not in ban_data["muted"]:
            ban_data["muted"][chat_id_str] = {}
        
        ban_data["muted"][chat_id_str][user_id_str] = {
            "user_id": target_user.id,
            "admin_id": user.id,
            "until": until_date.timestamp(),
            "reason": reason,
            "timestamp": datetime.now().timestamp(),
            "admin_name": user.full_name,
            "target_name": target_user.full_name
        }
        save_ban_data(ban_data)
        
        target_mention = get_user_mention(target_user.id, target_user.first_name)
        admin_mention = get_user_mention(user.id, user.first_name)
        
        duration_str = []
        if mute_duration.days > 0:
            duration_str.append(f"{mute_duration.days} дн.")
        hours = mute_duration.seconds // 3600
        if hours > 0:
            duration_str.append(f"{hours} ч.")
        minutes = (mute_duration.seconds % 3600) // 60
        if minutes > 0:
            duration_str.append(f"{minutes} мин.")
        
        duration_display = " ".join(duration_str) if duration_str else "1 час"
        
        if reason:
            message_text = f"<b>Пользователь {target_mention} замучен на {duration_display}</b>\nПричина: {reason}\nАдмин: {admin_mention}"
        else:
            message_text = f"<b>Пользователь {target_mention} замучен на {duration_display}</b>\nАдмин: {admin_mention}"
        await message.answer(message_text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка при муте: {e}")
        await message.answer(f"❌ Не удалось замутить пользователя: {e}")

async def unmute_command(message: Message, bot: Bot):
    """Снимает ограничения на отправку сообщений"""
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("❌ Эта команда работает только в группах!")
        return
    
    user = message.from_user
    if not is_admin_or_moderator(user.id):
        await message.answer("❌ У вас нет прав на использование этой команды!")
        return
    
    target_user = None
    
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    else:
        await message.answer("❌ Ответьте на сообщение пользователя")
        return
    
    if not target_user:
        await message.answer("❌ Не удалось определить пользователя")
        return
    
    chat_id = message.chat.id
    
    try:
        bot_member = await message.chat.get_member(bot.id)
        if bot_member.status not in ['administrator', 'creator'] or not bot_member.can_restrict_members:
            await message.answer("❌ У бота нет прав размучивать участников!")
            return
        
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_manage_topics=False
        )
        
        await bot.restrict_chat_member(chat_id, target_user.id, permissions=permissions)
        
        global ban_data
        chat_id_str = str(chat_id)
        user_id_str = str(target_user.id)
        
        if chat_id_str in ban_data["muted"] and user_id_str in ban_data["muted"][chat_id_str]:
            del ban_data["muted"][chat_id_str][user_id_str]
            if not ban_data["muted"][chat_id_str]:
                del ban_data["muted"][chat_id_str]
            save_ban_data(ban_data)
        
        target_mention = get_user_mention(target_user.id, target_user.first_name)
        admin_mention = get_user_mention(user.id, user.first_name)
        
        message_text = f"<b>Пользователь {target_mention} может снова писать</b>\nАдмин: {admin_mention}"
        await message.answer(message_text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка при размуте: {e}")
        await message.answer(f"❌ Не удалось размутить пользователя: {e}")

# ========== НЕЙРОСЕТЬ ==========
async def start_chat(message: Message, state: FSMContext):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    user_sessions[user_id] = {
        'active': True,
        'chat_type': message.chat.type
    }
    
    await message.answer(
        "🎃 Готов к разговору! О чем поболтаем?\n"
        "Как захочешь прекратить, напиши \"кисс, спать\""
    )

async def stop_chat(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    await message.answer("💤 Сладких снов! Жду нашего следующего разговора!")

def get_ai_response(message_text, user_id):
    try:
        logger.info(f"🔄 Отправляем в нейросеть: {message_text}")
        
        payload = {
            "inputs": message_text,
            "parameters": {
                "max_length": 150,
                "temperature": 0.9,
                "do_sample": True
            }
        }
        
        response = requests.post(MODEL_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                ai_response = result[0].get('generated_text', '')
                if ai_response:
                    if message_text in ai_response:
                        clean_response = ai_response.replace(message_text, "").strip()
                        if clean_response:
                            return clean_response
                    return ai_response
            return "Интересно! Расскажи мне больше."
        elif response.status_code == 503:
            return "Нейросеть просыпается... подожди секунду и напиши еще раз! ⏳"
        else:
            return try_gpt2_fallback(message_text)
    except Exception as e:
        logger.error(f"❌ Ошибка в нейросети: {e}")
        return "Давай поговорим! Что у тебя нового? 🎄"

def try_gpt2_fallback(message_text):
    try:
        gpt2_url = "https://api-inference.huggingface.co/models/gpt2"
        payload = {
            "inputs": message_text,
            "parameters": {
                "max_length": 100,
                "temperature": 0.8,
                "do_sample": True
            }
        }
        response = requests.post(gpt2_url, headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                ai_response = result[0].get('generated_text', '')
                if ai_response and len(ai_response) > 10:
                    if message_text in ai_response:
                        return ai_response.replace(message_text, "").strip()
                    return ai_response
        return "Расскажи мне что-нибудь интересное! ✨"
    except Exception as e:
        logger.error(f"❌ Ошибка GPT2: {e}")
        return "Привет! Как твои дела? 🎃"

# ========== ЛИП (ОБМЕН КОНФЕТ НА МОНЕТЫ) ==========
async def lip_exchange(message: Message, state: FSMContext):
    try:
        user = message.from_user
        user_id_str = str(user.id)
        
        initialize_user_reputation(user.id, user.id in ADMINS, user.id == OWNER_ID)
        
        rep_data = bot_data.data["REPUTATION_DATA"].get(user_id_str, {})
        current_candies = rep_data.get("candies", 0)
        
        message_text = message.text.lower()
        match = re.search(r'лип\s+(\d+)', message_text)
        
        if not match:
            await message.answer(
                "❌ Формат команды: Лип [число монеток]\n"
                "Пример: Лип 3\n\n"
                "Курс обмена: 5 конфеток = 1 монетка"
            )
            return
        
        coins_requested = int(match.group(1))
        
        if coins_requested < 1:
            await message.answer("❌ Минимум: 1 монетка")
            return
        
        candies_needed = coins_requested * 5
        
        if candies_needed > 10000:
            await message.answer(f"❌ Максимальный обмен: 10.000 конфеток\nДля {coins_requested} монеток нужно {candies_needed} конфеток")
            return
        
        if candies_needed < 5:
            await message.answer("❌ Минимальный обмен: 5 конфеток (1 монетка)")
            return
        
        if current_candies < candies_needed:
            await message.answer(f"❌ Недостаточно конфеток!\nУ вас есть: {current_candies}\nНужно: {candies_needed}")
            return
        
        transaction_id = f"{user.id}_{datetime.now().timestamp()}"
        await state.update_data({
            transaction_id: {
                "user_id": user.id,
                "user_id_str": user_id_str,
                "coins_requested": coins_requested,
                "candies_needed": candies_needed,
                "remaining_candies": current_candies - candies_needed
            }
        })
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Перевод ✔", callback_data=f"confirm_{transaction_id}"),
                InlineKeyboardButton(text="Назад ✖", callback_data=f"cancel_{transaction_id}")
            ]
        ])
        
        await message.answer(
            f"🍫 Переводим {candies_needed} конфеток в {coins_requested} монеток?\n"
            f"У вас останется: *{current_candies - candies_needed}* конфеток.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка в lip_exchange: {e}")
        await message.answer("❌ Ошибка. Используйте: Лип [число]")

async def handle_lip_buttons(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = callback.data
    
    if data.startswith("confirm_"):
        transaction_id = data.split("_", 1)[1]
        await process_lip_confirmation(callback, state, transaction_id)
    elif data.startswith("cancel_"):
        transaction_id = data.split("_", 1)[1]
        await process_lip_cancellation(callback, state, transaction_id)

async def process_lip_confirmation(callback: CallbackQuery, state: FSMContext, transaction_id: str):
    state_data = await state.get_data()
    transaction_data = state_data.get(transaction_id)
    
    if not transaction_data:
        await callback.message.edit_text("❌ Транзакция не найдена или устарела")
        return
    
    user_id_str = transaction_data["user_id_str"]
    coins_requested = transaction_data["coins_requested"]
    candies_needed = transaction_data["candies_needed"]
    remaining_candies = transaction_data["remaining_candies"]
    
    current_candies = bot_data.data["REPUTATION_DATA"].get(user_id_str, {}).get("candies", 0)
    
    if current_candies < candies_needed:
        await callback.message.edit_text(f"❌ Недостаточно конфеток!\nСейчас у вас: {current_candies}\nНужно: {candies_needed}")
        return
    
    current_coins = bot_data.data["REPUTATION_DATA"].get(user_id_str, {}).get("coins", 0)
    
    bot_data.data["REPUTATION_DATA"][user_id_str]["candies"] = remaining_candies
    bot_data.data["REPUTATION_DATA"][user_id_str]["coins"] = current_coins + coins_requested
    bot_data.save_data()
    
    await callback.message.edit_text(
        f"✅ Успешно!\n"
        f"Вы перевели {candies_needed} конфеток в {coins_requested} монеток.\n\n"
        f"🍫 Осталось конфеток: {remaining_candies}\n"
        f"❄ Всего монеток: {current_coins + coins_requested}",
        parse_mode="Markdown"
    )
    
    temp_data = await state.get_data()
    if transaction_id in temp_data:
        temp_data.pop(transaction_id)
        await state.set_data(temp_data)

async def process_lip_cancellation(callback: CallbackQuery, state: FSMContext, transaction_id: str):
    await callback.message.delete()
    temp_data = await state.get_data()
    if transaction_id in temp_data:
        temp_data.pop(transaction_id)
        await state.set_data(temp_data)
    await callback.message.answer("❌ Перевод отменен")

# ========== КОНФИСКАЦИЯ КОНФЕТ ==========
async def confiscate_candies(message: Message):
    try:
        confiscator = message.from_user
        confiscator_id = confiscator.id
        
        if confiscator_id not in ADMINS and confiscator_id != OWNER_ID:
            await message.answer("❌ Эта команда только для администраторов!")
            return
        
        target = None
        target_id = None
        amount = 0
        
        message_text = message.text
        parts = message_text.split()
        
        for i, part in enumerate(parts):
            if part.isdigit():
                amount = int(part)
                break
        
        if amount <= 0:
            await message.answer("❌ Укажите количество конфеток для конфискации!")
            return
        
        if message.reply_to_message:
            target = message.reply_to_message.from_user
            target_id = str(target.id)
        elif message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    mentioned_username = message.text[entity.offset:entity.offset + entity.length].lstrip('@')
                    try:
                        target_id = mentioned_username
                        target = type('User', (), {'id': target_id, 'first_name': mentioned_username})()
                    except:
                        await message.answer("❌ Не могу найти пользователя.")
                        return
                    break
        
        if not target:
            await message.answer("❌ Укажите пользователя через @username или ответьте на его сообщение!")
            return
        
        initialize_user_reputation(int(target_id), int(target_id) in ADMINS, int(target_id) == OWNER_ID)
        
        target_candies = bot_data.data["REPUTATION_DATA"][target_id]["candies"]
        
        if target_candies < amount:
            await message.answer(f"❌ У пользователя всего {target_candies} конфеток!")
            return
        
        bot_data.data["REPUTATION_DATA"][target_id]["candies"] -= amount
        bot_data.save_data()
        
        new_amount = target_candies - amount
        target_name = f'<a href="tg://user?id={target_id}">{target.first_name}</a>'
        confiscator_name = f'<a href="tg://user?id={confiscator_id}">{confiscator.first_name}</a>'
        
        await message.answer(f"🏦 Отнял {amount} конфеток у {target_name}. Теперь его число: {new_amount}.\nОтнял: {confiscator_name} 🧑‍⚖️", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка в confiscate_candies: {e}")
        await message.answer("❌ Ошибка при конфискации конфеток")

# ========== НАЗНАЧЕНИЕ СТАТУСОВ ==========
async def set_status(message: Message):
    try:
        if message.from_user.id not in ADMINS:
            await message.answer("❌ Только администраторы могут менять статусы!")
            return
        
        if message.reply_to_message:
            target = message.reply_to_message.from_user
            status_arg = message.text.lower().replace('назначить', '').replace('статус', '').strip()
        else:
            await message.answer("❌ Ответьте на сообщение пользователя!")
            return
        
        target_id = str(target.id)
        
        status_mapping = {
            'админ': 'админ 👻', 'админом': 'админ 👻',
            'модер': 'модер', 'модером': 'модер',
            'любимчик': 'любимчик 🍬', 'любимчиком': 'любимчик 🍬',
            'киссмейт': 'киссмейт 🦇', 'киссмейтом': 'киссмейт 🦇',
            'сладкоежка': 'сладкоежка 🍬', 'сладкоежкой': 'сладкоежка 🍬',
            'говноед': 'Говноедик 💩', 'говном': 'Говноедик 💩',
            'снюсоед': 'снюсоед 💎', 'снюсоедом': 'снюсоед 💎',
            'старик': 'Старик 👴🏻', 'стариком': 'Старик 👴🏻'
        }
        
        new_status = None
        for key, value in status_mapping.items():
            if key in status_arg:
                new_status = value
                break
        
        if not new_status:
            await message.answer("❌ Укажите статус: админ, модер, любимчик, киссмейт, сладкоежка, говноед, снюсоед, старик")
            return

        initialize_user_reputation(target.id, target.id in ADMINS, target.id == OWNER_ID)

        current_status = bot_data.data["REPUTATION_DATA"][target_id]["status"]
        if current_status == new_status:
            target_name = f'<a href="tg://user?id={target.id}">{target.first_name}</a>'
            await message.answer(f"😸 {target_name} уже с этим статусом")
            return

        bot_data.data["REPUTATION_DATA"][target_id]["status"] = new_status
        bot_data.save_data()
        
        target_name = f'<a href="tg://user?id={target.id}">{target.first_name}</a>'

        status_messages = {
            'админ 👻': f"🙀 {target_name} назначен админом!",
            'модер': f"🐈 Теперь {target_name} модератор!",
            'любимчик 🍬': f"💕 {target_name} теперь любимчик!",
            'киссмейт 🦇': f"💩 теперь ты обычный лашара, {target_name}.",
            'сладкоежка 🍬': f"🍬 Теперь {target_name} повелитель конфет!",
            'Говноедик 💩': f"💩 С этого момента {target_name} говноед!",
            'снюсоед 💎': f"💎 Теперь {target_name} снюсоед!",
            'Старик 👴🏻': f"👴🏻 {target_name} быстро состарился!"
        }
        
        await message.answer(status_messages[new_status], parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка в set_status: {e}")
        await message.answer("❌ Ошибка при установке статуса")

async def handle_special_status_commands(message: Message):
    try:
        if message.from_user.id not in ADMINS:
            return
            
        message_text = message.text.lower()
        
        if "назначить сладкоежкой" in message_text:
            await set_special_status(message, "сладкоежка 🍬", "🍬 Теперь {target_name} повелитель конфет!")
        elif "назначить говном" in message_text:
            await set_special_status(message, "Говноедик 💩", "💩 С этого момента {target_name} говноед!")
        elif "назначить снюсоедом" in message_text:
            await set_special_status(message, "снюсоед 💎", "💎 Теперь {target_name} снюсоед!")
        elif "назначить стариком" in message_text:
            await set_special_status(message, "Старик 👴🏻", "👴🏻 {target_name} быстро состарился!")
    except Exception as e:
        logger.error(f"Ошибка в handle_special_status_commands: {e}")

async def set_special_status(message: Message, status: str, msg: str):
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        target_id = str(target.id)
        
        initialize_user_reputation(target.id, target.id in ADMINS, target.id == OWNER_ID)
        bot_data.data["REPUTATION_DATA"][target_id]["status"] = status
        bot_data.save_data()
        
        target_name = f'<a href="tg://user?id={target.id}">{target.first_name}</a>'
        await message.answer(msg.format(target_name=target_name), parse_mode="HTML")
    else:
        await message.answer("❌ Ответьте на сообщение пользователя!")

# ========== НАЧИСЛЕНИЕ МОНЕТ АДМИНАМИ ==========
async def add_coins_command(message: Message, bot: Bot):
    try:
        user = message.from_user
        
        if user.id not in ADMINS:
            await message.answer("❌ Эта команда доступна только администраторам!")
            return
        
        message_text = message.text.strip()
        
        if not message_text.startswith('+'):
            await message.answer("❌ Формат: +число @username\nПример: +80 @username")
            return
        
        parts = message_text[1:].split()
        if len(parts) < 2:
            await message.answer("❌ Формат: +число @username\nПример: +80 @username")
            return
        
        try:
            coins_amount = int(parts[0])
        except ValueError:
            await message.answer("❌ Укажите число монет после плюса!")
            return
        
        if coins_amount <= 0 or coins_amount > 1000000:
            await message.answer("❌ Число монет должно быть от 1 до 1,000,000!")
            return
        
        target_username = parts[1]
        if not target_username.startswith('@'):
            mentioned_username = None
            if message.entities:
                for entity in message.entities:
                    if entity.type == "mention":
                        mentioned_username = message.text[entity.offset:entity.offset + entity.length]
                        break
            if mentioned_username and mentioned_username.startswith('@'):
                target_username = mentioned_username
            else:
                await message.answer("❌ Укажите @username пользователя!")
                return
        
        clean_username = target_username[1:].lower()
        target_user_id = None
        target_first_name = None
        
        for user_id_str, user_data in bot_data.data["REPUTATION_DATA"].items():
            try:
                user_obj = await bot.get_chat(int(user_id_str))
                if user_obj.username and user_obj.username.lower() == clean_username:
                    target_user_id = int(user_id_str)
                    target_first_name = user_obj.first_name
                    break
            except:
                continue
        
        if not target_user_id:
            try:
                user_chat = await bot.get_chat(target_username)
                target_user_id = user_chat.id
                target_first_name = user_chat.first_name
            except:
                await message.answer(f"❌ Не могу найти пользователя {target_username}")
                return
        
        initialize_user_reputation(target_user_id, target_user_id in ADMINS, target_user_id == OWNER_ID)
        
        target_user_id_str = str(target_user_id)
        current_coins = bot_data.data["REPUTATION_DATA"].get(target_user_id_str, {}).get("coins", 0)
        
        bot_data.data["REPUTATION_DATA"][target_user_id_str]["coins"] = current_coins + coins_amount
        bot_data.save_data()
        
        admin_response = f"✅ Начислил {coins_amount} монет пользователю {target_username}\n💰 Новый баланс: {current_coins + coins_amount}"
        await message.answer(admin_response)
        
        try:
            await bot.send_message(
                chat_id=target_user_id,
                text=f"🎁 *Вам начислены монеты!*\n\n✔ Было зачислено: *{coins_amount} монет*\n💰 Новый баланс: *{current_coins + coins_amount}*",
                parse_mode="Markdown"
            )
        except:
            await message.answer("✅ Монеты начислены, но не удалось отправить уведомление пользователю.")
    except Exception as e:
        logger.error(f"Ошибка в add_coins_command: {e}")
        await message.answer("❌ Ошибка при выполнении команды")

async def add_coins_reply_command(message: Message, bot: Bot):
    try:
        user = message.from_user
        
        if user.id not in ADMINS:
            await message.answer("❌ Эта команда доступна только администраторам!")
            return
        
        if not message.reply_to_message:
            return
        
        message_text = message.text.strip()
        if not message_text.startswith('+'):
            return
        
        try:
            coins_amount = int(message_text[1:])
        except ValueError:
            await message.answer("❌ Укажите число монет после плюса!")
            return
        
        if coins_amount <= 0 or coins_amount > 1000000:
            await message.answer("❌ Число монет должно быть от 1 до 1,000,000!")
            return
        
        target_user = message.reply_to_message.from_user
        target_user_id = target_user.id
        target_username = f"@{target_user.username}" if target_user.username else target_user.first_name
        
        initialize_user_reputation(target_user_id, target_user_id in ADMINS, target_user_id == OWNER_ID)
        
        target_user_id_str = str(target_user_id)
        current_coins = bot_data.data["REPUTATION_DATA"].get(target_user_id_str, {}).get("coins", 0)
        
        bot_data.data["REPUTATION_DATA"][target_user_id_str]["coins"] = current_coins + coins_amount
        bot_data.save_data()
        
        admin_response = f"✅ Начислил {coins_amount} монет пользователю {target_username}\n💰 Новый баланс: {current_coins + coins_amount}"
        await message.answer(admin_response)
        
        try:
            await bot.send_message(
                chat_id=target_user_id,
                text=f"🎁 *Вам начислены монеты!*\n\n✔ Было зачислено: *{coins_amount} монет*\n💰 Новый баланс: *{current_coins + coins_amount}*",
                parse_mode="Markdown"
            )
        except:
            await message.answer("✅ Монеты начислены, но не удалось отправить уведомление.")
    except Exception as e:
        logger.error(f"Ошибка в add_coins_reply_command: {e}")

async def remove_coins_command(message: Message, bot: Bot):
    try:
        user = message.from_user
        
        if user.id not in ADMINS:
            await message.answer("❌ Эта команда доступна только администраторам!")
            return
        
        message_text = message.text.strip()
        if not message_text.startswith('-'):
            await message.answer("❌ Формат: -число @username")
            return
        
        parts = message_text[1:].split()
        if len(parts) < 2:
            await message.answer("❌ Формат: -число @username")
            return
        
        try:
            coins_amount = int(parts[0])
        except ValueError:
            await message.answer("❌ Укажите число монет после минуса!")
            return
        
        if coins_amount <= 0:
            await message.answer("❌ Число монет должно быть положительным!")
            return
        
        target_username = parts[1]
        if not target_username.startswith('@'):
            await message.answer("❌ Укажите @username пользователя!")
            return
        
        clean_username = target_username[1:].lower()
        target_user_id = None
        
        for user_id_str, user_data in bot_data.data["REPUTATION_DATA"].items():
            try:
                user_obj = await bot.get_chat(int(user_id_str))
                if user_obj.username and user_obj.username.lower() == clean_username:
                    target_user_id = int(user_id_str)
                    break
            except:
                continue
        
        if not target_user_id:
            await message.answer(f"❌ Не могу найти пользователя {target_username}")
            return
        
        target_user_id_str = str(target_user_id)
        current_coins = bot_data.data["REPUTATION_DATA"].get(target_user_id_str, {}).get("coins", 0)
        
        if current_coins < coins_amount:
            await message.answer(f"❌ У пользователя недостаточно монет! Баланс: {current_coins}")
            return
        
        bot_data.data["REPUTATION_DATA"][target_user_id_str]["coins"] = current_coins - coins_amount
        bot_data.save_data()
        
        await message.answer(f"✅ Снял {coins_amount} монет у {target_username}\n💰 Новый баланс: {current_coins - coins_amount}")
    except Exception as e:
        logger.error(f"Ошибка в remove_coins_command: {e}")
        await message.answer("❌ Ошибка при выполнении команды")

# ========== ОБРАБОТЧИК ЛИЧНЫХ СООБЩЕНИЙ ==========
async def handle_private_messages(message: Message, state: FSMContext, bot: Bot):
    """Обрабатывает все сообщения в ЛС"""
    logger.info(f"🔥🔥🔥 handle_private_messages ПОЛУЧИЛО: {message.text} от {message.from_user.id}")
    user_id = message.from_user.id
    logger.info(f"=== handle_private_messages для {user_id} ===")
    
    current_state = await state.get_state()
    
    # Проверяем, является ли админ в режиме ответа
    if current_state == AdminStates.replying_to_message:
        logger.info("Обрабатываем как ОТВЕТ АДМИНА")
        await handle_admin_reply_message(message, state, bot)
        return
    
    # Проверяем, находится ли пользователь в режиме редактирования слива
    if current_state == UserStates.editing_sliv:
        logger.info("Обрабатываем как РЕДАКТИРОВАНИЕ СЛИВА")
        await handle_edited_sliv(message, state, bot)
        return
    
    # Проверяем, ожидаем ли сообщение админам
    if current_state == UserStates.awaiting_message_to_admins:
        logger.info("Обрабатываем как СООБЩЕНИЕ АДМИНАМ")
        await handle_message_to_admins(message, state, bot)
        return
    
    # Проверяем, ожидаем ли запрос на конфеты
    if current_state == UserStates.awaiting_candy_request:
        logger.info("Обрабатываем как ЗАПРОС КОНФЕТ")
        await process_candy_request(message, state, bot)
        return
    
    # Проверяем, ожидаем ли количество звезд
    if current_state == UserStates.awaiting_stars_amount:
        logger.info("Обрабатываем как КОЛИЧЕСТВО ЗВЕЗД")
        await handle_stars_amount_input(message, state, bot)
        return
    
    # Проверяем, ожидаем ли получателя звезд
    if current_state == UserStates.awaiting_stars_recipient:
        logger.info("Обрабатываем как ПОЛУЧАТЕЛЬ ЗВЕЗД")
        await handle_stars_recipient_text(message, state, bot)
        return
    
    # Проверяем, ожидаем ли количество монет
    if current_state == UserStates.awaiting_coins_amount:
        logger.info("Обрабатываем как КОЛИЧЕСТВО МОНЕТ")
        await handle_coins_amount_input(message, state, bot)
        return
    
    # Обработка рейда
    if current_state == UserStates.awaiting_raid_request:
        logger.info("Обрабатываем как РЕЙД")
        await handle_raid_request(message, state, bot)
        return
    
    # Обработка слива
    if current_state == UserStates.awaiting_sliv:
        logger.info("Обрабатываем как СЛИВ")
        await forward_to_admins(message, state, bot)
        return
    
    # Нейросеть для обычных сообщений
    if user_id in user_sessions and user_sessions[user_id].get('active'):
        ai_response = get_ai_response(message.text, user_id)
        await message.answer(ai_response)
    
    logger.info("Не ожидаем никаких действий - пропускаем")

# ========== ОТМЕНА ДЕЙСТВИЯ ==========
async def cancel_action(message: Message, state: FSMContext):
    try:
        if message.chat.type != "private":
            return
            
        user_id = message.from_user.id
        logger.info(f"Пользователь {user_id} пытается отменить действие")

        current_state = await state.get_state()
        
        if current_state == UserStates.awaiting_raid_request:
            await state.set_state(None)
            await message.answer("🐈‍⬛ Окей, отменил отправку админам =)")
            return
            
        if current_state == UserStates.awaiting_sliv:
            await state.set_state(None)
            await message.answer("🧙🏻‍♀️ Окееей, отменил отправку админам", reply_markup=get_keyboard("private"))
            return
        
        if current_state == UserStates.awaiting_message_to_admins:
            await state.set_state(None)
            await message.answer("❌ Отправка сообщения админам отменена.")
            return
        
        if current_state == UserStates.awaiting_candy_request:
            await state.set_state(None)
            await message.answer("❌ Запрос на получение конфет отменен.")
            return
        
        if current_state == UserStates.awaiting_coins_amount:
            await state.set_state(None)
            await message.answer("❌ Покупка монет отменена.")
            return
        
        if current_state == UserStates.awaiting_stars_amount:
            await state.set_state(None)
            await message.answer("❌ Покупка звезд отменена.")
            return
        
        await message.answer("🤔 Нечего отменять")
    except Exception as e:
        logger.error(f"Ошибка в cancel_action: {e}")
        await message.answer("❌ Ошибка при отмене действия")

# ========== ОТСЛЕЖИВАНИЕ АКТИВНОСТИ ==========
async def track_user_activity(message: Message):
    try:
        user_id = str(message.from_user.id)
        
        if user_id not in bot_data.data["USER_DATA"]["activity"]:
            bot_data.data["USER_DATA"]["activity"][user_id] = 0
        
        bot_data.data["USER_DATA"]["activity"][user_id] += 1
        
        if bot_data.data["USER_DATA"]["activity"][user_id] % 10 == 0:
            bot_data.save_data()
    except Exception as e:
        logger.error(f"Ошибка в track_user_activity: {e}")

# ========== НОВЫЕ УЧАСТНИКИ ==========
async def track_new_members(message: Message, bot: Bot):
    if not message.new_chat_members:
        return
    
    chat_id = message.chat.id
    
    for new_member in message.new_chat_members:
        if new_member.id == bot.id:
            continue
            
        user_id_str = str(new_member.id)
        
        if "CHAT_MEMBERS" not in bot_data.data:
            bot_data.data["CHAT_MEMBERS"] = {}
        
        chat_id_str = str(chat_id)
        if chat_id_str not in bot_data.data["CHAT_MEMBERS"]:
            bot_data.data["CHAT_MEMBERS"][chat_id_str] = []
        
        if user_id_str not in bot_data.data["CHAT_MEMBERS"][chat_id_str]:
            bot_data.data["CHAT_MEMBERS"][chat_id_str].append(user_id_str)
            bot_data.save_data()
        
        logger.info(f"Новый участник {user_id_str} добавлен в чат {chat_id_str}")

# ========== КОМАНДА .ДСК ==========
async def dsk_command(message: Message, bot: Bot):
    user = message.from_user
    chat = message.chat
    
    try:
        member = await chat.get_member(user.id)
        if member.status not in ['administrator', 'creator']:
            await message.answer("❌ Эта команда доступна только администраторам чата.")
            return
    except Exception as e:
        logger.error(f"Ошибка проверки прав: {e}")
        await message.answer("❌ Не удалось проверить ваши права.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📨 В ЛС", callback_data="dsk_private")],
        [InlineKeyboardButton(text="💬 Сюда", callback_data="dsk_chat")]
    ])
    await message.answer("🎃 Отправить ссылку сюда или в лс?", reply_markup=keyboard)

async def handle_dsk_choice(callback: CallbackQuery, bot: Bot):
    user = callback.from_user
    chat = callback.message.chat
    
    try:
        member = await chat.get_member(user.id)
        if member.status not in ['administrator', 'creator']:
            await callback.answer("❌ У вас нет прав для использования этой команды.", show_alert=True)
            return
    except Exception as e:
        await callback.answer("❌ Ошибка проверки прав.", show_alert=True)
        return
    
    await callback.answer("⏳ Получаю ссылку...")
    
    try:
        bot_member = await chat.get_member(bot.id)
        if bot_member.status not in ['administrator', 'creator']:
            await callback.message.edit_text("❌ Бот не является администратором чата.")
            return
            
        if not bot_member.can_invite_users:
            await callback.message.edit_text("❌ У бота нет прав для создания ссылок-приглашений.")
            return

        invite_link = await bot.export_chat_invite_link(chat.id)
        
        if callback.data == "dsk_private":
            try:
                await bot.send_message(chat_id=user.id, text=f"✨ Ссылка на чат:\n{invite_link}")
                await callback.message.edit_text("✅ Ссылка отправлена вам в личные сообщения!")
            except Exception as e:
                await callback.message.edit_text("❌ Не могу отправить вам сообщение. Возможно, вы не начинали диалог с ботом.")
        elif callback.data == "dsk_chat":
            await callback.message.edit_text(f"✨ Ссылка чата:\n{invite_link}")
    except Exception as e:
        logger.error(f"Ошибка получения ссылки: {e}")
        await callback.message.edit_text("❌ Не удалось получить ссылку на чат.")

# ========== РАССЫЛКА ==========
async def broadcast_command(message: Message, bot: Bot):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Эта команда только для владельца!")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Используйте: /bc ваш текст рассылки")
        return
    
    broadcast_text = args[1]
    success_count = 0
    fail_count = 0

    # ✅ ИСПРАВЛЕНО - используем правильную переменную для чатов
    chats_to_send = []
    for user_id_str in bot_data.data["USER_DATA"]["join_dates"]:
        try:
            user_id = int(user_id_str)
            # Пытаемся отправить в ЛС пользователя
            chats_to_send.append(user_id)
        except:
            pass
    
    for chat_id in chats_to_send:
        try:
            await bot.send_message(chat_id=chat_id, text=broadcast_text)
            success_count += 1
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Ошибка отправки для {chat_id}: {e}")
            fail_count += 1

    await message.answer(
        f"✅ Рассылка завершена!\n"
        f"Успешно: {success_count}\n"
        f"Не удалось: {fail_count}\n"
        f"Всего попыток: {len(chats_to_send)}"
    )

# ========== ПРИВЯЗКА КАНАЛА ==========
async def link_channel(message: Message, bot: Bot):
    if message.chat.type != "private":
        await message.answer("❌ Эта команда работает только в личных сообщениях с ботом.")
        return

    if message.from_user.id not in ADMINS:
        await message.answer("❌ Недостаточно прав. Ты не админ.")
        return

    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("❌ Неправильный формат. Используй: `!привязать @username_канала`", parse_mode="Markdown")
        return

    channel_username = parts[1]
    if not channel_username.startswith('@'):
        await message.answer("❌ Юзернейм канала должен начинаться с `@`.", parse_mode="Markdown")
        return

    try:
        chat = await bot.get_chat(channel_username)
        if chat.type not in ['channel', 'supergroup']:
            await message.answer("❌ Это не канал. Укажи юз канала.")
            return

        bot_member = await chat.get_member(bot.id)
        if bot_member.status not in ['administrator', 'creator']:
            await message.answer(f"❌ Бот не является администратором канала {channel_username}.")
            return

        bot_data.data["CHANNEL_FOR_POSTS"] = chat.id
        bot_data.save_data()
        await message.answer(f"✅ Привязал канал {channel_username}!")
    except Exception as e:
        logger.error(f"Ошибка при привязке канала: {e}")
        await message.answer(f"❌ Не удалось привязать канал. Ошибка: {e}")

# ========== ДЕБАГ ФОТО ==========
async def debug_photo(message: Message):
    if message.from_user.id not in ADMINS:
        return
        
    user_id = str(message.from_user.id)
    
    if user_id in bot_data.data["CUSTOM_PHOTOS_FILE_ID"]:
        photo_info = bot_data.data["CUSTOM_PHOTOS_FILE_ID"][user_id]
        await message.answer(
            f"🔧 ДЕБАГ ИНФО:\n"
            f"User: {user_id}\n"
            f"Photo: {photo_info}\n"
            f"Type: {type(photo_info)}"
        )
    else:
        await message.answer("❌ Нет кастомного фото")

# ========== НАЧИСЛЕНИЕ КОНФЕТ ВЛАДЕЛЬЦУ ==========
async def add_candies_command(message: Message):
    try:
        user = message.from_user
        
        if user.id != OWNER_ID:
            await message.answer("🖕🏻, не сегодня")
            return
        
        user_id_str = str(user.id)
        initialize_user_reputation(user.id, True, True)
        
        bot_data.data["REPUTATION_DATA"][user_id_str]["candies"] += 800000000000000000000000000000
        bot_data.save_data()
        
        new_candies = bot_data.data["REPUTATION_DATA"][user_id_str]["candies"]
        await message.answer(f"🍭 Начислил 800000000000000000000 конфет\nТеперь у тебя: {new_candies:,} конфет")
    except Exception as e:
        logger.error(f"Ошибка в add_candies_command: {e}")
        await message.answer("❌ Ошибка при начислении конфет")

# ========== АНЯ ФОТОГРАФИИ ==========
async def handle_anya_command(message: Message):
    message_text = message.text.lower().strip()
    
    commands = ["аня, скинь свои фотки", "аня скинь свои фотки", "аня фото", "аня, фото", "аня фотки", "аня, фотки"]
    
    if message_text not in commands:
        return
    
    user = message.from_user
    username = user.username or user.first_name
    
    await message.answer(f"✨ {username}, держи фотки Ани... 😏")
    
    photo_patterns = [
        "anya*.jpg", "anya*.jpeg", "anya*.png",
        "photo*.jpg", "photo*.jpeg", "photo*.png",
        "1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "6.jpg", "7.jpg", "8.jpg",
        "1.jpeg", "2.jpeg", "3.jpeg", "4.jpeg", "5.jpeg", "6.jpeg", "7.jpeg", "8.jpeg",
    ]
    
    found_photos = []
    
    for pattern in photo_patterns:
        if "*" in pattern:
            photos = glob.glob(pattern)
            photos.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.findall(r'\d+|\D+', x)])
            found_photos.extend(photos[:8])
        else:
            if os.path.exists(pattern):
                found_photos.append(pattern)
    
    if not found_photos:
        await message.answer("❌ Фотографии Ани не найдены...")
        return
    
    sent_count = 0
    for i, photo_path in enumerate(found_photos[:8], 1):
        try:
            photo_file = FSInputFile(photo_path)
            await message.answer_photo(photo=photo_file, caption=f"Фото {i}/{min(len(found_photos), 8)}")
            sent_count += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Ошибка отправки фото {photo_path}: {e}")
    
    if sent_count > 0:
        await message.answer("в0zbуд#лся¿ 😚")
    else:
        await message.answer("❌ Не удалось отправить ни одной фотографии...")

# ========== КОМАНДА НАЧИСЛИТЬ ==========
async def na4islit_command(message: Message):
    try:
        user = message.from_user
        if user.id != OWNER_ID:
            await message.answer("🖕🏻, не сегодня")
            return
        
        user_id_str = str(user.id)
        initialize_user_reputation(user.id, True, True)
        
        bot_data.data["REPUTATION_DATA"][user_id_str]["candies"] += 80000
        bot_data.save_data()
        
        await message.answer("🍭 Начислил 80000 конфет владельцу")
    except Exception as e:
        logger.error(f"Ошибка в na4islit_command: {e}")

# ========== ЛИМИТИРОВАННЫЕ КОНФЕТЫ ==========
async def check_limited_status(message: Message):
    try:
        total_given = bot_data.data.get("LIMITED_CANDIES_TOTAL_GIVEN", 0)
        remaining = LIMITED_CANDIES_TOTAL - total_given
        
        text = (
            f"⚡ <b>СИСТЕМА ЛИМИТИРОВАННЫХ КОНФЕТ</b>\n\n"
            f"📊 <b>Общая статистика:</b>\n"
            f"• Всего в системе: {LIMITED_CANDIES_TOTAL} конфет\n"
            f"• Уже выдано: {total_given} конфет\n"
            f"• Осталось: {remaining} конфет\n\n"
            f"🎰 <b>Обмен лимитированных конфет:</b>\n"
            f"• Команда: <code>микс</code>\n"
            f"• 1 лимитированная = 15-60 обычных\n"
            f"• Шанс при передаче: {LIMITED_CANDY_CHANCE*100}%\n\n"
            f"<i>Лимитированные конфеты могут получить только обычные пользователи при передаче конфет от сладкоежек</i>"
        )
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка в check_limited_status: {e}")
        await message.answer("❌ Ошибка при получении информации")

async def my_limited_candies(message: Message):
    try:
        user = message.from_user
        user_id_str = str(user.id)
        
        limited_candies = bot_data.data["LIMITED_CANDIES"].get(user_id_str, 0)
        
        if limited_candies <= 0:
            text = (
                f"🍭 <b>Твои лимитированные конфеты</b>\n\n"
                f"У тебя пока нет лимитированных конфеток!\n\n"
                f"Чтобы получить лимитированную конфету:\n"
                f"1. Попроси сладкоежку передать тебе обычные конфетки\n"
                f"2. При передаче есть шанс {LIMITED_CANDY_CHANCE*100}% получить лимитированную!\n"
                f"3. Всего можно выдать {LIMITED_CANDIES_TOTAL} лимитированных конфет"
            )
        else:
            text = (
                f"🍭 <b>Твои лимитированные конфеты</b>\n\n"
                f"⚡ У тебя есть: <b>{limited_candies}</b> лимитированных конфеток!\n\n"
                f"✨ <b>Что можно сделать:</b>\n"
                f"• Обменять на обычные конфеты командой <code>микс</code>\n"
                f"• 1 лимитированная = 15-60 обычных конфет\n"
                f"• Сохранить как коллекционные\n\n"
                f"<i>Всего лимитированных конфет в системе: {LIMITED_CANDIES_TOTAL}</i>"
            )
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка в my_limited_candies: {e}")
        await message.answer("❌ Ошибка при проверке конфет")

async def handle_numeric_input(message: Message, state: FSMContext, bot: Bot):
    """Обработчик числового ввода для покупки монет"""
    current_state = await state.get_state()
    
    if current_state == UserStates.awaiting_coins_amount:
        try:
            coins_amount = int(message.text.strip())
            
            if coins_amount <= 0 or coins_amount > 1000000:
                await message.answer("❌ Введите число от 1 до 1,000,000!")
                return
            
            rubles = coins_amount
            stars = coins_amount // 2
            
            await state.update_data(purchase_data={
                "coins": coins_amount,
                "rubles": rubles,
                "stars": stars,
                "user_id": message.from_user.id
            })
            
            text = f"🎄 Прекрасно!\nПокупка на: {coins_amount} монет\nК оплате: {rubles}р\nВ звездах: {stars}\n\nВыберите способ оплаты:"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="банковской картой 💳", url="https://pay.cloudtips.ru/p/921f9727")]
            ])
            await message.answer(text, reply_markup=keyboard)
            await state.set_state(None)
        except ValueError:
            await message.answer("❌ Пожалуйста, введите только число!")

# ========== ВОССТАНОВЛЕНИЕ ПОЛЬЗОВАТЕЛЕЙ ==========
async def restore_existing_users(bot: Bot):
    """Восстанавливает chat_id всех существующих пользователей"""
    try:
        for user_id_str in list(bot_data.data["USER_DATA"]["join_dates"].keys()):
            try:
                user_id = int(user_id_str)
                await bot.send_chat_action(chat_id=user_id, action="typing")
                user_chat_ids.add(user_id)
            except Exception as e:
                logger.warning(f"Пользователь {user_id_str} недоступен: {e}")
                continue
        logger.info(f"Восстановлено {len(user_chat_ids)} пользователей для рассылки")
    except Exception as e:
        logger.error(f"Ошибка восстановления пользователей: {e}")

# ========== ОБРАБОТЧИК ДЛЯ КНОПКИ НАЗАД ==========
async def handle_coins_amount_input(message: Message, state: FSMContext, bot: Bot):
    """Обработка ввода количества монет"""
    try:
        coins_amount = int(message.text.strip())
        
        if coins_amount <= 0 or coins_amount > 1000000:
            await message.answer("❌ Введите число от 1 до 1,000,000!")
            return
        
        rubles = coins_amount
        stars = coins_amount // 2
        
        await state.update_data(purchase_data={
            "coins": coins_amount,
            "rubles": rubles,
            "stars": stars,
            "user_id": message.from_user.id
        })
        
        text = f"🎄 Прекрасно!\nПокупка на: {coins_amount} монет\nК оплате: {rubles}р\nВ звездах: {stars}\n\nВыберите способ оплаты:"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="банковской картой 💳", url="https://pay.cloudtips.ru/p/921f9727")]
        ])
        await message.answer(text, reply_markup=keyboard)
        await state.set_state(None)
    except ValueError:
        await message.answer("❌ Пожалуйста, введите только число!")

async def handle_stars_recipient_text(message: Message, state: FSMContext, bot: Bot):
    """Обработка текстового ввода получателя звезд"""
    recipient_input = message.text.strip()
    
    if not recipient_input.startswith('@'):
        recipient_input = '@' + recipient_input
    
    if len(recipient_input) < 2:
        await message.answer("❌ Неверный формат username. Пример: @username")
        return
    
    data = await state.get_data()
    stars_data = data.get("stars_data", {})
    stars_data["recipient_username"] = recipient_input
    stars_data["is_for_self"] = False
    await state.update_data(stars_data=stars_data)
    
    text = (
        f"🖋 *ВНИМАТЕЛЬНО!*\n\n"
        f"ты покупаешь *{stars_data['stars_amount']}* звезд.\n"
        f"получатель: *{recipient_input}*\n"
        f"к оплате: *{stars_data['coins_needed']}* 🪙\n\n"
        f"все верно?"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, все верно ✅", callback_data="stars_confirm")],
        [InlineKeyboardButton(text="Назад 🔙", callback_data="stars_cancel")]
    ])
    
    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
    await state.set_state(None)

# ========== ДОБАВЬТЕ ЭТИ СТРОКИ ПЕРЕД ФУНКЦИЕЙ MAIN ==========

# Принудительная проверка текста кнопки
async def debug_text(message: Message):
    """Диагностика - показывает какой текст получил бот"""
    user_id = message.from_user.id
    text = message.text
    logger.info(f"Диагностика: пользователь {user_id} отправил текст: '{text}'")
    await message.answer(f"🔍 Бот получил текст: `{text}`\nДлина: {len(text)} символов", parse_mode="Markdown")

# Альтернативный запуск слива БЕЗ КОМАНДЫ
async def alt_sliv(message: Message, state: FSMContext):
    """Запуск слива по тексту"""
    text = message.text
    # Если кнопка не срабатывает из-за спецсимволов, проверяем оба варианта
    if text == "Слить 🔥" or text == "Слить" or "слить" in text.lower():
        await sliv(message, state)
        return True
    return False

# Перехватчик ВСЕХ сообщений в ЛС (для диагностики)
async def catch_all_messages(message: Message, state: FSMContext, bot: Bot):
    """Ловит все сообщения, которые не обработаны другими обработчиками"""
    user_id = message.from_user.id
    text = message.text
    
    logger.info(f"=== ПЕРЕХВАТЧИК: сообщение от {user_id}: '{text}' ===")
    
    # Проверяем текущее состояние
    current_state = await state.get_state()
    
    # Если ожидаем слив - обрабатываем
    if current_state == UserStates.awaiting_sliv:
        logger.info("ПЕРЕХВАТЧИК: обрабатываем как СЛИВ")
        await forward_to_admins(message, state, bot)
        return
    
    # Если просто текст - показываем диагностику
    await message.answer(f"📝 Получено: '{text}'\nСостояние: {current_state}\n\nНажмите кнопку 'Слить 🔥' для начала")

# ========== ПРЯМОЙ ОБРАБОТЧИК КНОПКИ "СЛИТЬ" ==========
async def handle_sliv_button(message: Message, state: FSMContext):
    """Прямой обработчик кнопки Слить 🔥"""
    logger.info(f"=== handle_sliv_button вызвана! Текст: {message.text} ===")
    
    # Проверяем разные варианты текста кнопки
    text = message.text
    if text == "Слить 🔥" or text == "Слить" or "слить" in text.lower():
        await sliv(message, state)
        return True
    return False

# ========== ФУНКЦИЯ MAIN - РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ ==========
async def main():
    global ban_data
    ban_data = load_ban_data()
    
    # Восстанавливаем пользователей для рассылки
    for user_id in bot_data.data["USER_DATA"]["join_dates"]:
        try:
            user_chat_ids.add(int(user_id))
        except:
            pass
    
    logger.info(f"Загружено {len(user_chat_ids)} пользователей из базы")
    
    # Создаем бота и диспетчер
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # ========== MIDDLEWARE ==========
    dp.message.middleware(subscription_middleware)
    dp.message.middleware(ban_middleware)
    
    # ========== КОМАНДЫ (СЛЕШ) ==========
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_ban_user, Command(commands=["ban", "бан"]))
    dp.message.register(cmd_unban_user, Command(commands=["unban", "разбан"]))
    dp.message.register(cmd_banned_list, Command(commands=["banned", "забаненные"]))
    dp.message.register(add_union, Command(commands=["addunion"]))
    dp.message.register(list_unions, Command(commands=["unions"]))
    dp.message.register(broadcast_command, Command(commands=["bc"]))
    dp.message.register(link_channel, Command(commands=["привязать"]))
    dp.message.register(dsk_command, Command(commands=["дск"]))
    dp.message.register(add_candies_command, Command(commands=["начислить"]))
    dp.message.register(debug_photo, Command(commands=["debugphoto"]))
    dp.message.register(guess_number_start, Command(commands=["guess"]))
    
    # ========== КОМАНДЫ МОДЕРАЦИИ В ГРУППАХ ==========
    dp.message.register(ban_command, F.text.lower().startswith("бан") & F.chat.type.in_({"group", "supergroup"}))
    dp.message.register(unban_command, F.text.lower().startswith("разбан") & F.chat.type.in_({"group", "supergroup"}))
    dp.message.register(mute_command, F.text.lower().startswith("мут") & F.chat.type.in_({"group", "supergroup"}))
    dp.message.register(unmute_command, F.text.lower().startswith("размут") & F.chat.type.in_({"group", "supergroup"}))
    
    # ========== УВЕДОМЛЕНИЯ О ВЫХОДАХ ==========
    dp.message.register(toggle_leave_notifications, (F.text.lower().startswith("+ув") | F.text.lower().startswith("-ув")) & F.chat.type.in_({"group", "supergroup"}))
    dp.message.register(set_custom_leave_message, F.text.lower().startswith("+фув") & F.chat.type.in_({"group", "supergroup"}))
    
    # ========== RP КОМАНДЫ ==========
    dp.message.register(rp_command, F.text.lower().startswith(("убить", "найти", "заспамить", "торт", "забыть", "купить", "влюбить")))
    
    # ========== ИГРЫ ==========
    dp.message.register(kmk_game, F.text.lower().startswith("кисс") & (F.text.lower().contains("поцеловать") | F.text.lower().contains("убить") | F.text.lower().contains("брак")))
    
    # ========== КНОПКИ ГЛАВНОГО МЕНЮ ==========
    dp.message.register(sliv, F.text == "Слить 🔥")
    dp.message.register(info, F.text == "Информация ❓")
    dp.message.register(random_fact, F.text == "Факт 😧")
    dp.message.register(show_materials, F.text == "👀 Материал 👀")
    dp.message.register(order_raid, F.text == "Заказать рейд 💣")
    dp.message.register(kiss_shop, F.text == "КиссШоп 🎄")
    dp.message.register(start_write_to_admins, F.text == "Написать нам 🖋")
    dp.message.register(candies_info, F.text == "Конфетки 🍬")
    
    # ========== КОМАНДЫ "КИСС, ..." ==========
    dp.message.register(handle_kiss_command, F.text.lower().startswith("кисс,"))
    dp.message.register(handle_whoami_command, F.text.lower().startswith("киссбот, кто я"))
    dp.message.register(handle_poll_command, F.text.lower().startswith("кисс, опрос"))
    dp.message.register(handle_compliment_command, F.text.lower().startswith("кисс, похвали"))
    dp.message.register(handle_insult_command, F.text.lower().startswith("кисс, обругай"))
    dp.message.register(handle_gossip_command, F.text.lower().startswith("кисс, сплетня"))
    dp.message.register(handle_calc_command, F.text.lower().startswith("кисс, посчитай"))
    dp.message.register(start_chat, F.text.lower().startswith(("кисс, поговорим", "поговорим", "бот, поговори")))
    dp.message.register(stop_chat, F.text.lower().startswith(("кисс, спать", "стоп", "спать", "хватит", "закончим")))
    
    # ========== ДРУГИЕ КОМАНДЫ ==========
    dp.message.register(kxd_response, F.text.lower().startswith(("kxd", "кхд")))
    dp.message.register(tezy_response, F.text.lower().startswith(("тези", "tezy", "тэзи")))
    dp.message.register(handle_anya_command, F.text.lower().startswith(("аня, скинь свои фотки", "аня фото", "аня фотки")))
    dp.message.register(handle_kaban_hello, F.text.lower().startswith(("кисс, как дела", "кисс как дела")))
    dp.message.register(random_hello_response, F.text.lower().startswith(("привет", "здарова")))
    dp.message.register(call_users, F.text.lower().startswith("позвать"))
    
    # ========== КОМАНДЫ АДМИНОВ (ЧИСЛОВЫЕ) ==========
    dp.message.register(add_coins_command, F.text.regexp(r'^\+\d+\s+@\w+') & (F.chat.type == "private"))
    dp.message.register(add_coins_reply_command, F.text.regexp(r'^\+\d+$') & (F.chat.type == "private") & F.reply_to_message)
    dp.message.register(remove_coins_command, F.text.regexp(r'^-\d+\s+@\w+') & (F.chat.type == "private"))
    dp.message.register(handle_numeric_input, F.text.regexp(r'^\+\d+$') & (F.chat.type == "private"))
    
    # ========== КОМАНДЫ КОНФЕТ ==========
    dp.message.register(give_candy, F.text.lower().startswith("конфетка"))
    dp.message.register(mix_limited_candy, F.text.lower().startswith("микс"))
    dp.message.register(check_limited_status, F.text.lower().startswith("лимит"))
    dp.message.register(my_limited_candies, F.text.lower().startswith(("мои лимитки", "мои лимит конфеты")))
    
    # ========== КОМАНДЫ РЕПУТАЦИИ ==========
    dp.message.register(show_reputation, F.text.lower().startswith("репутация"))
    dp.message.register(change_reputation, F.text.lower().startswith(("+реп", "-реп")))
    dp.message.register(show_reputation_top, F.text.lower().startswith(("топреп", "топ реп")))
    dp.message.register(set_status, F.text.lower().startswith("назначить"))
    dp.message.register(handle_special_status_commands, F.text.lower().startswith("назначить"))
    
    # ========== ДРУГИЕ КОМАНДЫ ==========
    dp.message.register(confiscate_candies, F.text.lower().startswith("забрать"))
    dp.message.register(lip_exchange, F.text.lower().startswith("лип"))
    dp.message.register(add_reminder, F.text.lower().startswith("+нп"))
    dp.message.register(set_custom_photo, F.text.lower().startswith("+фото") & (F.chat.type == "private") & F.photo)
    dp.message.register(remove_custom_photo, F.text.lower().startswith("-фото"))
    dp.message.register(set_custom_phrase, F.text.lower().startswith("+фр"))
    dp.message.register(reset_custom_phrase, F.text.lower().startswith("-фр"))
    dp.message.register(cancel_action, F.text.lower().startswith("отмена") & (F.chat.type == "private"))
    
    # ========== ОБРАБОТЧИКИ ЧИСЛОВОГО ВВОДА ==========
    dp.message.register(handle_coins_amount_input, StateFilter(UserStates.awaiting_coins_amount))
    dp.message.register(handle_stars_recipient_text, StateFilter(UserStates.awaiting_stars_recipient))
    
    # ========== ОБРАБОТЧИКИ FSM ==========
    dp.message.register(handle_message_to_admins, StateFilter(UserStates.awaiting_message_to_admins))
    dp.message.register(forward_to_admins, StateFilter(UserStates.awaiting_sliv))  # ТОЛЬКО ЭТОТ, БЕЗ process_sliv
    dp.message.register(handle_raid_request, StateFilter(UserStates.awaiting_raid_request))
    dp.message.register(process_candy_request, StateFilter(UserStates.awaiting_candy_request))
    dp.message.register(handle_edited_sliv, StateFilter(UserStates.editing_sliv))
    dp.message.register(handle_admin_reply_message, StateFilter(AdminStates.replying_to_message))
    
    # ========== ОБРАБОТЧИКИ ГРУПП ==========
    dp.message.register(guess_number_play, F.text.regexp(r'^\d+$') & F.chat.type.in_({"group", "supergroup"}))
    dp.message.register(track_new_members, F.new_chat_members)
    dp.message.register(handle_left_member, F.left_chat_member)
    
    # ========== ОБРАБОТЧИК ЛИЧНЫХ СООБЩЕНИЙ ==========
    dp.message.register(handle_private_messages, F.chat.type == "private")
    
    # ========== CALLBACK-ОБРАБОТЧИКИ ==========
    dp.callback_query.register(handle_subscription_check, F.data == "check_subscription")
    dp.callback_query.register(handle_candy_request, F.data == "request_candies")
    dp.callback_query.register(handle_candy_admin_response, F.data.startswith("candy_"))
    dp.callback_query.register(handle_mix_confirmation, F.data.startswith("mix_"))
    dp.callback_query.register(handle_lip_buttons, F.data.startswith(("confirm_", "cancel_")))
    dp.callback_query.register(handle_delete_sliv, F.data.startswith("delete_sliv_"))
    dp.callback_query.register(handle_edit_sliv, F.data.startswith("edit_sliv_"))
    dp.callback_query.register(handle_sliv_buttons, F.data.startswith("sliv_"))
    dp.callback_query.register(handle_raid_buttons, F.data.startswith("raid_"))
    dp.callback_query.register(union_button_handler, F.data.startswith("union_"))
    dp.callback_query.register(handle_admin_buttons, F.data.startswith("admin_"))
    dp.callback_query.register(handle_dsk_choice, F.data.startswith("dsk_"))
    dp.callback_query.register(back_to_shop, F.data == "back_to_shop")
    dp.callback_query.register(buy_coins_start, F.data == "buy_coins_start")
    dp.callback_query.register(handle_phone_numbers_start, F.data == "phone_numbers_start")
    dp.callback_query.register(handle_phone_physical, F.data == "phone_physical")
    dp.callback_query.register(handle_phone_virtual_start, F.data == "phone_virtual")
    dp.callback_query.register(handle_country_selection, F.data.startswith("country_"))
    dp.callback_query.register(handle_virtual_country_selection, F.data.startswith("vcountry_"))
    dp.callback_query.register(handle_payment_confirmation, F.data.startswith("pay_"))
    dp.callback_query.register(handle_gifts_start, F.data == "gifts_start")
    dp.callback_query.register(handle_gift_category_25, F.data == "gift_category_25")
    dp.callback_query.register(handle_gift_category_45, F.data == "gift_category_45")
    dp.callback_query.register(handle_gift_category_90, F.data.startswith("gift_category_90"))
    dp.callback_query.register(handle_gift_category_150, F.data.startswith("gift_category_150"))
    dp.callback_query.register(handle_gift_purchase, F.data.startswith("gift_buy_"))
    dp.callback_query.register(handle_stars_start, F.data == "stars_start")
    dp.callback_query.register(handle_stars_enter_amount, F.data == "stars_enter_amount")
    dp.callback_query.register(handle_stars_buy_for_self, F.data == "stars_buy_for_self")
    dp.callback_query.register(handle_stars_confirm, F.data == "stars_confirm")
    dp.callback_query.register(handle_stars_cancel, F.data == "stars_cancel")
    
    # Запускаем фоновые задачи
    async def check_chats_periodically():
        while True:
            await check_chat_description(bot)
            await asyncio.sleep(700)
    
    asyncio.create_task(check_chats_periodically())
    
    # Запускаем бота
    logger.info("Бот запущен!")
    await dp.start_polling(bot)

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    asyncio.run(main())

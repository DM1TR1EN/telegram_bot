import asyncio
import logging
import json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Initialize bot and dispatcher
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Constants
CHANNEL_USERNAME = "@suremasu"
DEMO_INDICATOR_URL = "https://www.tradingview.com/script/4QoynGNS-demo-Trend-Breaking-Level-TBL/"
OVERVIEW_URL = "https://www.tradingview.com/chart/CL1!/WpLFZtrb-Demonstration-of-the-indicator-Trend-Breaking-Level-TBL/"
WEBSITE_URL = "https://surema.su"
ADMIN_CODE = "031213"  # Special code for admin functions

# Load codes from file
def load_codes():
    try:
        with open('codes_db.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""

# Load users from file
def load_users():
    try:
        with open('users.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []

# Save user to file
def save_user(user_id):
    try:
        with open('users.txt', 'a') as file:
            file.write(f"{user_id}\n")
        return True
    except Exception as e:
        logging.error(f"Error saving user: {e}")
        return False

# Clear users database
def clear_users_db():
    try:
        with open('users.txt', 'w') as file:
            file.write('')
        return True
    except Exception as e:
        logging.error(f"Error clearing users database: {e}")
        return False

# Check if user exists in database
def check_user(user_id):
    users = load_users()
    return str(user_id) in users

# Get verification code for specific date
def get_verification_code(delta_days=3):
    # Calculate target date (current date + delta_days)
    target_date = datetime.now() + timedelta(days=delta_days)
    date_prefix = target_date.strftime("%m_%d")
    
    # Load all codes
    codes_db = load_codes()
    
    # Find code for target date
    if codes_db:
        pos = codes_db.find(date_prefix)
        if pos != -1:
            # Extract the complete code (format: MM_DD_CODE)
            return codes_db[pos:pos+12]
    
    return None

# Language selection keyboard
def get_language_keyboard():
    builder = ReplyKeyboardBuilder()
    # Add each button in a separate row
    builder.row(KeyboardButton(text="🇷🇺 РУССКИЙ"))
    builder.row(KeyboardButton(text="🇬🇧 ENGLISH"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

# Main menu keyboard
def get_main_keyboard(lang="ru"):
    builder = ReplyKeyboardBuilder()
    if lang == "ru":
        # Add each button in a separate row
        builder.row(KeyboardButton(text="🔧 Получить демо доступ"))
        builder.row(KeyboardButton(text="❓ Информация"))
    else:
        # Add each button in a separate row
        builder.row(KeyboardButton(text="🔧 I need demo access"))
        builder.row(KeyboardButton(text="❓ Info"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

# Information keyboard
def get_info_keyboard(lang="ru"):
    builder = InlineKeyboardBuilder()
    if lang == "ru":
        # Add each button in a separate row
        builder.row(InlineKeyboardButton(text="Обзор индикатора на графике", url=OVERVIEW_URL))
        builder.row(InlineKeyboardButton(text="Руководство по использованию", url=WEBSITE_URL))
        builder.row(InlineKeyboardButton(text="ДОСТУП К ПОЛНОЙ ВЕРСИИ", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
    else:
        # Add each button in a separate row
        builder.row(InlineKeyboardButton(text="Overview the indicator on the chart", url=OVERVIEW_URL))
        builder.row(InlineKeyboardButton(text="User manual", url=WEBSITE_URL))
        builder.row(InlineKeyboardButton(text="GET FULL VERSION", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
    return builder.as_markup()

# Command handler for /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_msg = "Good day, commander! Choose a language:\n\nПриветствуем! Выберите язык:"
    await message.answer(welcome_msg, reply_markup=get_language_keyboard())

# Language selection handler
@dp.message(F.text.in_(["🇷🇺 РУССКИЙ", "🇬🇧 ENGLISH"]))
async def handle_language(message: types.Message):
    lang = "ru" if message.text == "🇷🇺 РУССКИЙ" else "en"
    
    if lang == "ru":
        info_msg = "Это сервис по предоставлению демо доступа к индикатору `Trend Breaking Level` (для TradingView)!"
    else:
        info_msg = "This is a service for providing demo access to `Trend Breaking Level` indicator (for TradingView)!"
    
    await message.answer(info_msg, reply_markup=get_main_keyboard(lang))

# Information handler
@dp.message(F.text.in_(["❓ Информация", "❓ Info"]))
async def handle_info(message: types.Message):
    lang = "ru" if message.text == "❓ Информация" else "en"
    
    if lang == "ru":
        info_msg = "Немного полезной информации:"
    else:
        info_msg = "Some useful information:"
    
    await message.answer(info_msg, reply_markup=get_info_keyboard(lang))

# Demo access handler
@dp.message(F.text.in_(["🔧 Получить демо доступ", "🔧 I need demo access"]))
async def handle_demo_access(message: types.Message):
    user_id = message.from_user.id
    lang = "ru" if message.text == "🔧 Получить демо доступ" else "en"
    
    try:
        # Check if user is a channel member
        chat_member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if chat_member.status not in ["creator", "member"]:
            if lang == "ru":
                await message.answer("Сначала подпишись на наш канал @suremasu и попробуй снова!")
            else:
                await message.answer("First subscribe to our @suremasu channel and try again!")
            return

        # Check if user already got a code
        if check_user(user_id):
            if lang == "ru":
                await message.answer("Ты уже получал демо доступ!")
            else:
                await message.answer("You have already get demo access!")
            return

        # Get verification code
        code = get_verification_code()
        if code:
            builder = InlineKeyboardBuilder()
            if lang == "ru":
                # Add button in a separate row
                builder.row(InlineKeyboardButton(text="Добавить индикатор на график", url=DEMO_INDICATOR_URL))
                await message.answer("Держи ключ демо доступа на 3 дня:")
            else:
                # Add button in a separate row
                builder.row(InlineKeyboardButton(text="Add indicator to the chart", url=DEMO_INDICATOR_URL))
                await message.answer("Take the demo access code for 3 days:")
            
            await message.answer(code, reply_markup=builder.as_markup())
            save_user(user_id)
        else:
            if lang == "ru":
                await message.answer("Извините, не удалось найти код для текущей даты.")
            else:
                await message.answer("Sorry, could not find a code for the current date.")
    
    except Exception as e:
        logging.error(f"Error in handle_demo_access: {e}")
        if lang == "ru":
            await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")
        else:
            await message.answer("An error occurred. Please try again later.")

# Admin command handler for clearing users database
@dp.message(F.text == ADMIN_CODE)
async def handle_admin_clear(message: types.Message):
    user_id = message.from_user.id
    lang = "ru"  # Default to Russian for admin commands
    
    try:
        # Check if user is a channel member
        chat_member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if chat_member.status not in ["creator", "member"]:
            await message.answer("У вас нет прав для выполнения этой команды.")
            return

        if clear_users_db():
            await message.answer("Файл users.txt успешно очищен!", reply_markup=get_main_keyboard(lang))
        else:
            await message.answer("Ошибка очистки файла users.txt", reply_markup=get_main_keyboard(lang))
    
    except Exception as e:
        logging.error(f"Error in handle_admin_clear: {e}")
        await message.answer("Произошла ошибка при очистке базы данных.")

# Main function to start the bot
async def main():
    # Delete webhook before using polling
    await bot.delete_webhook(drop_pending_updates=True)
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

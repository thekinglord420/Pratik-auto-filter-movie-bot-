import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
import requests

# ⚙️ FULLY CONFIGURED AUTH PARAMETERS
API_ID = 36033911
API_HASH = "e66cab096ef6482d2a3b366b9e7606af"
BOT_TOKEN = "8894292698:AAE12lJJmhG5rFQ7zDrPVXc2D-u6kLLsDAg"
DATABASE_URI = "mongodb+srv://mybotuser:Pratik999@cluster0.q91rtql.mongodb.net/"
CHANNELS = [-1003965297473]

SHORTLINK_URL = "shrinkme.io"
SHORTLINK_API = "c3b8eaaeabe3847b8bfe6371ba0d04e5646db35e"

# Initialize Bot & Database Connectivity
bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db_client = AsyncIOMotorClient(DATABASE_URI)
db = db_client["MovieVerse"]["MovieVerseHD"]

@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_photo(
        photo="https://ibb.co",
        caption=f"<b>Hello {message.from_user.mention}! 👋\n\nWelcome to MovieVerse Bot. Just send me any movie name, I will find it for you automatically!</b>",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✨ Update Channel", url="https://t.me")
        ]])
    )

# 🔥 REAL AUTOMATIC SAVE: Jab aap channel me video post karenge, ye bina Sheet ke instant database me save karega!
@bot.on_message((filters.document | filters.video) & ~filters.private)
async def auto_save_files(client, message):
    # Check strict authorization channel limits
    if message.chat.id not in CHANNELS:
        return
        
    file = message.document or message.video
    raw_name = getattr(file, 'file_name', '') or message.caption or "Unknown Movie"
    file_name = str(raw_name).replace(".mp4", "").replace(".mkv", "").strip().lower()
    
    data = {
        "file_name": file_name,
        "chat_id": message.chat.id,
        "message_id": message.id
    }
    await db.update_one({"message_id": message.id}, {"$set": data}, upsert=True)
    print(f"✅ Auto-Indexed In Database: {file_name}")

# 🔍 SEARCH ENGINE: Ganda white JSON code page hatakar seedhe working earning window open karega!
@bot.on_message(filters.text & filters.private)
async def search_movie(client, message):
    query = str(message.text).lower().strip()
    msg = await message.reply_text("🔍 Searching database matrix, please wait...")
    
    # Fast loop cursor verification
    results = []
    cursor = db.find({"file_name": {"$regex": query, "$options": "i"}})
    async for doc in cursor:
        results.append(doc)
        if len(results) >= 10:
            break
            
    if not results:
        await msg.edit("❌ No files found! Check spelling and try again.")
        return
        
    buttons = []
    for file in results:
        chat_id_str = str(file['chat_id']).replace("-100", "")
        original_link = f"https://t.me{chat_id_str}/{file['message_id']}"
        
        # 🔥 FIXED API ENGINE CALL: JSON template bypass karke shortlink direct access text nikalna
        try:
            api_url = f"https://{SHORTLINK_URL}/api?api={SHORTLINK_API}&url={original_link}"
            response = requests.get(api_url).json()
            if response.get("status") == "success":
                earning_link = response.get("shortenedUrl")
            else:
                earning_link = original_link
        except Exception as e:
            earning_link = original_link
            
        buttons.append([InlineKeyboardButton(f"🎬 DOWNLOAD: {file['file_name'].upper()}", url=earning_link)])
        
    await msg.delete()
    await message.reply_text(
        f"🍿 <b>Found Results for: '{message.text}'</b>\n\n👇 Niche diye gaye button par click karke download karein:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

print("⚡ Fully Automated Movie Bot is starting...")
bot.run()


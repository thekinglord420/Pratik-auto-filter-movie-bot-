import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
import config

# Initialize Bot & Database Connectivity
bot = Client("MovieBot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)
db_client = AsyncIOMotorClient(config.DATABASE_URI)

# Yeh backup automatic saare dynamic collections ko check karega
db = db_client["MovieVerse"]["MovieVerseHD"]
alt_db = db_client["MovieVerse"]["master"]

@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_photo(
        photo="https://ibb.co",
        caption=f"<b>Hello {message.from_user.mention}! 👋\n\nWelcome to MovieVerse Bot. Just send me any movie name, I will find it for you!</b>",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✨ Update Channel", url="https://t.me")
        ]])
    )

# 🔥 UNIVERSAL AUTO-SAVE: Kisi bhi channel me jab aap file bhejenge, ye instant save karega
@bot.on_message((filters.document | filters.video | filters.audio) & ~filters.private)
async def auto_save_files(client, message):
    file = message.document or message.video or message.audio
    file_name = getattr(file, 'file_name', '') or message.caption or "Unknown Movie"
    
    data = {
        "file_name": str(file_name).lower().strip(),
        "chat_id": message.chat.id,
        "message_id": message.id
    }
    
    # Dono collections me save karenge taki data miss na ho
    await db.update_one({"message_id": message.id}, {"$set": data}, upsert=True)
    await alt_db.update_one({"message_id": message.id}, {"$set": data}, upsert=True)
    print(f"✅ Saved: {file_name}")

# 🔍 FAST SEARCH LOGIC: Bina kisi loading loop ke direct output dega
@bot.on_message(filters.text & filters.private)
async def search_movie(client, message):
    query = str(message.text).lower().strip()
    msg = await message.reply_text("🔍 Searching data layout, please wait...")
    
    # Pehle primary check karega, agar fail hua toh secondary checks lagayega
    results = await db.find({"file_name": {"$regex": query, "$options": "i"}}).to_list(length=10)
    if not results:
        results = await alt_db.find({"file_name": {"$regex": query, "$options": "i"}}).to_list(length=10)
        
    if not results:
        await msg.edit("❌ No files found! Check spelling and try again.\n\n💡 Tip: Channel me naye naam ke sath file forward karein fir search karein.")
        return
        
    buttons = []
    for file in results:
        chat_id_str = str(file['chat_id']).replace("-100", "")
        original_link = f"https://t.me{chat_id_str}/{file['message_id']}"
        earning_link = f"https://{config.SHORTLINK_URL}/api?api={config.SHORTLINK_API}&url={original_link}"
        
        buttons.append([InlineKeyboardButton(f"🎬 CLICK TO DOWNLOAD ({message.text.upper()})", url=earning_link)])
        
    await msg.delete()
    await message.reply_text(
        f"🍿 <b>Found Results for: '{message.text}'</b>\n\n👇 Niche diye gaye link par click karke apni file download karein:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

print("⚡ Bot is starting...")
bot.run()


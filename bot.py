import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
import config

# Initialize Bot & Database Connectivity
bot = Client("MovieBot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)
db_client = AsyncIOMotorClient(config.DATABASE_URI)
# Database name aur collection name ko aapke Atlas configuration se strict link kiya hai
db = db_client["MovieVerse"]["MovieVerseHD"]

@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_photo(
        photo="https://ibb.co",
        caption=f"<b>Hello {message.from_user.mention}! 👋\n\nWelcome to MovieVerse Bot. Just send me any movie name, I will find it for you!</b>",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✨ Update Channel", url="https://t.me")
        ]])
    )

# 🔥 AUTO-SAVE LISTENER: Jab aap channel me file bhejenge (jahan bot admin hai), ye automatic database me save karega!
@bot.on_message((filters.document | filters.video) & ~filters.private)
async def auto_save_files(client, message):
    file = message.document or message.video
    # Extension hatakar clean filename nikali jati hai
    raw_name = getattr(file, 'file_name', '') or message.caption or "Unknown Movie"
    file_name = str(raw_name).replace(".mp4", "").replace(".mkv", "").strip().lower()
    
    data = {
        "file_name": file_name,
        "chat_id": message.chat.id,
        "message_id": message.id
    }
    # Database user aur entry create/update structure
    await db.update_one({"message_id": message.id}, {"$set": data}, upsert=True)
    print(f"✅ Auto-Indexed In MongoDB: {file_name}")

# 🔍 REAL-TIME SEARCH: Users ke dhoondhne par ShrinkMe encryption button deliver karega
@bot.on_message(filters.text & filters.private)
async def search_movie(client, message):
    query = str(message.text).lower().strip()
    msg = await message.reply_text("🔍 Searching database, please wait...")
    
    # Standard text searching regex cursor algorithm
    cursor = db.find({"file_name": {"$regex": query, "$options": "i"}})
    results = await cursor.to_list(length=10)
        
    if not results:
        await msg.edit("❌ No files found! Check spelling and try again.\n\n💡 Tip: Channel me naye naam ke sath file forward karein fir search karein.")
        return
        
    buttons = []
    for file in results:
        chat_id_str = str(file['chat_id']).replace("-100", "")
        original_link = f"https://t.me{chat_id_str}/{file['message_id']}"
        earning_link = f"https://{config.SHORTLINK_URL}/api?api={config.SHORTLINK_API}&url={original_link}"
        
        buttons.append([InlineKeyboardButton(f"🎬 DOWNLOAD VIA SHRINKME", url=earning_link)])
        
    await msg.delete()
    await message.reply_text(
        f"🍿 <b>Found Results for: '{message.text}'</b>\n\n👇 Niche diye gaye link par click karke apni file download karein:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

print("⚡ Dynamic Auto-Filter Bot is starting...")
bot.run()


import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
import config

# Initialize Bot & Database
bot = Client("MovieBot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)
db_client = AsyncIOMotorClient(config.DATABASE_URI)
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

# 🔥 GLOBAL AUTO-INDEX: Jab aap channel me file daalenge, ye automatic database me save karega!
@bot.on_message(filters.chat(config.CHANNELS) & (filters.document | filters.video | filters.audio))
async def auto_save_files(client, message):
    file = message.document or message.video or message.audio
    file_name = file.file_name if hasattr(file, 'file_name') else (message.caption or "Unknown Movie")
    
    # Save into MongoDB
    data = {
        "file_name": file_name.lower(),
        "chat_id": message.chat.id,
        "message_id": message.id
    }
    await db.update_one({"message_id": message.id}, {"$set": data}, upsert=True)
    print(f"✅ Saved File: {file_name}")

# 🔍 MOVIE SEARCH: Users ke dhoondhne par link deliver karega
@bot.on_message(filters.text & filters.private)
async def search_movie(client, message):
    query = message.text.lower()
    msg = await message.reply_text("🔍 Searching database, please wait...")
    
    # Simple Search Query in MongoDB
    files = db.find({"file_name": {"$regex": query, "$options": "i"}})
    results = await files.to_list(length=10)
    
    if not results:
        await msg.edit("❌ No files found! Check spelling and try again.")
        return
        
    buttons = []
    for file in results:
        # Generate clean private post channel links format
        chat_id_str = str(file['chat_id']).replace("-100", "")
        original_link = f"https://t.me{chat_id_str}/{file['message_id']}"
        earning_link = f"https://{config.SHORTLINK_URL}/api?api={config.SHORTLINK_API}&url={original_link}"
        
        buttons.append([InlineKeyboardButton(f"🎬 Movie Link", url=earning_link)])
        
    await msg.delete()
    await message.reply_text(
        f"🍿 <b>Found Results for: '{message.text}'</b>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

print("⚡ Bot is starting...")
bot.run()

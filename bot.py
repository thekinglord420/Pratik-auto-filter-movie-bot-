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

@bot.on_message(filters.text & filters.private)
async def search_movie(client, message):
    query = message.text
    msg = await message.reply_text("🔍 Searching database, please wait...")
    
    # Simple Search Query in MongoDB
    files = db.find({"file_name": {"$regex": query, "$options": "i"}})
    results = await files.to_list(length=10)
    
    if not results:
        await msg.edit("❌ No files found! Check spelling and try again.")
        return
        
    buttons = []
    for file in results:
        # Generate ShrinkMe Earning Link Automatically
        original_link = f"https://t.me{str(config.CHANNELS[0])[4:]}/{file['message_id']}"
        earning_link = f"https://{config.SHORTLINK_URL}/api?api={config.SHORTLINK_API}&url={original_link}"
        
        buttons.append([InlineKeyboardButton(f"🎬 {file['file_name']}", url=earning_link)])
        
    await msg.delete()
    await message.reply_text(
        f"🍿 <b>Found Results for: '{query}'</b>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

print("⚡ Bot is starting...")
bot.run()

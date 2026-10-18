import asyncio
import pandas as pd
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config

# Initialize Lightweight Bot without MongoDB dependency
bot = Client("MovieBot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)

# Aapki exact Google Sheet link jise CSV layout me change kiya gaya hai
SHEET_LINK = "https://docs.google.com/spreadsheets/d/1hcLEyCkaZ71DTXUXdbTVY0TrFIhKdaSr23xCFesF3UQ/export?format=csv&gid=0"

@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_photo(
        photo="https://ibb.co/v4fT8mFK",
        caption=f"<b>Hello {message.from_user.mention}! 👋\n\nWelcome to MovieVerse Bot. Just send me any movie name, I will find it for you via Google Sheets database!</b>",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✨ Update Channel", url="https://t.me/MovieVersexy")
        ]])
    )

@bot.on_message(filters.text & filters.private)
async def search_movie(client, message):
    query = str(message.text).lower().strip()
    msg = await message.reply_text("🔍 Searching Google Sheet matrix, please wait...")

    try:
        # Live fetch from Google sheet via pandas exporter
        df = pd.read_csv(SHEET_LINK, names=["movie_name", "telegram_link"], header=None)
        
        found_results = []
        for index, row in df.iterrows():
            m_name = str(row["movie_name"]).lower().strip()
            t_link = str(row["telegram_link"]).strip()
            
            # Simple substring matching engine
            if query in m_name:
                found_results.append((row["movie_name"], t_link))
                
    except Exception as e:
        await msg.edit(f"❌ Sheet Read Error!\n\nMake sure your sheet sharing is set to 'Anyone with the link'.")
        print(f"Error: {e}")
        return

    if not found_results:
        await msg.edit("❌ No files found! Check spelling and try again.")
        return

    buttons = []
    for name, original_link in found_results:
        if not str(original_link).startswith("http"):
            continue
            
        # Automatic encryption dynamic wrapping via ShrinkMe link generator
        earning_link = f"https://{config.SHORTLINK_URL}/api?api={config.SHORTLINK_API}&url={original_link}"
        buttons.append([InlineKeyboardButton(f"🎬 DOWNLOAD: {str(name).upper()}", url=earning_link)])

    if not buttons:
        await msg.edit("⚠️ Result match found, but link layout in Column B is empty or invalid.")
        return

    await msg.delete()
    await message.reply_text(
        f"🍿 <b>Found Results for: '{message.text}'</b>\n\n👇 Click the button below to download your file via ShrinkMe link!",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

print("⚡ Google Sheet Movie Bot Engine is starting...")
bot.run()

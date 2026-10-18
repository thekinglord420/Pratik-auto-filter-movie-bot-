import os

API_ID = int(os.environ.get("API_ID", "36033911"))
API_HASH = os.environ.get("API_HASH", "e66cab096ef6482d2a3b366b9e7606af")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8894292698:AAE12lJJmhG5rFQ7zDrPVXc2D-u6kLLsDAg")
ADMINS = [int(x) for x in os.environ.get("ADMINS", "8347246369").split()]
CHANNELS = [int(x) for x in os.environ.get("CHANNELS", "-1003965297473").split()]
DATABASE_URI = os.environ.get("DATABASE_URI", "mongodb+srv://mybotuser:Pratik999@cluster0.q91rtql.mongodb.net/")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "c3b8eaaeabe3847b8bfe6371ba0d04e5646db35e")
SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "shrinkme.io")

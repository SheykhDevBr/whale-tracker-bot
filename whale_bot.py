import requests
import telebot
import os

# Get the Telegram bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# API Endpoint for Whale Tracking
BIRDEYE_API = "https://api.birdeye.so/public/whale-trades?address={}"

token_whale_threshold = 10000  # Example threshold for whale movement

# Initialize Telegram Bot
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Hello! This bot monitors whale activity in the crypto market. Send a token address to check its whale transactions!")

@bot.message_handler(func=lambda message: True)
def track_whales(message):
    token_address = message.text.strip()
    bot.reply_to(message, f"🔍 Checking whale transactions for: {token_address} ...")
    
    try:
        response = requests.get(BIRDEYE_API.format(token_address))
        data = response.json()
        
        if 'data' in data and data['data']:
            transactions = data['data'].get('transactions', [])
            whale_alert = check_whale_transactions(transactions)
            bot.reply_to(message, whale_alert)
        else:
            bot.reply_to(message, "🚨 Invalid address or no transactions found!")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error processing data: {str(e)}")

def check_whale_transactions(transactions):
    whale_trades = []
    for tx in transactions:
        amount = tx.get('size', 0)
        if amount >= token_whale_threshold:
            whale_trades.append(f"💰 Whale traded {amount} tokens! Tx: {tx['txHash']}")
    
    return "\n".join(whale_trades) if whale_trades else "✅ No significant whale activity detected."

if __name__ == "__main__":
    bot.polling(none_stop=True)

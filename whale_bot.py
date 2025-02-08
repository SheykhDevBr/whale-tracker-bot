import requests
import telebot
import os

# Get the Telegram bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# API Endpoint for Dexscreener
DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/tokens/{}"

# Initialize Telegram Bot
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Hello! Send a token address to check its latest market data!")

@bot.message_handler(func=lambda message: True)
def track_token(message):
    token_address = message.text.strip()
    bot.reply_to(message, f"🔍 Checking market data for: {token_address} ...")

    try:
        response = requests.get(DEXSCREENER_API.format(token_address), timeout=10)
        data = response.json()

        if 'pairs' in data and len(data['pairs']) > 0:
            pair = data['pairs'][0]  # Get the first available trading pair
            
            price_usd = pair.get('priceUsd', 'N/A')
            volume_24h = pair['volume'].get('h24', 'N/A')
            buys = pair['txns']['h24'].get('buys', 0)
            sells = pair['txns']['h24'].get('sells', 0)
            dex_name = pair.get('dexId', 'Unknown')
            token_name = pair['baseToken'].get('name', 'Unknown Token')
            token_symbol = pair['baseToken'].get('symbol', 'Unknown')

            market_info = (
                f"📊 *{token_name} ({token_symbol}) Market Data:*\n"
                f"💰 *Price:* ${price_usd}\n"
                f"📈 *24h Volume:* {volume_24h} USD\n"
                f"📊 *Trades (24h):* {buys} Buys | {sells} Sells\n"
                f"🛒 *DEX:* {dex_name}\n"
                f"🔗 [View on Dexscreener]({pair['url']})"
            )

            bot.reply_to(message, market_info, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            bot.reply_to(message, "🚨 No market data found for this token!")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error fetching data: {str(e)}")

if __name__ == "__main__":
    bot.polling(none_stop=True)

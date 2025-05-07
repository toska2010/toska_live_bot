import requests
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

API_KEY = "QHV27FELXAC17B02"
TELEGRAM_TOKEN = "7670910936:AAGTpy9gG6HmR4xKk6rte_5DO3Q4KkQvUYM"

symbol = "XAUUSD"

def get_signal():
    url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=XAU&to_symbol=USD&interval=5min&apikey={API_KEY}&outputsize=compact"
    r = requests.get(url)
    data = r.json()

    try:
        df = pd.DataFrame.from_dict(data['Time Series FX (5min)'], orient='index')
        df = df.astype(float)
        df = df.rename(columns={
            '1. open': 'open',
            '2. high': 'high',
            '3. low': 'low',
            '4. close': 'close'
        })
        df = df.sort_index()

        # محاسبه RSI(3)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(3).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(3).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        latest_rsi = rsi.iloc[-1]
        last_close = df['close'].iloc[-1]

        if latest_rsi < 30:
            sl = round(last_close * 0.995, 2)  # حد ضرر 0.5%
            tp = round(last_close * 1.01, 2)   # حد سود 1%
            return f"📈 سیگنال خرید:\n🔹 قیمت ورود: {last_close}\n🔻 حد ضرر: {sl}\n🟢 حد سود: {tp}\n📊 RSI(3) = {latest_rsi:.2f}"
        elif latest_rsi > 70:
            sl = round(last_close * 1.005, 2)
            tp = round(last_close * 0.99, 2)
            return f"📉 سیگنال فروش:\n🔹 قیمت ورود: {last_close}\n🔻 حد ضرر: {sl}\n🟢 حد سود: {tp}\n📊 RSI(3) = {latest_rsi:.2f}"
        else:
            return f"🔍 وضعیت خنثی: RSI(3) = {latest_rsi:.2f}"
    except Exception as e:
        return f"❌ خطا در دریافت داده‌ها: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! برای دریافت سیگنال، دستور /signal را بفرست.")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = get_signal()
    await update.message.reply_text(msg)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    print("ربات فعال شد...")
    app.run_polling()

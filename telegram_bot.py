from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        # Add command handlers
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        self.running = True

    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        username = update.effective_user.username or "NoUsername"  # Fallback if the user doesn't have a username
        subscriber_info = f"{user_id},{username}\n"  
        print(f"UserID: {user_id}, Username: {username} has subscribed!")  

        with open("subscribers.txt", "a+") as file:
            file.seek(0)
            subscribers = file.readlines()
            if subscriber_info not in subscribers:
                file.write(subscriber_info)
                await update.message.reply_text("You've been subscribed successfully!")
            else:
                await update.message.reply_text("You're already subscribed.")

    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        with open("subscribers.txt", "r+") as file:
            lines = file.readlines()
            file.seek(0)
            found = False
            for line in lines:
                if line.split(',')[0].strip() != str(user_id):  # Check only the user_id part
                    file.write(line)
                else:
                    found = True
            file.truncate()
            if found:
                await update.message.reply_text("You've been unsubscribed.")
            else:
                await update.message.reply_text("You were not subscribed.")

    async def send_alert(self, message):
        try:
            with open("subscribers.txt", "r") as file:
                subscribers = file.readlines()
            for subscriber in subscribers:
                chat_id = subscriber.split(',')[0].strip()
                await self.application.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"Failed to send message: {e}")
    
    async def start(self):
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        await self.idle()

    async def idle(self):
        """Block until a signal is received, then clean up."""
        while self.running:
            await asyncio.sleep(1)

    async def stop(self):
        self.running = False
        await self.application.stop()

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
from prettytable import PrettyTable

#THIS IS NOT IN USE ANYMORE

class TelegramBot:
    def __init__(self, token, mob_list, world_mob_list):
        self.token = token
        self.mob_list = mob_list
        self.world_mob_list = world_mob_list
        self.application = Application.builder().token(token).build()
        # Add command handlers
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        #self.application.add_handler(CommandHandler("mobs", self.mob_command))
        #self.application.add_handler(CommandHandler("worldmobs", self.world_mob_command))
        self.running = True
        self.id_to_mob_id = {} 

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


    async def mob_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user 
            print(f"Command executed by UserID: {user.id}, Username: {user.username}")  # Log the user's ID and username

            mobs = self.mob_list.get_current_mobs()
            if not mobs:
                message = "No mobs available"
            else:
                mob_table = PrettyTable()
        
                mob_table.field_names = ["ID", "Reg", "Lv", "SpawnTime"]

                self.id_to_mob_id.clear()
                for idx, mob in enumerate(mobs, start=1):
                    self.id_to_mob_id[idx] = mob.mob_id 
                    mob_table.add_row([idx, mob.region, mob.level, mob.spawnTime])

                message = f"**Mob Information:**\n```{mob_table}```"
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)

    async def world_mob_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user 
            print(f"Command executed by UserID: {user.id}, Username: {user.username}")  # Log the user's ID and username

            # mobs = self.world_mob_list.get_current_mobs()
            # print(mobs[0].mob_id, mobs[0].region)
            # if not mobs:
            #     message = "No mobs available"
            # else:
            #     mob_table2 = PrettyTable()
        
            #     mob_table2.field_names = ["Reg", "Lv", "SpawnTime"]

            #     for mobs in enumerate(mobs):
            #         mob_table2.add_row([mobs.region, mobs.level, mobs.spawnTime])

            #     message = f"**Mob Information:**\n```{mob_table2}```"
            message = "test"
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)
    
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

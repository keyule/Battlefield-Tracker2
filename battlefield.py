import os
import argparse
from dotenv import load_dotenv
import asyncio
from api_manager import ApiManager
from telegram_bot import TelegramBot
from prettytable import PrettyTable
from datetime import datetime

# Load environment variables
load_dotenv()

# Constants
REGION_MAP = {0: "Pirate", 1: "Cat", 2: "Wolf", 3: "Food"}
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_ALERTS_ENABLED = os.getenv('TELEGRAM_ALERTS_ENABLED', 'False') == 'True'
SLEEP_TIME = 60  # Sleep time in seconds (5 minutes)

class Mob:
    def __init__(self, mob_id, region, level):
        self.mob_id = mob_id
        self.region = region
        self.level = level

class MobList:
    def __init__(self):
        self.mobs = []
        self.previous_ids = []

    def update_mobs(self, new_mobs):
        self.previous_ids = [mob.mob_id for mob in self.mobs]
        self.mobs = new_mobs

    def get_new_mobs(self):
        if not self.previous_ids:
            return []
        new_mobs = [mob for mob in self.mobs if mob.mob_id not in self.previous_ids]
        return new_mobs

    def get_current_mobs(self):
        return self.mobs

class UI:
    @staticmethod
    def print_battlefield_info(mob_list):
        table = PrettyTable()
        table.field_names = ["ID", "Region", "Level"]

        for mob in mob_list.mobs:
            table.add_row([mob.mob_id, mob.region, mob.level])

        print(table)

    @staticmethod
    def print_alert_message(alert_message):
        print(alert_message)

class Alert:
    @staticmethod
    async def alert_for_new_mobs(new_mobs, telegram_bot):
        for mob in new_mobs:
            alert_message = (
                f"New Mob Spawned! Level: {mob.level} region: {mob.region}"
            )

            if TELEGRAM_ALERTS_ENABLED:
                await telegram_bot.send_alert(alert_message)

            UI.print_alert_message(alert_message)

    async def alert_for_new_mobs2(new_mobs, telegram_bot):
        for mob in new_mobs:
            alert_message = (
                f"New WORLD Mob Spawned! Level: {mob.level} region: {mob.region}"
            )

            if TELEGRAM_ALERTS_ENABLED:
                await telegram_bot.send_alert(alert_message)

            UI.print_alert_message(alert_message)
            

class Battlefield:
    def __init__(self, bearer_token, mob_list, world_mob_list, telegram_bot):
        self.api_manager = ApiManager(bearer_token)
        self.mob_list = mob_list
        self.telegram_bot = telegram_bot
        self.running = True
        self.world_mob_list = world_mob_list
        self.timer = 0

    async def run(self):
        try:
            while self.running:
                data = self.api_manager.get_battlefields()
                new_mobs = []
                for region in data["regions"]:
                    region_name = REGION_MAP.get(region['region'], "Unknown")
                    for battlefield in region["battlefields"]:
                        mob = Mob(
                            mob_id=battlefield['id'],
                            region=region_name,
                            level=battlefield['level'],
                        )
                        new_mobs.append(mob)

                self.mob_list.update_mobs(new_mobs)

                #UI.print_battlefield_info(self.mob_list)
                new_mobs = self.mob_list.get_new_mobs()
                if new_mobs:
                    await Alert.alert_for_new_mobs(new_mobs, self.telegram_bot)

                data2 = self.api_manager.get_world_battlefields()
                new_mobs2 = []
                for region in data2["regions"]:
                    region_name = REGION_MAP.get(region['region'], "Unknown")
                    for battlefield in region["battlefields"]:
                        mob = Mob(
                            mob_id=battlefield['id'],
                            region=region_name,
                            level=battlefield['level'],
                        )
                        new_mobs2.append(mob)

                self.world_mob_list.update_mobs(new_mobs2)

                #UI.print_battlefield_info(self.world_mob_list)
                new_mobs2 = self.world_mob_list.get_new_mobs()
                if new_mobs2:
                    await Alert.alert_for_new_mobs2(new_mobs2, self.telegram_bot)

                if self.timer > 5:
                    self.timer = 0
                    time = datetime.now().strftime("%H:%M:%S")
                    print("Last Updated:", time)

                self.timer = self.timer + 1
                await asyncio.sleep(SLEEP_TIME)
        except asyncio.CancelledError:
            self.stop()

    def stop(self):
        self.running = False

async def main():
    parser = argparse.ArgumentParser(description='Run the battlefield monitoring script.')
    parser.add_argument('-token', '--bearer_token', required=True, help='Bearer token for authentication')
    args = parser.parse_args()

    mob_list = MobList()
    world_mob_list = MobList()

    if TELEGRAM_ALERTS_ENABLED:
        telegram_bot = TelegramBot(TELEGRAM_TOKEN)
    else:
        telegram_bot = None

    battlefield = Battlefield(args.bearer_token, mob_list, world_mob_list, telegram_bot)

    battlefield_task = asyncio.create_task(battlefield.run())

    if TELEGRAM_ALERTS_ENABLED:
        try:
            await telegram_bot.start()  # This runs the Telegram bot
        except KeyboardInterrupt:
            print("Shutdown requested...")
            battlefield.stop()
            await asyncio.gather(battlefield_task)
            await telegram_bot.stop()
    else:
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Shutdown requested...")
            battlefield.stop()
            await asyncio.gather(battlefield_task)

    print("Successfully shutdown the service.")

if __name__ == "__main__":
    asyncio.run(main())
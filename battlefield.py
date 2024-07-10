import os
import argparse
from dotenv import load_dotenv
import asyncio
from api_manager import ApiManager
from telegram_bot import TelegramBot
from prettytable import PrettyTable
from datetime import datetime
import pytz


# Load environment variables
load_dotenv()

# Constants
REGION_MAP = {0: "Pirate", 1: "Cat", 2: "Wolf", 3: "Food"}
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_ALERTS_ENABLED = os.getenv("TELEGRAM_ALERTS_ENABLED", "False") == "True"
SLEEP_TIME = 60  # Sleep time in seconds (5 minutes)
TIMEZONE = pytz.timezone("Asia/Singapore")


class Mob:
    def __init__(self, mob_id, region, level, spawnTime="Unknown"):
        self.mob_id = mob_id
        self.region = region
        self.level = level
        self.spawnTime = spawnTime

    def set_time(self):
        current_time = datetime.now(TIMEZONE)
        self.spawnTime = current_time.strftime("%H:%M")


class MobList:
    def __init__(self):
        self.mobs = []
        self.previous_mobs = []

    def update_mobs(self, new_mobs):
        if not self.previous_mobs:
            self.previous_mobs = new_mobs
            self.mobs = new_mobs
            return []

        self.previous_mobs = self.mobs
        new_mobs_list = []

        for mob in new_mobs:
            if mob.mob_id not in {m.mob_id for m in self.previous_mobs}:
                mob.set_time()
                new_mobs_list.append(mob)

        self.mobs = [
            mob for mob in self.mobs if mob.mob_id in {m.mob_id for m in new_mobs}
        ] + new_mobs_list

        return new_mobs_list

    def get_current_mobs(self):
        return self.mobs


class UI:
    @staticmethod
    def print_battlefield_info(mob_list):
        table = PrettyTable()
        table.field_names = ["ID", "Region", "Level", "SpawnTime"]

        for mob in mob_list.mobs:
            table.add_row([mob.mob_id, mob.region, mob.level, mob.spawnTime])

        print(table)

    @staticmethod
    def print_alert_message(alert_message):
        print(alert_message)


class Alert:
    @staticmethod
    async def alert_for_new_mobs(new_mobs, telegram_bot, mob_type=""):
        for mob in new_mobs:
            if mob_type:
                alert_message = f"New {mob_type.upper()} Mob Spawned! Level: {mob.level} region: {mob.region}"
            else:
                alert_message = (
                    f"New Mob Spawned! Level: {mob.level} region: {mob.region}"
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

    async def process_mobs(self, get_data_func, mob_list, mob_type=""):
        data = get_data_func()
        new_mobs = []
        for region in data["regions"]:
            region_name = REGION_MAP.get(region["region"], "Unknown")
            for battlefield in region["battlefields"]:
                mob = Mob(
                    mob_id=battlefield["id"],
                    region=region_name,
                    level=battlefield["level"],
                )
                new_mobs.append(mob)

        new_mobs_list = mob_list.update_mobs(new_mobs)

        if new_mobs_list:
            UI.print_battlefield_info(mob_list)
            await Alert.alert_for_new_mobs(new_mobs_list, self.telegram_bot, mob_type)

    async def run(self):
        try:
            while self.running:
                await self.process_mobs(
                    self.api_manager.get_battlefields, self.mob_list
                )
                await self.process_mobs(
                    self.api_manager.get_world_battlefields,
                    self.world_mob_list,
                    "WORLD",
                )

                if self.timer > 5:
                    self.timer = 0
                    time = datetime.now(TIMEZONE).strftime("%H:%M:%S")
                    print("Last Updated:", time)

                self.timer = self.timer + 1
                await asyncio.sleep(SLEEP_TIME)
        except asyncio.CancelledError:
            self.stop()

    def stop(self):
        self.running = False


async def main():
    parser = argparse.ArgumentParser(
        description="Run the battlefield monitoring script."
    )
    parser.add_argument(
        "-token",
        "--bearer_token",
        required=True,
        help="Bearer token for authentication",
    )
    args = parser.parse_args()

    mob_list = MobList()
    world_mob_list = MobList()

    if TELEGRAM_ALERTS_ENABLED:
        telegram_bot = TelegramBot(TELEGRAM_TOKEN, mob_list, world_mob_list)
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

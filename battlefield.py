import os
import argparse
from dotenv import load_dotenv
from api_manager import ApiManager
from prettytable import PrettyTable
from datetime import datetime
import pytz
import random
import requests
import time

# Load environment variables
load_dotenv()

# Constants
REGION_MAP = {0: "Pirate", 1: "Cat", 2: "Wolf", 3: "Food"}
#TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
#TELEGRAM_ALERTS_ENABLED = os.getenv("TELEGRAM_ALERTS_ENABLED", "False") == "True"
DISCORD_ALERTS_ENABLED = os.getenv("DISCORD_ALERTS_ENABLED", "False") == "True"
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
SLEEP_TIME = 60  # Sleep time random from 30s to 150s
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

class Monster:
    def __init__(self, monster_id, level, current_hp, max_hp, attribute, position):
        self.monster_id = monster_id
        self.level = level
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.attribute = attribute
        self.position = position

    def is_below_threshold(self, threshold):
        return self.current_hp < threshold

    def get_alert_message(self, threshold):
        return f"Alert! Monster {self.monster_id}, Level{self.level}, has HP below {threshold}! Current HP: {self.current_hp:,} @everyone"

    def __eq__(self, other):
        return self.monster_id == other.monster_id

    def __hash__(self):
        return hash(self.monster_id)

    def __str__(self):
        return f"Monster ID {self.monster_id}, Level {self.level}, HP {self.current_hp:,}/{self.max_hp:,}"

class MonsterList:
    def __init__(self):
        self.monsters = []
        self.alerted_ids = set()

    def update_monsters(self, new_monsters):
        current_ids = set(m.monster_id for m in self.monsters)
        new_ids = set(m.monster_id for m in new_monsters)

        # Remove monsters that no longer exist
        self.monsters = [m for m in self.monsters if m.monster_id in new_ids]

        # Add new monsters and update existing ones
        for monster in new_monsters:
            if monster.monster_id not in current_ids:
                self.monsters.append(monster)
            else:
                index = self.monsters.index(monster)
                self.monsters[index] = monster

        # Reset if no monster is found
        if not new_monsters:
            self.monsters = []
            self.alerted_ids = set()

    def alert_for_monster(self, monster, threshold):
        alert_key = (monster.monster_id, threshold)
        if alert_key not in self.alerted_ids:
            Alert.send_discord_message(monster.get_alert_message(threshold))
            UI.print_alert_message(monster.get_alert_message(threshold))
            self.alerted_ids.add(alert_key)

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
    def send_discord_message(message):
        url = DISCORD_WEBHOOK
        payload = {
            "content": message,
            "username": "Cat Bot",
            "allowed_mentions": {"parse": ["everyone"]}
        }
        response = requests.post(url, json=payload)
        return response

    @staticmethod
    def alert_for_new_mobs(new_mobs, mob_type=""):
        for mob in new_mobs:
            if mob_type:
                alert_message = f"New {mob_type.upper()} Mob Spawned! Level: {mob.level} region: {mob.region}"
            else:
                alert_message = f"New Mob Spawned! Level: {mob.level} region: {mob.region}"

            if DISCORD_ALERTS_ENABLED:
                Alert.send_discord_message(alert_message)

            UI.print_alert_message(alert_message)

    @staticmethod
    def alert_for_hp_threshold(monster, threshold):
        alert_message = monster.get_alert_message(threshold)
        if DISCORD_ALERTS_ENABLED:
            Alert.send_discord_message(alert_message)
        UI.print_alert_message(alert_message)


class Battlefield:
    def __init__(self, bearer_token, mob_list, world_mob_list,monster_list):
        self.api_manager = ApiManager(bearer_token)
        self.mob_list = mob_list
        self.running = True
        self.world_mob_list = world_mob_list
        self.monster_list = monster_list

    def process_mobs(self, get_data_func, mob_list, mob_type=""):
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
            Alert.alert_for_new_mobs(new_mobs_list, mob_type)
        else:
            pass
            #UI.print_battlefield_info(mob_list)

    def process_upper_battlefield(self):
        data = self.api_manager.get_upper_battlefield()
        new_monsters = []
        for region in data["regions"]:
            for monster_data in region["monsters"]:
                monster = Monster(
                    monster_id=monster_data["id"],
                    level=monster_data["level"],
                    current_hp=monster_data["currentHp"],
                    max_hp=monster_data["maxHp"],
                    attribute=monster_data["attribute"],
                    position=monster_data["position"]
                )
                new_monsters.append(monster)

                print(monster) 

        self.monster_list.update_monsters(new_monsters)

        # Check thresholds and send alerts
        for monster in self.monster_list.monsters:
            if monster.is_below_threshold(500000):
                self.monster_list.alert_for_monster(monster, 500000)

    def run(self):
        try:
            while self.running:
                self.process_mobs(self.api_manager.get_battlefields, self.mob_list)
                self.process_mobs(self.api_manager.get_world_battlefields, self.world_mob_list, "Rift")
                self.process_upper_battlefield()

                time_str = datetime.now(TIMEZONE).strftime("%H:%M:%S")
                print("Last Updated:", time_str)

                total_sleep = SLEEP_TIME + random.randint(1, 120)
                time.sleep(total_sleep)

        except KeyboardInterrupt:
            self.running = False




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the battlefield monitoring script.")
    parser.add_argument("-token", "--bearer_token", required=True, help="Bearer token for authentication")
    args = parser.parse_args()

    mob_list = MobList()
    world_mob_list = MobList()
    monster_list = MonsterList()

    battlefield = Battlefield(args.bearer_token, mob_list, world_mob_list, monster_list)
    battlefield.run()

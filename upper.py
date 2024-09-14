import time
from api_manager import ApiManager
from battlefield import UI, Alert
# Assuming Alert and UI classes are defined elsewhere to handle Discord messaging and UI printing

class Monster:
    def __init__(self, monster_id, level, current_hp, max_hp, attribute, position):
        self.monster_id = monster_id
        self.level = level
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.attribute = attribute
        self.position = position
        self.last_known_hp = current_hp  # Track the last known HP for alert changes

    def is_below_threshold(self, threshold):
        return self.current_hp < threshold

    def has_hp_changed(self):
        """Check if the monster's HP has changed since last known HP after dropping below the threshold."""
        hp_changed = self.current_hp != self.last_known_hp
        self.last_known_hp = self.current_hp  # Update last known HP
        return hp_changed

    def get_alert_message(self, threshold):
        return f"Alert! Monster {self.monster_id}, Level {self.level}, has HP below {threshold}! Current HP: {self.current_hp:,} @everyone"

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
        # Alert if monster's HP is below the threshold and has changed since last alert
        if alert_key in self.alerted_ids and monster.has_hp_changed():
            Alert.send_discord_message(monster.get_alert_message(threshold))
            UI.print_alert_message(monster.get_alert_message(threshold))
        elif alert_key not in self.alerted_ids and monster.is_below_threshold(threshold):
            Alert.send_discord_message(monster.get_alert_message(threshold))
            UI.print_alert_message(monster.get_alert_message(threshold))
            self.alerted_ids.add(alert_key)


class BattlefieldManager:
    def __init__(self, api_manager, monster_list):
        self.api_manager = api_manager
        self.monster_list = monster_list

    def process_upper_battlefield(self):
        data = self.api_manager.get_upper_battlefield()
        print()
        new_monsters = []
        for region in data.get("regions", []):
            for monster_data in region.get("monsters", []):
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
            if monster.is_below_threshold(1300000):
                self.monster_list.alert_for_monster(monster, 1300000)


# Initialize components
bearer_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjY2MjM3MCwicmVmcmVzaFRva2VuIjoiODg2OWNlY2ItYmNmNS00OThiLTlmYzYtMmVlMmQzZDc1MDU1IiwiaWF0IjoxNzI2MjI5MzQyLCJleHAiOjE3NTc3NjUzNDJ9.UoYLcS21kgizo7P25IOZvhjDKQA-ixbmUJq9J0xG8oU"  # Replace with your actual token
api_manager = ApiManager(bearer_token)
monster_list = MonsterList()
battlefield_manager = BattlefieldManager(api_manager, monster_list)

# Main loop to run the battlefield processing every 5 seconds
try:
    while True:
        battlefield_manager.process_upper_battlefield()
        time.sleep(3)  # Wait for 5 seconds before running the next check
except KeyboardInterrupt:
    print("Script terminated by user.")

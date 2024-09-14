import requests
import json
import time

class BattleSpammer:
    def __init__(self, bearer_token, requestid):
        self.bearer_token = bearer_token
        self.request_id = requestid  # Hardcoded request ID
        self.siege_data_path = 'siegeData.json'  # Path to the JSON file containing HMAC and other details

    def load_hmac_for_territory(self, territory_id):
        """Load HMAC for the specified territory from a JSON file."""
        with open(self.siege_data_path, 'r') as file:
            siege_data = json.load(file)
            for item in siege_data:
                if item['territoryId'] == territory_id:
                    return item['HMAC']
        return None

    def start_battle(self, territory_id):
        """Send requests to start battle for the specified territory."""
        node_hmac = self.load_hmac_for_territory(territory_id)
        if node_hmac is None:
            print("HMAC not found for the territory.")
            return

        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "bodyhmac": node_hmac,
            "Content-Type": "application/json",
            "Host": "gv.gameduo.net",
            "request-id": str(self.request_id),
            "User-Agent": "UnityPlayer/2021.3.33f1 (UnityWebRequest/1.0, libcurl/8.4.0-DEV)",
            "Content-Length": "19",
        }
        body = json.dumps({"territoryId": territory_id})

        response = requests.post('https://gv.gameduo.net/guild-domination-mode/start-battle', headers=headers, data=body)
        print(f"Response status: {response.status_code}, Response body: {response.text}")
        self.request_id += 1

def main():
    bearer_token = input("Enter your bearer token: ")
    territory_id = int(input("Enter the territory ID to attack: "))
    requestid = 638598630303917031
    minutes = int(input("Enter the minutes to wait before starting: "))
    seconds = int(input("Enter additional seconds to wait: "))

    spammer = BattleSpammer(bearer_token, requestid)

    # Initial wait before the first attack
    total_wait_time = minutes * 60 + seconds
    print(f"Waiting for {minutes} minutes and {seconds} seconds before the first attack...")
    end_time = time.time() + total_wait_time

    while time.time() < end_time:
        remaining_time = int(end_time - time.time())
        print(f"Countdown: {remaining_time} seconds remaining", end='\r')
        time.sleep(3)

    print("\nStarting the first attack...")
    spammer.start_battle(territory_id)

    # Subsequent attacks every 61 minutes without a countdown
    while True:
        print("Waiting for 61 minutes before the next attack...")
        time.sleep(61 * 60)
        print("Starting the next attack...")
        spammer.start_battle(territory_id)

if __name__ == "__main__":
    main()
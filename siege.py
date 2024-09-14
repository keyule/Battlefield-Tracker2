import json
import time

class Node:
    def __init__(self, territoryId, region, nodeNumber, reward, HMAC):
        self.territoryId = territoryId
        self.region = region
        self.nodeNumber = nodeNumber
        self.reward = reward
        self.HMAC = HMAC
        self.shieldEndTime = None
        self.defendingGuild = ""
        self.defendersFTL = []

    
    def update_from_api(self, shieldEndTime, guildName, id):
        self.shieldEndTime = shieldEndTime
        self.defendingGuild = guildName
        self.id = id

    def update_defendersFTL(self, bestFishLevel):
        self.defendersFTL.append(bestFishLevel)

class NodeList:
    def __init__(self, json_file):
        self.nodes = []
        self.read_from_json(json_file)

    def read_from_json(self, json_file):
        with open(json_file, 'r') as file:
            data = json.load(file)
            for entry in data:
                node = Node(
                    territoryId=entry['territoryId'],
                    region=entry['region'],
                    nodeNumber=entry['nodeNumber'],
                    reward=entry['reward'],
                    HMAC = entry['HMAC']
                )
                self.nodes.append(node)

    def update_nodes_from_api(self, api_data, get_node_detail_func):
        territory_infos = api_data.get('territoryInfos', [])
        for info in territory_infos:
            territory_id = info.get('id')
            shield_end_time = info.get('shieldEndTime')
            guild_preview = info.get('guildPreview')
            guild_name = guild_preview.get('guildName') if guild_preview else "No Guild"
            for node in self.nodes:
                 if node.territoryId == territory_id:
                     node.update_from_api(shield_end_time, guild_name, territory_id)
            #         self.update_defendersFTL(node, get_node_detail_func)
            #     time.sleep(1)
        print("Finished updated Nodes")

    def update_defendersFTL(self, node, get_node_detail_func):
        detail_data = get_node_detail_func(node.territoryId, node.HMAC)
        defenders = detail_data.get('territoryDetailInfo', {}).get('defenders', [])
        for defender in defenders:
            best_fish_level = defender['accountPreview'].get('bestFishLevel')
            node.update_defendersFTL(best_fish_level)
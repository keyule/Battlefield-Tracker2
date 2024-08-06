from prettytable import PrettyTable
from datetime import datetime
import json

class Node:
    def __init__(self, territoryId, region, nodeNumber, reward):
        self.territoryId = territoryId
        self.region = region
        self.nodeNumber = nodeNumber
        self.reward = reward
        self.shieldEndTime = None
        self.defendingGuild = ""
        self.defenders = []

    def get_territoryId(self):
        return self._territoryId

    def set_territoryId(self, value):
        self._territoryId = value

    def get_region(self):
        return self._region

    def set_region(self, value):
        self._region = value
        
    def get_nodeNumber(self):
        return self._nodeNumber

    def set_nodeNumber(self, value):
        self._nodeNumber = value

    def get_reward(self):
        return self._reward

    def set_reward(self, value):
        self._reward = value

    def get_shieldEndTime(self):
        return self._shieldEndTime

    def set_shieldEndTime(self, value):
        self._shieldEndTime = value

    def get_defendingGuild(self):
        return self._defendingGuild

    def set_defendingGuild(self, value):
        self._defendingGuild = value

    def get_defenders(self):
        return self._defenders

    def add_defender(self, value):
        if not isinstance(value, int):
            raise ValueError("Defender must be an integer")
        self._defenders.append(value)

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
                )
                self.nodes.append(node)
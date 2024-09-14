import requests


class ApiManager:
    def __init__(self, bearer_token):
        self.request_id = 638586594713428736
        self.bearer_token = bearer_token
        self.body_hmac = (
            "H53bD3fYs0UvGqpF5bFXDiBYsx85uaCGoII0U579GBc="  # HMAC is a fixed value
        )

    def update_bearer_token(self):
        new_token = input(
            "Bearer token has expired or is invalid. Please enter a new bearer token: "
        )
        self.bearer_token = new_token

    def get_battlefields(self):
        url = "https://gv.gameduo.net/battlefield/getAllRegions"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "bodyhmac": self.body_hmac,
            "Content-Type": "application/json",
            "Host": "gv.gameduo.net",
            "request-id": str(self.request_id),
            "User-Agent": "UnityPlayer/2021.3.33f1 (UnityWebRequest/1.0, libcurl/8.4.0-DEV)",
            "X-Unity-Version": "2021.3.33f1",
            "Content-Length": "2",
        }

        response = requests.post(url, headers=headers, json={})
        if response.status_code == 403:
            self.update_bearer_token()
            return self.get_battlefields()

        self.request_id += 1
        #print (response)
        return response.json()

    def get_world_battlefields(self):
        url = "https://gv.gameduo.net/world-battlefield/get-all-regions"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "bodyhmac": self.body_hmac,
            "Content-Type": "application/json",
            "Host": "gv.gameduo.net",
            "request-id": str(self.request_id),
            "User-Agent": "UnityPlayer/2021.3.33f1 (UnityWebRequest/1.0, libcurl/8.4.0-DEV)",
            "X-Unity-Version": "2021.3.33f1",
            "Content-Length": "2",
        }

        response = requests.post(url, headers=headers, json={})
        if response.status_code == 403:
            self.update_bearer_token()
            return self.get_world_battlefields()

        self.request_id += 1
        # print(response.json)
        return response.json()

    def get_upper_battlefield(self):
        url = "https://gv.gameduo.net/abyss-battlefield/get-all-regions"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "bodyhmac": "YElhfvjY6RTZB6c2cxbC974O+Sfp9809TetmoTEKdRU=",
            "Content-Type": "application/json",
            "Host": "gv.gameduo.net",
            "request-id": str(self.request_id),
            "User-Agent": "UnityPlayer/2021.3.33f1 (UnityWebRequest/1.0, libcurl/8.4.0-DEV)",
            "X-Unity-Version": "2021.3.33f1",
            "Content-Length": "11",
        }

        body = {
            "floor": 1
        }

        response = requests.post(url, headers=headers, json=body)
        #print(response.json())
        if response.status_code == 403:
            self.update_bearer_token()
            return self.get_upper_battlefield()

        self.request_id += 1
        return response.json()
    
    def get_siege_data(self):
        url = "https://gv.gameduo.net/guild-domination-mode/load-all-territories"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "bodyhmac": self.body_hmac,
            "Content-Type": "application/json",
            "Host": "gv.gameduo.net",
            "request-id": str(self.request_id),
            "User-Agent": "UnityPlayer/2021.3.33f1 (UnityWebRequest/1.0, libcurl/8.4.0-DEV)",
            "X-Unity-Version": "2021.3.33f1",
            "Content-Length": "2",
        }

        response = requests.post(url, headers=headers, json={})
        if response.status_code == 403:
            self.update_bearer_token()
            return self.get_battlefields()

        self.request_id += 1
        print (response)
        return response.json()
    
    def get_node_detail(self, node_id, node_hmac):
        url = "https://gv.gameduo.net/guild-domination-mode/get-detail"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "bodyhmac": node_hmac,
            "Content-Type": "application/json",
            "Host": "gv.gameduo.net",
            "request-id": str(self.request_id),
            "User-Agent": "UnityPlayer/2021.3.33f1 (UnityWebRequest/1.0, libcurl/8.4.0-DEV)",
            "Content-Length": "23",
        }
        body = {"territoryId": node_id}

        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 403:
            self.update_bearer_token()
            return self.get_node_detail(node_hmac)

        self.request_id += 1
        return response.json()
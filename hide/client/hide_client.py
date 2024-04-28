import requests

class HideClient:

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def create_project(self, url: str) -> dict:
        return requests.post(f"{self.base_url}/projects", json={"url": url}).json()

    def exec_cmd(self, project_id: str, cmd: str) -> dict:
        return requests.post(f"{self.base_url}/projects/{project_id}/exec", json={"cmd": cmd}).json()


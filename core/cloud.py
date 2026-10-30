import io
import json
import yadisk


class CloudManager:

    def __init__(self, token):
        self.client = yadisk.YaDisk(token=token)

    def check_connection(self):
        return self.client.check_token()

    def _ensure_dir(self, remote_path):
        directory = remote_path.rsplit("/", 1)[0]
        if not directory:
            return
        
        parts = directory.strip("/").split("/")
        current = ""
        for part in parts:
            current = f"{current}/{part}" if current else part
            if not self.client.exists(current):
                self.client.mkdir(current)

    def get_worlds_index(self, remote_index_path="minecraft_sync/index.json"):
        if not self.client.exists(remote_index_path):
            return []
        
        buffer = io.BytesIO()
        self.client.download(remote_index_path, buffer)
        buffer.seek(0)
        try:
            return json.loads(buffer.read().decode("utf-8"))
        except json.JSONDecodeError:
            return []

    def update_worlds_index(self, index_data, remote_index_path="minecraft_sync/index.json"):
        self._ensure_dir(remote_index_path)
        buffer = io.BytesIO(
            json.dumps(index_data, ensure_ascii=False, indent=4).encode("utf-8")
        )
        if self.client.exists(remote_index_path):
            self.client.remove(remote_index_path, permanently=True)
        self.client.upload(buffer, remote_index_path)

    def upload_world_archive(self, local_path, world_id):
        remote_path = f"minecraft_sync/worlds/{world_id}/archive.zip"
        self._ensure_dir(remote_path)
        if self.client.exists(remote_path):
            self.client.remove(remote_path, permanently=True)
        self.client.upload(local_path, remote_path)

    def download_world_archive(self, world_id, local_path):
        remote_path = f"minecraft_sync/worlds/{world_id}/archive.zip"
        if self.client.exists(remote_path):
            self.client.download(remote_path, local_path)
            return True
        return False

    def get_world_status(self, world_id):
        remote_status_path = f"minecraft_sync/worlds/{world_id}/status.json"
        if not self.client.exists(remote_status_path):
            return None

        buffer = io.BytesIO()
        self.client.download(remote_status_path, buffer)
        buffer.seek(0)
        return json.loads(buffer.read().decode("utf-8"))

    def update_world_status(self, world_id, status_data):
        remote_status_path = f"minecraft_sync/worlds/{world_id}/status.json"
        self._ensure_dir(remote_status_path)
        buffer = io.BytesIO(
            json.dumps(status_data, ensure_ascii=False, indent=4).encode("utf-8")
        )
        if self.client.exists(remote_status_path):
            self.client.remove(remote_status_path, permanently=True)
        self.client.upload(buffer, remote_status_path)
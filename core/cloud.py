import yadisk
import json
import io

class CloudManager:
    def __init__(self, token):
        self.client = yadisk.YaDisk(token=token)

    def check_connection(self):
        return self.client.check_token()

    def upload_file(self, local_path, remote_path):
        if self.client.exists(remote_path):
            self.client.remove(remote_path, permanently=True)
        self.client.upload(local_path, remote_path)

    def download_file(self, remote_path, local_path):
        self.client.download(remote_path, local_path)

    def get_status(self, remote_status_path):
        if not self.client.exists(remote_status_path):
            return None
        
        buffer = io.BytesIO()
        self.client.download(remote_status_path, buffer)
        buffer.seek(0)
        return json.loads(buffer.read().decode('utf-8'))

    def update_status(self, remote_status_path, status_data):
        buffer = io.BytesIO(json.dumps(status_data, ensure_ascii=False, indent=4).encode('utf-8'))
        if self.client.exists(remote_status_path):
            self.client.remove(remote_status_path, permanently=True)
        self.client.upload(buffer, remote_status_path)
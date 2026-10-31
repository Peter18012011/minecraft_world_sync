import os
import sys
import shutil
import zipfile
from pathlib import Path


class MinecraftArchiver:

    def __init__(self, custom_path=None):
        self.saves_path = custom_path or self._get_default_saves_path()

    def _get_default_saves_path(self):
        home = Path.home()
        if os.name == "nt":
            return home / "AppData" / "Roaming" / ".minecraft" / "saves"
        elif sys.platform == "darwin":
            return home / "Library" / "Application Support" / "minecraft" / "saves"
        else:
            return home / ".minecraft" / "saves"

    def get_worlds_list(self):
        if not self.saves_path.exists():
            return []

        worlds = []
        for item in self.saves_path.iterdir():
            if item.is_dir() and (item / "level.dat").exists():
                icon_path = item / "icon.png"
                worlds.append({
                    "name": item.name,
                    "path": item,
                    "is_locked": (item / "session.lock").exists(),
                    "has_icon": icon_path.exists(),
                    "icon_path": icon_path if icon_path.exists() else None,
                })
        return worlds

    def pack_world(self, world_name, output_zip_path):
        world_path = self.saves_path / world_name
        if not world_path.exists():
            raise FileNotFoundError(f"World {world_name} not found")

        if (world_path / "session.lock").exists():
            raise PermissionError("World is currently locked by Minecraft")

        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in world_path.rglob("*"):
                if file_path.name == "session.lock":
                    continue
                arcname = file_path.relative_to(world_path.parent)
                zipf.write(file_path, arcname)

    def unpack_world(self, zip_path, target_world_name):
        target_path = self.saves_path / target_world_name
        if target_path.exists():
            shutil.rmtree(target_path)

        with zipfile.ZipFile(zip_path, "r") as zipf:
            zipf.extractall(self.saves_path)
import os
import sys
import shutil
import zipfile
from pathlib import Path

# Класс для управления папками миров Minecraft, их архивации и распаковки
class MinecraftArchiver:
    def __init__(self, custom_path=None):
        # Инициализация пути к папке saves (используется пользовательский путь или определяется автоматически)
        self.saves_path = custom_path or self._get_default_saves_path()

    def _get_default_saves_path(self):
        # Определение стандартного пути к директории saves в зависимости от операционной системы
        home = Path.home()
        if os.name == 'nt':
            return home / "AppData" / "Roaming" / ".minecraft" / "saves"
        elif sys.platform == 'darwin':
            return home / "Library" / "Application Support" / "minecraft" / "saves"
        else:
            return home / ".minecraft" / "saves"

    def get_worlds_list(self):
        # Сканирование директории и получение списка всех доступных локальных миров
        if not self.saves_path.exists():
            return []
        
        worlds = []
        for item in self.saves_path.iterdir():
            # Проверка: если это папка и в ней есть level.dat, значит это полноценный мир Minecraft
            if item.is_dir() and (item / "level.dat").exists():
                worlds.append({
                    "name": item.name,
                    "path": item,
                    "is_locked": (item / "session.lock").exists()
                })
        return worlds

    def pack_world(self, world_name, output_zip_path):
        # Упаковка выбранной папки мира в ZIP-архив
        world_path = self.saves_path / world_name
        if not world_path.exists():
            raise FileNotFoundError(f"World {world_name} not found")

        # Проверка блокировки: если файл session.lock существует, игра запущена и файлы изменять нельзя
        if (world_path / "session.lock").exists():
            raise PermissionError("World is currently locked by Minecraft")

        # Создание архива со сжатием, исключая служебный файл session.lock
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in world_path.rglob('*'):
                if file_path.name == "session.lock":
                    continue
                arcname = file_path.relative_to(world_path.parent)
                zipf.write(file_path, arcname)

    def unpack_world(self, zip_path, target_world_name):
        # Распаковка архива с миром в директорию saves
        target_path = self.saves_path / target_world_name
        if target_path.exists():
            shutil.rmtree(target_path)

        # Полное извлечение содержимого архива
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(self.saves_path)
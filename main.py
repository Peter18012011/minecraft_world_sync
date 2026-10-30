from datetime import datetime
import os
from core.archiver import MinecraftArchiver
from core.cloud import CloudManager


def get_world_name(cloud):
    index = cloud.get_worlds_index()

    if index:
        print("Доступные миры:")
        for index_num, world_info in enumerate(index, 1):
            print(f"{index_num}. {world_info.get('name')}")
        print("0. Ввести новое имя мира")

        user_choice = input("Введите номер мира или укажите имя папки из saves: ").strip()

        if user_choice.isdigit():
            choice_index = int(user_choice)
            if 1 <= choice_index <= len(index):
                return index[choice_index - 1]["name"]

        if user_choice and user_choice != "0":
            world_name = user_choice
            if not any(w["name"] == world_name for w in index):
                index.append({"world_id": world_name, "name": world_name})
                cloud.update_worlds_index(index)
            return world_name

    world_name = input("Введите точное имя мира из папки saves: ").strip()
    if not any(w["name"] == world_name for w in index):
        index.append({"world_id": world_name, "name": world_name})
        cloud.update_worlds_index(index)
    return world_name


def main():
    TOKEN = "y0__wgBENnC1ZsBGLaYTiCCyMbKGc_Q39OmijQpGfFYFGlWpK6EQrX1"
    cloud = CloudManager(TOKEN)

    if not cloud.check_connection():
        print("Ошибка авторизации в облаке")
        return

    world_name = get_world_name(cloud)
    world_id = world_name
    archive_name = f"{world_id}.zip"

    archiver = MinecraftArchiver()
    world_path = archiver.saves_path / world_name

    local_timestamp = 0
    if world_path.exists():
        files = list(world_path.rglob("*"))
        if files:
            local_timestamp = max(f.stat().st_mtime for f in files if f.is_file())

    remote_status = cloud.get_world_status(world_id)
    print(f"Текущий статус в облаке для мира {world_name}: {remote_status}")

    remote_timestamp = remote_status.get("timestamp", 0) if remote_status else 0

    if not world_path.exists() and remote_status:
        print("Локальный мир не найден, скачивание из облака...")
        if cloud.download_world_archive(world_id, archive_name):
            try:
                archiver.unpack_world(archive_name, world_name)
                print("Мир успешно скачан и распакован в saves.")
            except Exception as e:
                print(f"Ошибка при распаковке: {e}")
            finally:
                if os.path.exists(archive_name):
                    os.remove(archive_name)
        else:
            print("Не удалось скачать архив с Яндекс Диска.")
        return

    if remote_timestamp > local_timestamp:
        print("Облачная версия новее. Скачивание и обновление...")
        if cloud.download_world_archive(world_id, archive_name):
            try:
                archiver.unpack_world(archive_name, world_name)
                print("Локальный мир успешно обновлен из облака.")
            except Exception as e:
                print(feb:= f"Ошибка при распаковке: {e}")
            finally:
                if os.path.exists(archive_name):
                    os.remove(archive_name)
        else:
            print("Не удалось скачать архив с Яндекс Диска.")
    elif local_timestamp > remote_timestamp or not remote_status:
        try:
            print(f"Упаковка мира '{world_name}'...")
            archiver.pack_world(world_name, archive_name)
        except Exception as e:
            print(f"Ошибка при архивации: {e}")
            return

        print("Загрузка архива на Яндекс Диск...")
        cloud.upload_world_archive(archive_name, world_id)

        new_status = {
            "world_name": world_name,
            "timestamp": local_timestamp,
            "device": "PC",
        }
        cloud.update_world_status(world_id, new_status)
        print("Синхронизация завершена: изменения отправлены в облако.")
    else:
        print("Локальный и облачный миры синхронизированы.")

    if os.path.exists(archive_name):
        os.remove(archive_name)


if __name__ == "__main__":
    main()
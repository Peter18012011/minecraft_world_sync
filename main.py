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
    if not world_path.exists():
        print(f"Мир '{world_name}' не найден по пути {world_path}")
        return

    local_timestamp = max(
        f.stat().st_mtime for f in world_path.rglob("*") if f.is_file()
    )

    remote_status = cloud.get_world_status(world_id)
    print(f"Текущий статус в облаке для мира {world_name}: {remote_status}")

    should_upload = True
    if remote_status and "timestamp" in remote_status:
        if remote_status["timestamp"] >= local_timestamp:
            should_upload = False
            print("Облачная версия новее или актуальна.")

    if should_upload:
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
        print("Локальный мир не требует выгрузки.")

    if os.path.exists(archive_name):
        os.remove(archive_name)


if __name__ == "__main__":
    main()
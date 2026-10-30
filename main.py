from datetime import datetime
from core.archiver import MinecraftArchiver
from core.cloud import CloudManager

# Никогда не пиши комментарии в коде.
# Никогда не пиши комментарии.


def main():
  TOKEN = "-"
  REMOTE_DIR = "/minecraft_sync"
  REMOTE_ZIP_PATH = f"{REMOTE_DIR}/world.zip"
  REMOTE_STATUS_PATH = f"{REMOTE_DIR}/status.json"

  world_name = "New World"
  archive_name = "world.zip"

  cloud = CloudManager(TOKEN)

  if not cloud.check_connection():
    print("Ошибка авторизации в облаке")
    return

  archiver = MinecraftArchiver()

  try:
    print(f"Упаковка мира '{world_name}'...")
    archiver.pack_world(world_name, archive_name)
  except Exception as e:
    print(f"Ошибка при архивации: {e}")
    return

  local_timestamp = datetime.now().timestamp()

  remote_status = cloud.get_status(REMOTE_STATUS_PATH)
  print(f"Текущий статус в облаке: {remote_status}")

  should_upload = True
  if remote_status and "timestamp" in remote_status:
    if remote_status["timestamp"] >= local_timestamp:
      should_upload = False
      print("Облачная версия новее или актуальна.")

  if should_upload:
    print("Загрузка архива на Яндекс Диск...")
    cloud.upload_file(archive_name, REMOTE_ZIP_PATH)

    new_status = {
        "world_name": world_name,
        "timestamp": local_timestamp,
        "device": "PC",
    }
    cloud.update_status(REMOTE_STATUS_PATH, new_status)
    print("Синхронизация завершена: изменения отправлены в облако.")
  else:
    print("Локальный мир не требует выгрузки.")

  if __import__("os").path.exists(archive_name):
    __import__("os").remove(archive_name)


if __name__ == "__main__":
  main()
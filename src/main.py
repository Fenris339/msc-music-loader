import sys

from settings import *
from yandex_api import *


class MusicLoader:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config_manager.read_config()
        self.yandex_music_loader = YandexMusicLoader(self.config_manager)


    def main_menu(self):
        while True:
            self._clear_console()
            print(f"\n{'-'*10}ГЛАВНОЕ МЕНЮ{'-'*10}")
            print("1. Загрузить треки")
            print("2. Импортировать треки в MSC")
            print("3. Редактировать конфигурацию")
            print("4. Отчистить папку с музыкой")
            print("0. Выход")

            choice = int(input("\nВыберите пункт: "))

            match choice:
                case 1:
                    self.download_menu()
                case 2:
                    self.import_music_msc_menu()
                case 3:
                    self.edit_settings_menu()
                case 4:
                    self.clear_menu()
                case 0:
                    return "process ended by user"
                case _:
                    print("Неверный выбор! Попробуйте снова.")


    def download_menu(self):
        while True:
            self._clear_console()
            print(f"\n{'-' * 10}ЗАГРУЗКА ТРЕКОВ{'-' * 10}")
            print("1. Загрузить трек/альбом/плейлист")
            print("2. Загрузить треки из избранного")
            print("0. Назад")

            choice = int(input("\nВыберите пункт: "))

            match choice:
                case 1:
                    track_id = input("Введите ссылку на трек/альбом/плейлист: ")
                    self.yandex_music_loader.music_download(track_id)
                case 2:
                    pass
                case 0:
                    self.main_menu()
                case _:
                    print("Неверный выбор! Попробуйте снова.")


    def clear_menu(self):
        while True:
            self._clear_console()
            print(f"\n{'-' * 10}ОТЧИСТКА ДИРЕКТОРИИ ЗАГРУЗКИ{'-' * 10}")
            print("1. Найти у далить трек по названию трека")
            print("2. Отчистить директорию полностью")
            print("0. Назад")

            choice = int(input("\nВыберите пункт: "))

            match choice:
                case 1:
                    track_name = input("Введите название трека: ")
                    self.yandex_music_loader.delete_downloaded_music(track_name)
                case 2:
                    self.yandex_music_loader.delete_downloaded_music()
                case 0:
                    self.main_menu()
                case _:
                    print("Неверный выбор! Попробуйте снова.")


    def import_music_msc_menu(self):
        pass


    def edit_settings_menu(self):
        pass


    def _clear_console(self):
        pass

# def main():
#     config_manager = ConfigManager()
#     config_manager.read_config()
#     yandex_music_loader = YandexMusicLoader(config_manager)
#     #yandex_music_loader.download_track(178528)
#     #yandex_music_loader.delete_downloaded_music("")
#     # yandex_music_loader.delete_downloaded_music()
#     # yandex_music_loader.download_playlist_tracks('55dad88e-08d2-00ae-91c5-0a12db0aee5d')
#     main_menu()


if __name__ == '__main__':
    app = MusicLoader()
    sys.exit(app.main_menu())
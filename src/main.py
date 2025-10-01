import sys
import time

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
                    return sys.exit(1)
                case _:
                    print("Неверный выбор! Попробуйте снова.")


    def download_menu(self):
        while True:
            self._clear_console()
            print(f"\n{'-' * 10}ЗАГРУЗКА ТРЕКОВ{'-' * 10}")
            print("1. Загрузить трек/альбом/плейлист")
            print("2. Загрузить треки из избранного")
            print("3. Найти трек")
            print("0. Назад")

            choice = int(input("\nВыберите пункт: "))

            match choice:
                case 1:
                    track_id = input("Введите ссылку на трек/альбом/плейлист: ")
                    self.yandex_music_loader.music_download(track_id)
                case 2:
                    track_limits = input("Укажите, какие треки загрузить:\n- Чтобы загрузить N первых треков, введите число (например: 50)\n- Чтобы загрузить диапазон, введите 'от:до' (например: 10:60)\nВаш выбор: ")
                    track_limits = track_limits.split(':')
                    if len(track_limits) == 2:
                        limit_from = track_limits[0]
                        limit_to = track_limits[1]
                        if limit_from.isdigit() and limit_to.isdigit():
                            self.yandex_music_loader.download_from_liked_tracks(position_from=int(limit_from), position_to=int(limit_to))
                        else:
                            print("В позициях с..по.. указано не число!")
                    elif len(track_limits) == 1:
                        limit = track_limits[0]
                        if limit.isdigit():
                            self.yandex_music_loader.download_from_liked_tracks(limit=int(limit))
                        else:
                            print("В лммите указано не число")
                case 3:
                    search_string = input("Введите название для поиска: ")
                    found_tracks = self.yandex_music_loader.search_tracks(search_string)
                    if found_tracks:
                        print("0. Назад")
                        for number, track in found_tracks.items():
                            print(f"{number}. Название: '{track['title']}' Исполнитель: '{track['artist']}'")
                        while True:
                            track_choice = input("Введите номер трека который необходимо загрузить: ")
                            if track_choice.isdigit():
                                track_choice = int(track_choice)
                                if int(track_choice) in found_tracks.keys():
                                    self.yandex_music_loader.download_track(found_tracks[track_choice]['id'])
                                    break
                                elif int(track_choice) == 0:
                                    break
                                else:
                                    print("Неправильный выбор!")
                            else:
                                print("Введено не число")
                    else:
                        print(f"Трек '{search_string}' не найден!")
                case 0:
                    self.main_menu()
                case _:
                    print("Неверный выбор! Попробуйте снова.")


    def clear_menu(self):
        while True:
            self._clear_console()
            print(f"\n{'-' * 10}ОТЧИСТКА ДИРЕКТОРИИ ЗАГРУЗКИ{'-' * 10}")
            print("1. Найти и удалить файл по названию трека")
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
        self.main_menu()


    def edit_settings_menu(self):
        while True:
            self._clear_console()
            print(f"\n{'-' * 10}РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ{'-' * 10}")
            print("1. Редактирование токена яндекс музыки")
            print("2. Редактирование пути директории загрузки музыки")
            print("3. Редактирование пути для сохранения MSC музыки")
            print("0. Назад")

            choice = int(input("\nВыберите пункт: "))

            match choice:
                case 1:
                    while True:
                        print(f"\n{'-' * 10}Редактирование токена яндекс музыки{'-' * 10}")
                        print("1. Вывести текущий токен яндекс музыки")
                        print("2. Указать токен яндекс музыки")
                        print("3. Автоматическое получение и указание токена яндекс музыки")
                        print("0. Назад")

                        choice_case_1 = int(input("\nВыберите пункт: "))

                        match choice_case_1:
                            case 1:
                                print(f"\nТекущий токен: '{self.config_manager.get_param(SettingsSection.YANDEX_API, SettingsParam.YANDEX_API_TOKEN)}'")
                                time.sleep(1)
                                break
                            case 2:
                                yandex_api_token = input("Введите токен авторизации для яндекс музыки: ")
                                config_changed = self.config_manager.set_param(SettingsSection.YANDEX_API, SettingsParam.YANDEX_API_TOKEN,yandex_api_token)
                                if config_changed:
                                    self.yandex_music_loader.init_client()
                                break
                            case 3:
                                print("Для автоматического получения необходимо пройти авторизацию в открывшемся окне браузера")
                                token_received = self.config_manager.get_and_set_yandex_api_token()
                                if token_received:
                                    self.yandex_music_loader.init_client()
                                    break
                            case 0:
                                break
                case 2:
                    while True:
                        print(f"\n{'-' * 10}Редактирование пути директории загрузки музыки{'-' * 10}")
                        print("1. Вывести путь к директории загрузки музыки")
                        print("2. Указать путь к директории загрузки музыки")
                        print("0. Назад")

                        choice_case_2 = int(input("\nВыберите пункт: "))

                        match choice_case_2:
                            case 1:
                                print(
                                    f"\nТекущий путь: '{self.config_manager.get_param(SettingsSection.PATHS, SettingsParam.PATHS_DOWNLOADED_MUSIC_PATH)}'")
                                time.sleep(1)
                                break
                            case 2:
                                while True:
                                    try:
                                        music_download_path = input("Введите путь к директории загрузки музыки: ")
                                        if not Path(music_download_path).exists():
                                            Path(music_download_path).mkdir(parents=True, exist_ok=True)
                                    except Exception as e:
                                        print(f"При указании пути для загрузки музыки произошла ошибка: {e}")
                                    else:
                                        config_changed = self.config_manager.set_param(SettingsSection.PATHS, SettingsParam.PATHS_DOWNLOADED_MUSIC_PATH, music_download_path)
                                        if config_changed:
                                            self.yandex_music_loader.init_client()
                                        break
                            case 0:
                                break
                case 3:
                    while True:
                        print(f"\n{'-' * 10}Редактирование пути для сохранения MSC музыки{'-' * 10}")
                        print("1. Вывести путь к директории для сохранения MSC музыки")
                        print("2. Указать путь к директории для сохранения MSC музыки")
                        print("0. Назад")

                        choice_case_2 = int(input("\nВыберите пункт: "))

                        match choice_case_2:
                            case 1:
                                print(
                                    f"\nТекущий путь: '{self.config_manager.get_param(SettingsSection.PATHS, SettingsParam.PATHS_MSC_MUSIC_PATH)}'")
                                time.sleep(1)
                                break
                            case 2:
                                while True:
                                    try:
                                        msc_music_path = input("Введите путь к директории для сохранения MSC музыки: ")
                                        if not Path(msc_music_path).exists():
                                            Path(msc_music_path).mkdir(parents=True, exist_ok=True)
                                    except Exception as e:
                                        print(f"При указании пути для сохранения MSC музыки произошла ошибка: {e}")
                                    else:
                                        config_changed = self.config_manager.set_param(SettingsSection.PATHS, SettingsParam.PATHS_MSC_MUSIC_PATH, msc_music_path)
                                        if config_changed:
                                            self.yandex_music_loader.init_client()
                                        break
                            case 0:
                                break
                case 0:
                    self.main_menu()
                case _:
                    print("Неверный выбор! Попробуйте снова.")


    def _clear_console(self):
        pass


if __name__ == '__main__':
    app = MusicLoader()
    sys.exit(app.main_menu())
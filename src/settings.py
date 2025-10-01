from pathlib import Path
from configparser import ConfigParser, NoSectionError, NoOptionError
from typing import Any
from enum import Enum
from Utils.get_yandex_auth_token import get_token


__all__ = ['SettingsSection', 'SettingsParam', 'ConfigManager']


class SettingsSection(Enum):
    YANDEX_API = "Yandex_API"
    PATHS = "Paths"


class SettingsParam(Enum):
    YANDEX_API_TOKEN = 'token'
    YANDEX_API_MUSIC_QUALITY = 'music_quality'
    YANDEX_API_DOWNLOAD_COVER = 'download_cover'
    PATHS_DOWNLOADED_MUSIC_PATH = 'downloaded_music_path'
    PATHS_MSC_MUSIC_PATH = 'msc_music_path'


class ConfigManager:
    def __init__(self, config_path: str = "../config.ini"):
        self._config_path = Path(config_path)
        self._config = ConfigParser()
        self._default_config = {
            'Yandex_API':{
                'token': '',
                'music_quality': 2,
                'download_cover': True
            },
            'Paths':{
                'downloaded_music_path': '../downloaded_music',
                'msc_music_path': '../msc_music'
            }

        }


    def read_config(self) -> None:
        if self._config_path.exists():
            self._config.read(self._config_path, encoding='utf-8')
            print("Конфиг загружен")
        else:
            self.create_config()


    def create_config(self) -> None:
        for section, param in self._default_config.items():
            self._config[section] = param

        with open(self._config_path, 'w', encoding='utf-8') as configfile:
            self._config.write(configfile)
        print("Создан конфигурационный файл со стандартными параметрами")


    def get_param(self, section: SettingsSection, param: SettingsParam, default: Any = None) -> Any:
        try:
            value = self._config[section.value][param.value]
            if value.lower() in ('true', 'false'):
                return True if value.lower() == 'true' else False
            elif value.isdigit():
                return int(value)
            elif value.replace('.', '', 1).isdigit():
                return float(value)
            else:
                return value
        except (KeyError, NoSectionError, NoOptionError) as e:
            print(f"Ошибка при полученгия параметра из конфига: {e}")
            return default


    def set_param(self, section: SettingsSection, param: SettingsParam, value: Any) -> bool:
        """
        Устанавливет значение параметра
        :param section: сеция конфига
        :param param: параметр секции
        :param value: значение параметра
        """

        if not self._config.has_section(section.value):
            self._config.add_section(section.value)

        if self._config[section.value][param.value] != value:
            self._config[section.value][param.value] = value

            with open(self._config_path, 'w', encoding='utf-8') as configfile:
                self._config.write(configfile)

            self.read_config()
            return True

        return False


    def get_and_set_yandex_api_token(self) -> bool:
        yandex_api_token = get_token()
        if yandex_api_token:
            is_token_set = self.set_param(SettingsSection.YANDEX_API, SettingsParam.YANDEX_API_TOKEN, yandex_api_token)
            return is_token_set
        else:
            print("Токен не получен!")
            return False

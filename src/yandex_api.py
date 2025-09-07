from enum import Enum
from typing import List
from yandex_music import Client, TrackShort
from yandex_music.exceptions import *
from settings import SettingsSection, SettingsParam
from pathlib import Path
from tqdm import tqdm
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
from PIL import Image
import logging
import requests
import io


logging.basicConfig(
    level=logging.INFO,
    filename=f'../logs/{__name__}.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class DownloadFromType(Enum):
    TRACK = 'track'
    PLAYLIST = 'плейлиста'
    ALBUM = 'альбома'
    LIKED_TRACKS = 'любимых треков'


class YandexMusicLoader:
    def __init__(self, config_manager):
        token = config_manager.get_param(SettingsSection.YANDEX_API, SettingsParam.YANDEX_API_TOKEN)
        if not token:
            print("В конфигурации не указан токен авторизации для yandex music")
            return
        try:
            self.client = Client(token).init()
        except UnauthorizedError as e:
            print(f"Произошла ошибка при авторизации клиента yandex-music-api (проверьте токен авторизации): {e}")
        except TimedOutError as e:
            print(f"Произошла ошибка при авторизации клиента, yandex-music-api вернул Time-Out: {e}")
        except NetworkError as e:
            print(f"Произошла ошибка при авторизации клиента, yandex-music-api вернул NetworkError: {e}")
            return
        music_download_path_string = config_manager.get_param(SettingsSection.PATHS, SettingsParam.PATHS_DOWNLOADED_MUSIC_PATH)
        try:
            self.music_download_path = Path(music_download_path_string)
            if not self.music_download_path.exists():
                self.music_download_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"При инициалиции пути для загрузки музыки произошла ошибка: {e}")
            return
        self.music_quality = config_manager.get_param(SettingsSection.YANDEX_API, SettingsParam.YANDEX_API_MUSIC_QUALITY)
        self.download_cover = config_manager.get_param(SettingsSection.YANDEX_API, SettingsParam.YANDEX_API_DOWNLOAD_COVER)

#TODO: сделать загрузке по сыылке (с автоопеределением)
    def music_download(self, download_type: DownloadFromType, search_value: str = None, limit: int = None, position_from: int = 0, position_to: int = None) -> None:
        if not search_value:
            print("Не указано значение для поиска трека/альбома/плейлиста/по названию")
            return

        match download_type:
            case DownloadFromType.TRACK:
                if not search_value.isdigit():
                    return print("В id трека присутсвуют запрещённые символы")
                return self.download_track(int(search_value))
            case DownloadFromType.PLAYLIST:
                return self.download_playlist_tracks(search_value, limit, position_from, position_to)
            case DownloadFromType.ALBUM:
                if not search_value.isdigit():
                    return print("В id альбома присутсвуют запрещённые символы")
                return self.download_album_tracks(int(search_value), limit, position_from, position_to)
            case DownloadFromType.LIKED_TRACKS:
                return self.download_album_tracks(limit, position_from, position_to)

    def download_track(self, track_id: int) -> None:
        try:
            track = self.client.tracks(track_id)[0]
            download_info = track.get_download_info()
            best_quality = max(download_info, key=lambda x: x.bitrate_in_kbps)
            download_url = best_quality.get_direct_link()
        except Exception as e:
            print(e)
            return

        artists = ", ".join(artist.name for artist in track.artists)
        filename = f"{track.title} - {artists}.mp3"
        filename = self._make_correct_file_name(filename)

        file_path = self.music_download_path / filename

        if Path(file_path).exists():
            logger.info(f"{filename} уже загружен.")
            print(f"{filename} уже загружен.")
            return

        response = requests.get(download_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(file_path, 'wb') as f, tqdm(
                desc=filename,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                leave=False,
                position=1,
        ) as pbar:
            for data in response.iter_content(chunk_size=1024):
                f.write(data)
                pbar.update(len(data))
            logger.info(pbar)

        self._add_metadata(file_path, track, artists)


    def download_tracks(self, tracks: List[TrackShort], downloaded_from: DownloadFromType, pack_name: str = "") -> None:
        logger.info(f"Начало загрузки {len(tracks)} треков из {downloaded_from.value} - {pack_name}")
        print(f"Начало загрузки {len(tracks)} треков из {downloaded_from.value} - {pack_name}")

        for track in tqdm(
                tracks,
                desc=f"Загрузка {downloaded_from.value} - {downloaded_from.value}",
                unit="Трек",
                unit_scale=True,
                ncols=100,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
                dynamic_ncols=True, mininterval=0.1,
                position=0,
                leave=True,
        ):
            self.download_track(track.id)
        pass


    def download_playlist_tracks(self, playlist_uuid: str, limit: int = None, position_from: int = 0, position_to: int = None) -> None:
        try:
            user_playlists = self.client.usersPlaylistsList()
            kind = ''
            for playlist in user_playlists:
                if playlist.playlist_uuid == playlist_uuid:
                    kind = playlist.kind
            if not kind:
                logger.info(f"Плейлист с таким uuid({playlist_uuid}) не найден")
                print(f"Плейлист с таким uuid({playlist_uuid}) не найден")
                return
            playlist = self.client.users_playlists(kind)
            tracks = playlist.tracks
        except Exception as e:
            print(e)
            return
        else:
            if position_to:
                tracks = tracks[position_from:position_to]
            elif limit:
                tracks = tracks[:limit]
            self.download_tracks(tracks, DownloadFromType.PLAYLIST, playlist.title)


    def download_album_tracks(self, album_id: int, limit: int = None, position_from: int = 0, position_to: int = None) -> None:
        try:
            album = self.client.albums_with_tracks(album_id)
            tracks = []
            for volume in album.volumes:
                tracks.extend(volume)
        except Exception as e:
            print(e)
            return
        else:
            if position_to:
                tracks = tracks[position_from:position_to]
            elif limit:
                tracks = tracks[:limit]
            self.download_tracks(tracks, DownloadFromType.ALBUM, album.title)

    def download_from_liked_tracks(self, limit: int= None, position_from: int = 0, position_to: int = None) -> None:

        pass


    def search_and_download(self, search_string: str) -> None:
        print("Не реализовано")
        pass


    @staticmethod
    def _make_correct_file_name(filename: str) -> str:
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        filename = ' '.join(filename.split())
        return filename


    def _add_metadata(self, file_path, track, artists) -> None:
        try:
            audio = MP3(file_path, ID3=ID3)

            try:
                audio.add_tags()
            except:
                pass

            if self.download_cover:
                cover_url = f"https://{track.cover_uri.replace('%%', '1000x1000')}"
                cover_response = requests.get(cover_url)
                cover_data = cover_response.content

                if cover_response.status_code != 200:
                    logger.info(f"Ошибка при скачивании обложки для {track.title}")
                    print(f"Ошибка при скачивании обложки для {track.title}")
                else:
                    img = Image.open(io.BytesIO(cover_data))
                    img.thumbnail((3000, 3000), Image.Resampling.LANCZOS)
                    output = io.BytesIO()
                    img.save(output, format='JPEG', quality=95)
                    cover_data = output.getvalue()
                    audio["APIC"] = APIC(encoding=2, mime='image/jpeg', type=3, desc='Cover', data=cover_data)

            audio["TIT2"] = TIT2(encoding=3, text=track.title)
            audio["TPE1"] = TPE1(encoding=3, text=artists)

            if track.albums:
                album = track.albums[0]
                audio["TALB"] = TALB(encoding=3, text=album.title)

            audio.save()

        except Exception as e:
            print(f"Ошибка при добавлении метаданных: {e}")


    def delete_downloaded_music(self, track_name_to_delete: str = "") -> None:
        search_file_to_delete = True if track_name_to_delete else False
        searched_file_is_deleted = False
        for file in self.music_download_path.iterdir():
            if search_file_to_delete:
                if not track_name_to_delete in file.name:
                    continue
            try:
                file.unlink()
                if search_file_to_delete:
                    searched_file_is_deleted = True
                    break
            except OSError  as e:
                logger.error(f"Ошибка при удалении файла {file}: {e}")
                print(f"Ошибка при удалении файла {file}: {e}")

        if search_file_to_delete and not searched_file_is_deleted:
            logger.info(f"Файл для удаления с названием {track_name_to_delete} не найден")
            print(f"Файл для удаления с названием {track_name_to_delete} не найден")
        elif search_file_to_delete and searched_file_is_deleted:
            logger.info(f"Файл с названием {track_name_to_delete} удалён")
            print(f"Файл с названием {track_name_to_delete} удалён")
        else:
            logger.info(f"Директория с установленной музыкой очищена ({self.music_download_path})")
            print(f"Директория с установленной музыкой очищена ({self.music_download_path})")

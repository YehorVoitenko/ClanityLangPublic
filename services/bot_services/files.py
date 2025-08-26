from pathlib import Path

from services.cache_service.cache_service import words_redis_client
from services.cache_service.schemas import WordsCache


def upload_files_to_cache():
    file_names = ["B1 LEVEL WORDS.xlsx", "A2 LEVEL WORDS.xlsx", "HOUSE WORDS.xlsx"]

    for file_name in file_names:
        file_path = Path("constants/files") / file_name
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        match file_name:
            case "B1 LEVEL WORDS.xlsx":
                key = WordsCache.B_LEVEL_WORDS.value
            case "A2 LEVEL WORDS.xlsx":
                key = WordsCache.A_LEVEL_WORDS.value
            case "HOUSE WORDS.xlsx":
                key = WordsCache.SPECIAL_WORDS.value
            case _:
                raise ValueError(f"Неизвестный файл: {file_name}")

        words_redis_client.set(name=key, value=file_bytes)

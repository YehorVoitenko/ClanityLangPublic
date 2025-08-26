import subprocess
import tempfile
import uuid
from contextlib import asynccontextmanager
from html import escape
from pathlib import Path
from subprocess import CalledProcessError, DEVNULL

import deepl
from aiogram.types import FSInputFile
from aiogram.types import Message
from gtts import gTTS

from config.deepl_config import DEEPL_TOKEN


@asynccontextmanager
async def temp_audio_files():
    created = []
    try:
        yield created.append
    finally:
        for p in created:
            try:
                Path(p).unlink(missing_ok=True)
            except Exception:
                pass


def normalize_word_for_pronunciation(word: str) -> str:
    return word.strip().strip("\"'")


def synthesize_tts_to_mp3(text: str, lang: str = "en") -> Path:
    clean = text.strip()
    if not clean:
        raise ValueError("Порожній текст для синтезу.")
    tts = gTTS(text=clean, lang=lang, slow=False)
    tmp_mp3 = Path(tempfile.gettempdir()) / f"tts_{uuid.uuid4().hex}.mp3"
    tts.save(str(tmp_mp3))
    return tmp_mp3


async def synth_and_send_voice(message: Message, text: str):
    if len(text) > 60:
        await message.reply(
            "Будь ласка, надішли коротше слово або фразу (до 60 символів)."
        )
        return

    async with temp_audio_files() as remember:
        try:
            mp3_path = synthesize_tts_to_mp3(text, lang="en")
            remember(mp3_path)
            ogg_path = convert_mp3_to_ogg_opus(mp3_path)
            remember(ogg_path)

            original_text = escape(text)

            translator = deepl.Translator(DEEPL_TOKEN)
            translated = translator.translate_text(text=original_text, target_lang="UK")

            safe_caption = f"🇺🇸 {original_text}\n\n 🇺🇦 {translated}"
            voice_file = FSInputFile(str(ogg_path))
            await message.answer_voice(
                voice=voice_file, caption=safe_caption, disable_notification=True
            )

        except Exception as e:
            err = escape(str(e))
            await message.reply(
                f"Сталася помилка під час синтезу або конвертації: <code>{err}</code>\n"
                f"Переконайся, що ffmpeg встановлено правильно."
            )


def convert_mp3_to_ogg_opus(mp3_path: Path) -> Path:
    ogg_path = mp3_path.with_suffix(".oga")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(mp3_path),
        "-c:a",
        "libopus",
        "-b:a",
        "48k",
        "-vbr",
        "on",
        "-compression_level",
        "10",
        str(ogg_path),
    ]
    try:
        subprocess.run(cmd, check=True, stdout=DEVNULL, stderr=DEVNULL)
    except FileNotFoundError as e:
        raise RuntimeError(
            "Не знайдено ffmpeg. Встановіть ffmpeg і переконайтесь, що він у PATH."
        ) from e
    except CalledProcessError as e:
        raise RuntimeError("Помилка конвертації аудіо у OGG/Opus.") from e

    return ogg_path

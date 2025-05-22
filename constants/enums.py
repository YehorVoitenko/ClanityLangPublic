from enum import Enum


class FileTypes(Enum):
    NEW_FILE = 'NEW_FILE'
    PREVIOUS_FILE = 'PREVIOUS_FILE'


class StateKeys(Enum):
    QUIZ_DATA = 'quiz_data'
    QUIZ_LIMIT = 'quiz_limit'
    FILE_TYPE = 'file_type'
    ROW_INDEX = 'index'
    UPLOADED_FILE_DATA = 'uploaded_file'
    CURRENT_WORD = 'original_word'
    CURRENT_TRANSLATION = 'translation_word'

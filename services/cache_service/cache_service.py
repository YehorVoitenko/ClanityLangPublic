from redis import Redis

from config.background_tasks_config import REDIS_HOST

USER_SUB_CACHE_STORES_IN_SEC = 3600
WORDS_FILE_LIVES_IN_SEC = 86400

cache_user_sub_redis_client = Redis(
    host=REDIS_HOST, port=6379, db=1, decode_responses=True
)

words_redis_client = Redis(host=REDIS_HOST, port=6379, db=2)

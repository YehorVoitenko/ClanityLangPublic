from config.elastic_config import ElasticAvailableIndexes
from services.elastic_service.elastic_service import elastic_client
from services.elastic_service.schemas import CreateUserActivity


class UserActivityProcessor:
    @staticmethod
    def user_tap_start_button(user_id: int):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="SESSION ENTERED", userId=user_id
            ).dict(),
        )

    @staticmethod
    def user_tap_add_file_button(user_id: int):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="TAP ADD FILE", userId=user_id
            ).dict(),
        )

    @staticmethod
    def user_added_file(user_id: int):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="UPLOADED FILE", userId=user_id
            ).dict(),
        )

    @staticmethod
    def user_used_last_file(user_id: int):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="USE LAST FILE", userId=user_id
            ).dict(),
        )

    @staticmethod
    def user_play_a1_a2_level(user_id: int):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="PLAY A1 AND A2 MODE", userId=user_id
            ).dict(),
        )

    @staticmethod
    def user_play_b1_b2_level(user_id: int):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="PLAY B1 AND B2 MODE", userId=user_id
            ).dict(),
        )

    @staticmethod
    def user_play_special_mode(user_id: int, mode_name: str):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="PLAY SPECIAL MODE", userId=user_id, value=mode_name
            ).dict(),
        )

    @staticmethod
    def user_write_correct_word(user_id: int, original_word: str, translated_word: str):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="WRITE CORRECT WORD",
                userId=user_id,
                value=original_word,
                additional_value=translated_word,
            ).dict(),
        )

    @staticmethod
    def user_write_wrong_word(user_id: int, original_word: str, translated_word: str):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="WRITE WRONG WORD",
                userId=user_id,
                value=original_word,
                additional_value=translated_word,
            ).dict(),
        )

    @staticmethod
    def user_answer_time(user_id: int, time_difference: str):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="ANSWER TIME", userId=user_id, value=time_difference
            ).dict(),
        )

    @staticmethod
    def user_used_hint(user_id: int, original_word: str):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="USED HINT", userId=user_id, value=original_word
            ).dict(),
        )

    @staticmethod
    def user_listened_word(user_id: int, original_word: str):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="LISTENED WORD", userId=user_id, value=original_word
            ).dict(),
        )

    @staticmethod
    def user_passed_word(user_id: int, original_word: str):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="PASSED WORD", userId=user_id, value=original_word
            ).dict(),
        )

    @staticmethod
    def user_tap_get_instructions_button(user_id: int):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="GET INSTRUCTIONS",
                userId=user_id,
            ).dict(),
        )

    @staticmethod
    def stopped_quiz(user_id: int):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="STOPPED QUIZ",
                userId=user_id
            ).dict(),
        )

    @staticmethod
    def ask_for_help(user_id: int):
        elastic_client.index(
            index=ElasticAvailableIndexes.USER_ACTIVITY.value,
            document=CreateUserActivity(
                activityId="HELP BUTTON",
                userId=user_id
            ).dict(),
        )

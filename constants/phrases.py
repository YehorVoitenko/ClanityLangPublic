from enum import Enum

MOTIVATION_PHRASES_FOR_MISTAKES = [
    "<b>🌱 Almost there! Every mistake is a step toward mastery.</b>",
    "<b>💡 Don’t worry, you’re learning with every try!</b>",
    "<b>🚧 Mistakes mean you’re pushing boundaries — keep going!</b>",
    "<b>✨ Keep it up! Practice makes perfect, one step at a time.</b>",
    "<b>🔄 Not quite yet, but you’re on the right track!</b>",
    "<b>🌟 Every error is a chance to grow stronger!</b>",
    "<b>🛠️ Keep building those skills — you’re doing great!</b>",
    "<b>🎯 Close! Adjust and try again — you’ve got this!</b>",
    "<b>📈 Progress isn’t always perfect, but it’s progress!</b>",
    "<b>🔥 Don’t give up now, you’re heating up your skills!</b>"
]



SUCCESS_PHRASES = [
    "<b>🎉 Congratulations! You've completed the quiz.</b>",
    "<b>🏆 Well done! You nailed it!</b>",
    "<b>🚀 Great job! You're making awesome progress.</b>",
    "<b>🌟 Fantastic! You’ve mastered this round.</b>",
    "<b>👏 Bravo! You’re on fire!</b>",
    "<b>✅ Success! You’ve finished the quiz like a pro.</b>",
    "<b>🥳 Woohoo! Another step closer to fluency!</b>",
    "<b>🔥 You crushed it! Keep up the momentum.</b>",
    "<b>💪 Impressive! You’re leveling up fast.</b>",
    "<b>📚 Excellent work! Another quiz in the bag.</b>"
]

USER_NOTIFICATIONS = [
    "<b>👋 Hey there! Your English journey is waiting for you at Clanity. Let’s keep going!</b>",
    "<b>📚 Ready to learn some new words today? \nI’m here when you are!</b>",
    "<b>⏳ Haven’t seen you in a while! Your progress is calling—let’s jump back in!</b>",
    "<b>🎯 Your next English challenge is ready. \nLet’s level up together!</b>",
    "<b>🧠 Just a few minutes a day keeps the forgotten words away. \n\nCome back to Clanity!</b>",
    "<b>✨ You’ve made great progress so far. \nLet’s not stop now!</b>",
    "<b>💬 Want to practice a few quick words? I’ve got a quiz ready just for you!</b>",
    "<b>📈 Remember your goals? You're closer than you think. Let’s continue!</b>",
    "<b>🙌 I’m still here, ready to help you grow your English skills. \n\nJoin me anytime!</b>",
    "<b>🚀 Every day you learn a little more. \nLet’s keep the streak going!</b>"
]

SIMPLE_SUB_DESCRIPTION = (
    "<b>SIMPLE subscription level</b>🤩\n\n"
    "This level allows you to <u><b>add your own files (.xlsx)</b></u> with words and <u><b>learn them in quiz mode</b></u>🤩. \n"
    "<i>*with unlimited rounds)</i>\n\n"
    "We can also <u><b>save your favorite file</b></u> to make your learning easier, simpler and more comfortable"

    "<b>Clanity is an easy way to learn new words:\n</b>"
    "<i>- any language you need</i>\n"
    "<i>- everywhere</i>\n"
    "<i>- any time</i>"
)

START_SUB_DESCRIPTION = (
    "<b>START subscription level</b>🚀\n\n"
    "This level includes everything from the <u><b>Simple subscription</b></u>: \n"
    "— the ability to <u><b>add your own files (.xlsx)</b></u> with words\n"
    "— <u><b>learn them in quiz mode</b></u> with <i>unlimited rounds</i> 🤩\n"
    "— <u><b>save your favorite file</b></u> for easier and more comfortable learning\n\n"

    "<b>PLUS ➕</b> you get access to a <u><b>library of 1000+ preloaded A1–A2 level words</b></u>, carefully selected for beginner learners 🌱\n"
    "Start learning immediately – no need to prepare your own wordlists!\n\n"
    "<b>Clanity is an easy way to learn new words:</b>\n"
    "<i>- any language you need</i>\n"
    "<i>- everywhere</i>\n"
    "<i>- any time</i>"
)

PRO_SUB_DESCRIPTION = (
    "<b>PRO subscription level</b>👑\n\n"

    "You get everything from <u><b>Simple</b></u> and <u><b>Start</b></u> subscriptions:\n"
    "— <u><b>add your own files (.xlsx)</b></u> and learn in <b>quiz mode</b> 🤩\n"
    "— <u><b>save your favorite file</b></u> for comfort\n"
    "— access to <u><b>1000+ ready-to-learn words (A1–A2)</b></u> 🌱\n\n"

    "<b>PLUS ULTRA ➕</b> You unlock the full vocabulary power –\n"
    "<u><b>2000+ words</b></u> covering all CEFR levels: <b>B1 → C2</b> 💪\n"
    "Master words for travel, work, study, and fluent daily conversations.\n"
    "<i>No matter your level — you're fully covered.</i>\n\n"
    "<b>Clanity is an easy way to learn new words:</b>\n"
    "<i>- any language you need</i>\n"
    "<i>- everywhere</i>\n"
    "<i>- any time</i>"
)


class InteractivePhrases(Enum):
    WELCOME_MESSAGE = "Welcome! Use to start a vocabulary quiz from an Excel file."
    LOW_SUBSCRIPTION_LEVEL = "Sorry(\n\n<u><b>You subscription is low.</b></u> To use this quiz type you have to buy next level of subscription🙌"
    SUBSCRIPTION_LIST_MESSAGE = "Hi 👋\n \nHere our subscription list. You can tap on each you want and get more information about it.\n"
    SET_LIMIT = "Please enter the number of words you want in the quiz:"
    SUCCESS_SET_LIMIT = "✅ Limit set. Starting the quiz..."
    WRONG_SET_LIMIT = "❌ Please enter a valid number (e.g., 10, 20)."
    ASK_TO_SEND_FILE = "📝 Got it! I’ll quiz you on your words. Now send me the Excel file. \n\n<i>*You can forward already send file from our chat)</i>"
    START_QUIZ = "✅ Loaded {len_of_pairs} words.\n🎯 Quiz length: {limit} rounds\n\n"
    FINISH_QUIZ = "✅ Quiz finished! 🎉"
    START_FIRST_QUIZ_WORD = "✅ Translate this word:\n\n👉 <b>{current_word}</b>"
    CORRECT_USER_WORD = "✅ Correct!\n\nTranslate this word:\nThe next word is 👉 <b>{next_original_word}</b>"
    INCORRECT_USER_WORD = "❌ Incorrect. The correct answer is: <b>{correct_answer}</b>\n\nThe next word is 👉 <b>{next_word}</b>"
    PASSED_USER_WORD = "The correct answer was: <b>{correct_answer}</b>\n\nThe next word is 👉 <b>{next_word}</b>"
    WRONG_FILE_CONTENT_QUANTITY = "⚠️ The file only contains {len_of_pairs} entries, but you requested {limit}.\n I will use the full list instead."
    EMPTY_FILE = "❌ File not found. Please restart the quiz."
    SUCCESS_GET_PREVIOUS_FILE = "✅ Previous file was loaded from server"
    SUCCESS_PURCHASE_PAYMENT = "✅ SUCCESS PURCHASE"
    STOP_QUIZ = "🛑 The quiz was stopped"
    INSTRUCTION = (
        "📖 *How to Use Clanity Bot*\n\n"
        "1️⃣ Send me a `.xlsx` file with word translations.\n"
        "2️⃣ Write translations for quiz words.\n\n"
        "📂 Here's an example file to help you get started 👇"
    )

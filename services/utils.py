def mask_word(word: str) -> str:
    result = ""
    index_in_word = 1

    for char in word:
        if char == " ":
            result += char
            index_in_word = 1
            continue

        result += f"||{char}||" if index_in_word % 2 == 0 else char
        index_in_word += 1

    return result


def escape_markdown_v2(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return "".join("\\" + c if c in escape_chars else c for c in text)

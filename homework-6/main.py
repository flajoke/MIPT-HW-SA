import re
from collections import defaultdict
from typing import Dict, Iterable
import requests

# до улучшения приложения я не смог замерить скорость, мои ноутбук 8гб не выдержал и спустя 10 минут ожидания 
# я просто убил терминал, нынешний вариант отрабатывает примерно за 0.6 - 1 сек.

URL = "https://eng.mipt.ru/why-mipt/"
WORDS_FILE = "words.txt"
TIMEOUT = 10
WORD_RE = re.compile(r"[A-Za-z']+")


def load_target_words(path: str) -> list[str]:
    """Load unique words preserving order from a file."""
    with open(path, "r", encoding="utf-8") as file:
        return list(dict.fromkeys(line.strip().lower() for line in file if line.strip()))


def get_text(url: str) -> str:
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response.text.lower()


def count_word_frequencies(text: str, target_words: Iterable[str]) -> Dict[str, int]:
    targets = set(target_words)
    frequencies: dict[str, int] = defaultdict(int)

    for match in WORD_RE.finditer(text):
        word = match.group(0)
        if word in targets:
            frequencies[word] += 1

    return {word: frequencies.get(word, 0) for word in target_words}


def main() -> None:
    target_words = load_target_words(WORDS_FILE)
    text = get_text(URL)
    frequencies = count_word_frequencies(text, target_words)
    print(frequencies)


if __name__ == "__main__":
    main()

from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR.parent / "datasets" / "text-files"
OUTPUT_DIR = BASE_DIR / "output"

def count_words(text):
    import re
    words = re.findall(r"\b\w+\b", text.lower())
    return Counter(words)

# Expected counts from the original input files
expected = Counter()

for file_path in INPUT_DIR.glob("*.txt"):
    if file_path.name != "expected_word_count.txt":
        expected.update(count_words(file_path.read_text(encoding="utf-8")))

# Counts produced by your MapReduce program
actual = Counter()

for file_path in OUTPUT_DIR.glob("part-*.txt"):
    for line in file_path.read_text(encoding="utf-8").splitlines():
        parts = line.rsplit(maxsplit=1)
        if len(parts) == 2:
            word, count = parts
            actual[word] += int(count)

print("Expected unique words:", len(expected))
print("Actual unique words:", len(actual))

missing = expected.keys() - actual.keys()
extra = actual.keys() - expected.keys()
wrong = {
    word: (expected[word], actual[word])
    for word in expected.keys() & actual.keys()
    if expected[word] != actual[word]
}

print("Missing words:", len(missing))
print("Extra words:", len(extra))
print("Incorrect counts:", len(wrong))

if not missing and not extra and not wrong:
    print("SUCCESS: All word counts match!")
else:
    print("Check the differences above.")
    print("Missing examples:", list(missing)[:10])
    print("Extra examples:", list(extra)[:10])
    print("Incorrect examples:", list(wrong.items())[:10])

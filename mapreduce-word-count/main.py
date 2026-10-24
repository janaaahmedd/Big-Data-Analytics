
import os
import re
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor #to run multiple mapper tasks concurrently using threads.

# Folder containing the five input text files
INPUT_DIR = Path(__file__).resolve().parent.parent / "datasets" / "text-files"

# Folder where the reducer output files will be saved
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

NUM_REDUCERS = 2

#Mapper function
def mapper(file_path):
    """Read a text file and emit (word, 1) pairs."""
    word_counts = []

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read().lower()

    words = re.findall(r"\b[a-zA-Z]+\b", text)

    for word in words:
        word_counts.append((word, 1))

    return word_counts
#Shuffle and Sort function
def shuffle_and_sort(mapper_outputs):
    """Group all values belonging to the same word."""
    grouped_words = defaultdict(list)

    for mapper_output in mapper_outputs:
        for word, count in mapper_output:
            grouped_words[word].append(count)

    return grouped_words
#Reducer
def reducer(grouped_words):
    """Sum the counts for each word."""
    word_counts = {}

    for word, counts in grouped_words.items():
        word_counts[word] = sum(counts)

    return word_counts


def main():
    # Find all input text files
    input_files = sorted(INPUT_DIR.glob("book_*.txt"))

    if not input_files:
        print("No input files found:", INPUT_DIR)
        return

    print(f"Found {len(input_files)} input files.")

    # Run mappers concurrently
    with ThreadPoolExecutor() as executor:
        mapper_outputs = list(
            executor.map(mapper, input_files)
        )

    # Shuffle and sort mapper outputs
    grouped_words = shuffle_and_sort(mapper_outputs)

    # Divide words between two reducers
    reducer_inputs = [defaultdict(list) for _ in range(NUM_REDUCERS)]

    for word, counts in grouped_words.items():
        reducer_id = hash(word) % NUM_REDUCERS
        reducer_inputs[reducer_id][word] = counts

    # Run the reducers concurrently
    with ThreadPoolExecutor(max_workers=NUM_REDUCERS) as executor:
        results = list(
            executor.map(reducer, reducer_inputs)
        )

    # Create the output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save each reducer's results
    for i, result in enumerate(results):
        output_file = OUTPUT_DIR / f"part-{i:02d}.txt"

        with open(output_file, "w", encoding="utf-8") as file:
            for word, count in sorted(result.items()):
                file.write(f"{word}\t{count}\n")

        print(f"Saved: {output_file}")

    print("MapReduce Word Count completed successfully!")


if __name__ == "__main__":
    main()



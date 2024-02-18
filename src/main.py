import os
import time

from indexer import (
    create_schema,
    create_index,
    add_documents_to_index,
    lemmatize_content_in_batches,
)
from retriever.index_searcher import search_index, gpt3_complete, calculate_precision_at_1, calculate_mrr
from parsers import parse_jeopardy_questions
from parsers.wikipedia_parser import parse_wikipedia_file
import json

from retriever.query_builder import preprocess_clue


def index_wiki_data():
    wiki_data_path = "data/wikipedia_data/"
    index_dir = "data/indexdir_with_custom_lemmatization"

    if os.path.exists(index_dir):
        print(f"Index directory '{index_dir}' already exists. Skipping indexing.")
        return

    schema = create_schema()
    indexer = create_index(index_dir, schema)

    start_time = time.time()
    for filename in sorted(os.listdir(wiki_data_path)):
        if filename.endswith(".txt"):
            print(f"Indexing documents from {filename}.")
            articles = parse_wikipedia_file(os.path.join(wiki_data_path, filename))
            start_time_per_file = time.time()
            lemmatized_articles = lemmatize_content_in_batches(articles)
            add_documents_to_index(indexer, lemmatized_articles)
            end_time_per_file = time.time()
            print(
                f"Time taken to add documents from {filename}: {end_time_per_file - start_time_per_file:.2f} seconds."
            )

    end_time = time.time()
    print(f"Indexing completed in {end_time - start_time:.2f} seconds.")


def evaluate_questions(questions, index_dir, results_filename):
    correct_count = 0
    reciprocal_ranks = []
    hits = []

    for question in questions:
        category = question["Category"]
        clue = question["Clue"]
        expected_answer = question["Answer"]

        processed_clue = preprocess_clue(clue)
        search_results = search_index(processed_clue, category, with_rerank=False, index_dir=index_dir)

        # if not search_results:
        #     enhanced_query = gpt3_complete(clue, category)
        #     print(f"Enhanced Query for '{clue}': {enhanced_query}")  # Log to console
        #     search_results = search_index(enhanced_query, category, index_dir)

        is_correct = expected_answer in search_results
        hits.append(
            {"Clue": clue, "Search Results": search_results, "Is Correct": is_correct}
        )

        # Compute Precision@1 and MRR
        correct_count += calculate_precision_at_1(search_results, expected_answer)
        reciprocal_ranks.append(calculate_mrr(search_results, expected_answer))

    p_at_1 = correct_count / len(questions) if questions else 0
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0

    write_results_to_file(results_filename, questions, hits)

    return p_at_1, mrr


def write_results_to_file(filename, questions, hits):
    with open(filename, "w") as file:
        for question, hit in zip(questions, hits):
            file.write(
                json.dumps(
                    {
                        "Category": question["Category"],
                        "Clue": question["Clue"],
                        "Expected Answer": question["Answer"],
                        "Search Results": hit["Search Results"],
                        "Is Correct": hit["Is Correct"],
                    },
                    indent=4,
                )
                + "\n\n"
            )


def main():
    # index_wiki_data()
    jeopardy_questions_path = "data/jeopardy/questions.txt"
    index_dir = "data/indxdir"

    results_filename = "search_results.txt"

    questions = parse_jeopardy_questions(jeopardy_questions_path)
    p_at_1, mrr = evaluate_questions(questions, index_dir, results_filename)

    print(f"Precision at 1: {p_at_1:.4f}")
    print(f"Mean Reciprocal Rank: {mrr:.4f}")


def main_manually():
    # index_wiki_data()

    print("Enter a clue:")
    clue = input()
    print("Enter a category:")
    category = input()

    search_query = preprocess_clue(clue)
    print("preprocessed query:")
    print(search_query)

    top_result = search_index(
        search_query, category, with_rerank=False, index_dir="data/indexdir_with_custom_lemmatization"
    )
    print(top_result)


if __name__ == "__main__":
    main()
    # main_manually()

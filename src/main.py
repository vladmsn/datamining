import os
import time

from indexer import create_schema, create_index, add_documents_to_index
from retriever.query_retriever import build_query_from_clue, build_boolean_query_from_clue
from parsers import parse_jeopardy_questions
from parsers.wikipedia_parser import parse_wikipedia_file
from whoosh.qparser import QueryParser
from whoosh.index import open_dir


def index_wiki_data():
    wiki_data_path = "data/wikipedia_data/"
    index_dir = "data/indexdir_with_simple_analzyer"

    schema = create_schema()
    indexer = create_index(index_dir, schema)

    start_time = time.time()
    for filename in os.listdir(wiki_data_path):
        if filename.endswith(".txt"):
            articles = parse_wikipedia_file(os.path.join(wiki_data_path, filename))
            add_documents_to_index(indexer, articles)

    end_time = time.time()
    print(f"Indexing completed in {end_time - start_time:.2f} seconds.")



def search_index_for_top_result(index_dir, search_query):
    ix = open_dir(index_dir)
    parser = QueryParser("content", schema=ix.schema)

    query = parser.parse(search_query)
    with ix.searcher() as searcher:
        results = searcher.search(query)
        if results:
            return results[0]["title"]
        else:
            return None


def evaluate_questions(questions, index_dir, results_filename):
    correct_count = 0
    reciprocal_ranks = []
    hits = []

    for question in questions:
        category = question["Category"]
        clue = question["Clue"]
        expected_answer = question["Answer"]

        search_query = build_query_from_clue(clue)
        top_result = search_index_for_top_result(index_dir, search_query)

        is_correct = top_result and expected_answer.lower() in top_result.lower()
        hits.append({"Clue": clue, "Top Result": top_result, "Is Correct": is_correct})

        if is_correct:
            correct_count += 1
            reciprocal_ranks.append(1.0)
        else:
            reciprocal_ranks.append(0)

    p_at_1 = correct_count / len(questions)
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)

    write_results_to_file(results_filename, questions, hits)

    return p_at_1, mrr


def write_results_to_file(filename, questions, hits):
    with open(filename, 'w') as file:
        for question, hit in zip(questions, hits):
            file.write(f"Category: {question['Category']}\n")
            file.write(f"Clue: {question['Clue']}\n")
            file.write(f"Query: {build_query_from_clue(question['Clue'])}\n")
            file.write(f"Expected Answer: {question['Answer']}\n")
            file.write(f"Top Search Result: {hit['Top Result']}\n")
            file.write(f"Hit: {'Yes' if hit['Is Correct'] else 'No'}\n")
            file.write("-------------------------------------------------\n")


def main():
    # index_wiki_data()
    jeopardy_questions_path = "data/jeopardy/questions.txt"
    index_dir = "data/indexdir_with_simple_analzyer"

    results_filename = "search_results.txt"

    questions = parse_jeopardy_questions(jeopardy_questions_path)
    p_at_1, mrr = evaluate_questions(questions, index_dir, results_filename)

    print(f"Precision at 1: {p_at_1:.4f}")
    print(f"Mean Reciprocal Rank: {mrr:.4f}")

    # p_at_1, mrr = evaluate_questions(questions, index_dir, "boolean_" + results_filename, use_custom_query="boolean")
    # print(f"Precision at 1 (boolean): {p_at_1:.4f}")
    # print(f"Mean Reciprocal Rank (boolean): {mrr:.4f}")

    # p_at_1, mrr = evaluate_questions(questions, index_dir, "nlp_" + results_filename, use_custom_query="nlp")
    # print(f"Precision at 1 (nlp): {p_at_1:.4f}")
    # print(f"Mean Reciprocal Rank (nlp): {mrr:.4f}")


def main_manually():
    index_wiki_data()
    #
    # print("Enter a clue:")
    # clue = input()
    # print("Enter a category:")
    # category = input()
    #
    # search_query = build_query_from_clue(clue)
    # print("nlp query:")
    # print(search_query)
    #
    # top_result = search_index_for_top_result(index_dir, search_query)
    # print(top_result)


if __name__ == "__main__":
    main()
    # main_manually()

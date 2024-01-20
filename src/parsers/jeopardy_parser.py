def parse_jeopardy_questions(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    questions = []
    for i in range(0, len(lines), 4):
        category = lines[i].strip()
        clue = lines[i + 1].strip()
        answer = lines[i + 2].strip()
        questions.append({"Category": category, "Clue": clue, "Answer": answer})

    return questions

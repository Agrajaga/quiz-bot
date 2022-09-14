import re


def get_quiz(filename: str) -> dict:
    with open(filename, "r", encoding="KOI8-R") as quiz_file:
        file_contents = quiz_file.read()

    questions = []
    for question_text in file_contents.split("\n\n\n"):
        for fragment in question_text.split("\n\n"):
            fragment = fragment.replace("\n", " ")
            if fragment[:6].lower() == "вопрос":
                question = re.sub("^Вопрос \d+:", "", fragment).strip()
            if fragment[:5].lower() == "ответ":
                answer = re.sub("^Ответ:", "", fragment).strip()
                answer = re.split("\.|\(", answer)[0]
        questions.append(
            {
                'question': question,
                'answer': answer,
            }
        )
    return questions


if __name__ == "__main__":
    quiz = get_quiz("questions/1vs1201.txt")
    print(quiz)

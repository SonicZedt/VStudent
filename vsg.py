import answer
import vclass
import configparser
import tkinter
from log import debug
from tkinter import filedialog

def input_valid_url(message:str, requirement:tuple):
    """ Make sure given input contain all requirements """
    while True:
        url = input(message)
        if url.lower() in ('N', 'n'):
            exit()
        elif not all([req in url for req in requirement]):
            print("Invalid URL!, enter [N/n] to exit: ")
            continue
        elif url:
            return url

def get_answer_doc_path(ext:str='.docx') -> str:
    """ Get answered documen path """
    while True:
        print("Select answered quiz document")
        path = filedialog.askopenfilename(title='Select answered quiz document')
        if path.endswith(ext):
            return path
        elif not path:
            exit()
        
        while True:
            choice = input("Invalid document type. Enter [Y/y] to select another document or [N/n] to exit: ").lower()
            if choice == 'y':
                break
            elif choice == 'n':
                exit()

def answer_quiz(quiz:vclass.Quiz, count:int, ansdoc:answer.DOCX):
    debug.log(f"total question: {count}", newline=True)
    answered_count = 0
    next_question_available = quiz.next_question(check=True)

    for _ in range(1, count+1):
        question = quiz.get_current_question()       

        # get answer from defined list of dict
        debug.log("Chceking answer ...", newline=True)
        for qna in ansdoc.QnA:
            if qna['question'] != question:
                continue
            if not qna['answer']:
                continue
            ans = qna['answer']

        # answer the question
        answered = quiz.answer_current_question(question, ans)

        if answered:
            answered_count = answered_count + 1
        if not next_question_available:
            break
        next_question_available = quiz.next_question()

    debug.log(f"Answered {answered_count} out of {count}", newline=True)

def main(config_path:str='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_path)

    # prevents an empty tkinter window from appearing
    tkinter.Tk().withdraw()
    #ansdoc = answer.DOCX(get_answer_doc_path())
    ansdoc = answer.TXT(get_answer_doc_path(ext='.txt'))

    quiz_url = input_valid_url(
        message="Quiz URL: ",
        requirement=('quiz', 'id='))

    vstudent = vclass.VStudent(config)
    vstudent.login()

    quiz = vclass.Quiz(vstudent.active_browser, quiz_url)
    question_count = quiz.attempt()

    answer_quiz(quiz, question_count, ansdoc)

if __name__ == "__main__":
    main()
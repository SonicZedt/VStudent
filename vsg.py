import time
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

def get_answer_doc_path(accepted_ext:list[str]=['.docx', '.txt']) -> str:
    """ Get answered documen path """
    while True:
        print("Select answered quiz document")
        path = filedialog.askopenfilename(title='Select answered quiz document')
        if [True for ext in accepted_ext if path.endswith(ext)]:
            return path
        elif not path:
            exit()
        
        while True:
            choice = input("Invalid document type. Enter [Y/y] to select another document or [N/n] to exit: ").lower()
            if choice == 'y':
                break
            elif choice == 'n':
                exit()

def answer_quiz(quiz:vclass.Quiz, count:int, qna:answer.QnA, delay=2) -> int:
    """ Answer quiz 
    return: answered question count """
    debug.log(f"total question: {count}", newline=True)
    answered_count = 0
    next_question_available = quiz.next_question(check=True)

    for _ in range(1, count+1):
        time.sleep(delay)
        question = quiz.get_current_question()       
        ans = qna.get_answer(question)

        # answer if answer exist
        if ans:
            answered = quiz.answer_current_question(question, ans)
            if answered:
                answered_count = answered_count + 1
        if not next_question_available:
            break
        next_question_available = quiz.next_question()

    debug.log(f"Answered {answered_count} out of {count}", newline=True)
    return answered_count

def main(config_path:str='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_path)

    # prevents an empty tkinter window from appearing
    tkinter.Tk().withdraw()
    ansdoc = answer.define_doc(get_answer_doc_path())
    if not ansdoc.confirm():
        print("Failed to extract question and answer from given document")
        exit()

    # verify quiz url
    quiz_url = input_valid_url(
        message="Quiz URL: ",
        requirement=('quiz', 'id='))

    # login to vclass
    vstudent = vclass.VStudent(config)
    vstudent.login()

    # go to quiz page and attempt quiz
    quiz = vclass.Quiz(vstudent.active_browser, quiz_url)
    question_count = quiz.attempt()

    # answer quiz
    answered_count = answer_quiz(
        quiz=quiz,
        count=question_count,
        qna=ansdoc.qna,
        delay=config.getint('vclass', 'answer_delay'))
    ask_submit_quiz_confirmation = config['vclass'].getboolean('submit_quiz_confirmation')
    if (answered_count == question_count):
        if quiz.ask_submit_quiz_confirmation(ask_submit_quiz_confirmation):
            quiz.submit()

if __name__ == "__main__":
    main()
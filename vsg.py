import answer
import vclass
import configparser
import tkinter
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

def get_answer_doc_path() -> str:
    """ Get answered documen (.docx) path """
    while True:
        print("Select answered quiz document (.docx)")
        path = filedialog.askopenfilename(title='Select answered quiz document')
        if path.endswith('.docx'):
            return path
        elif not path:
            exit()
        
        while True:
            choice = input("Only documents from Word that can be processed at this time. Enter [Y/y] to select another document or [N/n] to exit: ").lower()
            if choice == 'y':
                continue
            elif choice == 'n':
                exit()

def main(config_path:str='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_path)

    # prevents an empty tkinter window from appearing
    tkinter.Tk().withdraw()
    ansdoc = answer.DOCX(get_answer_doc_path())

    quiz_url = input_valid_url(
        message="Quiz URL: ",
        requirement=('quiz', 'id='))

    vstudent = vclass.VStudent(config)
    vstudent.login()

    quiz = vclass.Quiz(vstudent.active_browser, quiz_url)

if __name__ == "__main__":
    main()
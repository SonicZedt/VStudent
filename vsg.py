import vclass
import anskey
import configparser

def input_valid_url(message:str, requirement:tuple):
    """ Make sure given input contain all requirements """
    while True:
        url = input(message)
        if url.lower() in ('N', 'n'):
            exit()
        elif not all([req in url for req in requirement]):
            print("Invalid URL!, enter [N/n] to exit")
            continue
        elif url:
            return url

def main(config_path:str='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_path)

    quiz_url = input_valid_url(
        message="Quiz URL: ",
        requirement=('quiz', 'id='))

    vstudent = vclass.VStudent(config)
    vstudent.login()

    quiz = vclass.Quiz(vstudent.active_browser, quiz_url)

def ondev():
    path = 'doc/anskey1.docx'
    ansdoc = anskey.AnswerDOCX(path)
    for qna in ansdoc.QnA:
        print(qna['question'])
        print(qna['answer'], '\n')

if __name__ == "__main__":
    main()
    #ondev()
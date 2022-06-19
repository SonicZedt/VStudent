import vclass
import anskey
import configparser

def input_valid_url(message:str, requirement:tuple):
    """ Make sure given input contain all requirements """
    while True:
        url = input(message)
        if not all([req in url for req in requirement]):
            print("Invalid URL!, enter [N/n] to exit")
            continue
        elif url.lower() in ('N', 'n'):
            exit()
        elif url:
            return url

def main(config_path:str='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_path)

    assign_url = input_valid_url("Assignment URL: ", ('/', 'assign'))

    vstudent = vclass.VStudent(config)
    vstudent.login()

    assign = vclass.Assignment(vstudent.active_browser, assign_url)

def ondev():
    path = 'doc/anskey1.docx'
    ansdoc = anskey.AnswerDOCX(path)
    for qna in ansdoc.QnA:
        print(qna['question'])
        print(qna['answer'], '\n')

if __name__ == "__main__":
    #main()
    ondev()
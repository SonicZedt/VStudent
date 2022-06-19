import docx
from docx.document import Document
from docx.text.paragraph import Paragraph

class AnswerDOCX:
    def __init__(self, path:str):
        self.path = path
        self.doc = self.__redefine_doc(docx.Document(path))
        self.QnA = self.__define_QnA()

    def __redefine_doc(self, doc:Document):
        """ Somehow fixed auto-complete problem """
        return doc

    def __define_QnA(self) -> list[dict]:
        """ Define list of question and it's answer """
        QnA_list = []

        def get_answer(choices:list[Paragraph], type:int, debug_choices:bool=False) -> Paragraph:
            """ Get the answer from the choices 
            :params: choices: a list of answer choice
            :type: Either (0) unique style, (1)___, (2)___"""

            # 1. Unique style. an answer could be use Heading 1 as style while the others is not
            # the answer is must be the one that is different from the others
            # return a Paragraph with unique style
            if debug_choices:
                print("=========")
                for c in choices:
                    print(c.text)

            if type == 0:
                answer_style = [answer.style for answer in choices]
                style_freq = [answer_style.count(style) for style in answer_style]
                return choices[style_freq.index(min(style_freq))]

        # remove empty paragraph
        paragraphs = [paragraph for paragraph in self.doc.paragraphs if paragraph.runs]

        for i, paragraph in enumerate(paragraphs):
            QnA = {
                'question' : '',
                'answer' : ''
            }

            # define QnA by using "Select one:" as keyword
            keyword = "Select one:"
            if keyword not in paragraph.text:
                continue

            # a question must be right before keyword or in same paragraph as keyword
            if paragraph.text == keyword:
                QnA['question'] = paragraphs[i-1].text
            else:
                QnA['question'] = paragraphs[i].text.split(keyword)[0].strip()

            # the four choices of answer must be right after keyword
            answer_choices = paragraphs[i+1:i+5]
            QnA['answer'] = get_answer(answer_choices, type=0).text

            QnA_list.append(QnA)
        
        return QnA_list
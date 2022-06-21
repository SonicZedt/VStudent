import docx
from docx.document import Document
from docx.text.paragraph import Paragraph

class DOCX:
    def __init__(self, path:str):
        """ The answer document

        Parameter
        ---------
        path    : str,
            path to document.docx """
        self.path = path
        self.doc = self.__redefine_doc(docx.Document(path))
        self.__remove_textboxt()
        self.QnA = self.__define_QnA()

    def __redefine_doc(self, doc:Document):
        """ Somehow fixed auto-complete problem """
        return doc

    def __remove_textboxt(self):
        # FIXME: can not read paragraph if it inside a textbox
        """ Extract paragraph from it's textbox """
        return 0

    def __define_QnA(self) -> list[dict]:
        """ Define list of question and it's answer """
        QnA_list = []

        def get_ansdoc_type(choices:list[Paragraph]) -> int:  
            """
            return
            ----------
            0 if it is not-answered question
            1 if choices has two different style 
            2 if choices has from review page """

            answer_style = [answer.style for answer in choices]
            style_freq = set([answer_style.count(style) for style in answer_style])
            if len(style_freq) == 1:
                #if from_review_page:
                #    return 2
                #else:
                #    return 0
                return 0
            elif len(style_freq) == 2:
                return 1  

        def get_answer(choices:list[Paragraph], debug_choices:bool=False) -> str:
            if debug_choices:
                print("=========")
                for c in choices:
                    print(c.text)

            ansdoc_type = get_ansdoc_type(choices)
            if ansdoc_type == 0:
                # type 0 is choices with no answer
                return ''
            elif ansdoc_type == 1:
                # type 1 answer is a Paragraph with unique style
                answer_style = [answer.style for answer in choices]
                style_freq = [answer_style.count(style) for style in answer_style]
                return choices[style_freq.index(min(style_freq))].text

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

            # the four choices of answer must be right after keyword
            answer_choices = paragraphs[i+1:i+5]
            if not answer_choices:
                continue

            QnA['answer'] = get_answer(answer_choices)

            # a question must be right before keyword or in same paragraph as keyword
            if paragraph.text == keyword:
                QnA['question'] = paragraphs[i-1].text
            elif keyword in paragraph.text:
                QnA['question'] = paragraphs[i].text.split(keyword)[0].strip()

            QnA_list.append(QnA)
        
        return QnA_list
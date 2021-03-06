import app
import docx
import numpy as np
from log import debug
from figure import RadioButton
from docx.document import Document
from docx.text.paragraph import Paragraph
from pdfminer.layout import LAParams, LTTextBox, LTFigure, LTImage
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdftypes import PDFObjRef
from pdfminer.psparser import PSLiteral

def define_doc(path:str):
    ext = path.split('.')[-1].lower()
    if ext == 'docx':
        return DOCX(path)
    elif ext == 'txt':
        return TXT(path)
    elif ext == 'pdf':
        return PDF(path)

class QnA:
    def __init__(self, qna:list=[]):
        """ QnA is a list of dict contains question and answer """
        self.qna = qna

    @property
    def count(self) -> int:
        return len(self.qna)

    def confirm(self) -> bool:
        """ Confirm question and answer count """
        print(f"Question and Answer count from answer document: {self.count}")
        return self.count > 0

    def append(self, dict:dict):
        self.qna.append(dict)

    def get_answer(self, question:str):
        for qna in self.qna:
            if qna['question'] == question:
                return qna['answer']

    def remove_unanswered(self):
        """ Remove unanswered question """
        self.qna = [qna for qna in self.qna if qna['answer']]

    def print(self):
        """ Print all question and answer """
        self.confirm()
        for qna in self.qna:
            print(qna)

class PDF:
    # qna: QnA class
    # QnA: variabel inside this class

    def __init__(self, path:str, verbose:int=1):
        self.path = path
        self._file = open(path, 'rb')
        resource_manager = PDFResourceManager()
        laparams = LAParams()
        aggregator = PDFPageAggregator(resource_manager, laparams=laparams)
        interpreter = PDFPageInterpreter(resource_manager, aggregator)
        self.pages = PDFPage.get_pages(self._file)

        # get paragraph and image coordinates
        self.text_coorinates = []
        self.figure_coorinates = []

        debug.log("Extracting text and images ...", verbose, newline=True)
        for page in self.pages:
            interpreter.process_page(page)
            layout = aggregator.get_result()
            for layout_object in layout:
                # get paragraph coordinates
                if isinstance(layout_object, LTTextBox):
                    self.text_coorinates.append({
                        'paragraph': layout_object.get_text().replace('\n', '').strip(),
                        'x': layout_object.bbox[0],
                        'y': layout_object.bbox[3]
                    })

                # get image coordinates
                if isinstance(layout_object, LTFigure):
                    for img in layout_object:
                        if not isinstance(img, LTImage):
                            # not an image
                            continue

                        if img.stream.attrs['Filter'].name == 'DCTDecode':
                            # JPEG
                            continue

                        try:
                            imgdata = img.stream.get_data()
                        except:
                            imgdata = img.stream.get_rawdata()
                        if not imgdata:
                            continue
                        
                        # convert imgdata from bytes to 3d np.array
                        colorspace = img.stream.attrs['ColorSpace']
                        w = img.stream.attrs['Width']
                        h = img.stream.attrs['Height']
                        c = 3 if (type(colorspace) == PSLiteral) and (colorspace.name == 'DeviceRGB') else 1
                            #c = 3 if img.stream.attrs['ColorSpace'].name == 'DeviceRGB' else 1

                        imgdata = np.frombuffer(imgdata, dtype=np.uint8)
                        imgdata = imgdata.reshape(h, w, c)

                        # skip average blank image
                        if np.average(imgdata) == 0:
                            continue

                        self.figure_coorinates.append({
                            'image_data' : imgdata,
                            'x' : layout_object.bbox[0],
                            'y' : layout_object.bbox[1]
                        })

        debug.log(
            f"Extracted {len(self.text_coorinates)} text and {len(self.images)} images",
            verbose)

        self.paragraphs = self.__clean_up_paragraph(['Question', 'Mark'])
        self.buttons = self.__define_button()

        if not self.__confirm_button():
            debug.log("No radio button found and unable to extract answer")
            app.exit_app()

        self.QnA = self.__define_QnA()

    @property
    def paragraphs_raw(self) -> list[str]:
        """ Get all paragraphs """
        return [paragraph['paragraph'] for paragraph in self.text_coorinates]

    @property
    def images(self) -> list[np.ndarray]:
        """ Raw images """
        return [image['image_data'] for image in self.figure_coorinates]

    @property
    def qna(self) -> QnA:
        return self.QnA

    def __clean_up_paragraph(self, keywords:list[str]):
        """ Remove paragraph contains keywords """
        paragraphs = self.paragraphs_raw
        for paragraph in paragraphs:
            for keyword in keywords:
                if keyword in paragraph:
                    paragraphs.remove(paragraph)
                    break
        return paragraphs

    def __define_button(self) -> list[RadioButton]:
        """ Define radio button from images """
        buttons = []
        for image in self.images:
            button = RadioButton(image)
            button.brighten_color()
            buttons.append(button)
        return buttons

    def __confirm_button(self) -> bool:
        """ Confirm radio button count """
        return len(self.buttons) > 0

    def __define_QnA(self) -> QnA:
        qna = QnA()
        keyword = "Select one:"

        def get_question(paragraph:str, keyword:str='Select one:') -> str:
            # a question must be right before keyword or in same paragraph as keyword
            if paragraph == keyword:
                question = self.paragraphs[i-1]
            elif keyword in paragraph:
                question = self.paragraphs[i].split(keyword)[0].strip()
            return question

        def get_answer(choices:list[str], buttons:list[RadioButton]) -> str:
            """ Get answer based on it's radio button
            params: list[str], choices, answer choices
            params: list[RadioButton], button, radio button corresponding to each answer """
            for i, answer in enumerate(choices):
                answer = answer.split(' ', 1)[-1].strip()
                if buttons and buttons[i].is_selected:
                    return answer
            return ''

        button_idx = 0
        for i, paragraph in enumerate(self.paragraphs):
            if keyword not in paragraph:
                continue

            correct_answer_available = False
            correct_answer_keyword = 'The correct answer is: '
            try:
                # possible correct answer confirmed (type 2)
                correct_answer = self.paragraphs[i+6]
                if correct_answer_keyword in correct_answer:
                    question = get_question(paragraph)
                    correct_answer = correct_answer.split(correct_answer_keyword)[1].strip()
                    qna.append({'question': question, 'answer': correct_answer})
                    correct_answer_available = True
                    continue
            except:
                pass

            answer_choices = self.paragraphs[i+2:i+6]
            if not answer_choices and not correct_answer_available:
                continue
            buttons_choices = self.buttons[button_idx:button_idx+4]
            button_idx += 4

            question = get_question(paragraph)
            answer = get_answer(answer_choices, buttons_choices)

            qna.append({
                'question': question,
                'answer': answer
            })

        qna.remove_unanswered()
        return qna

    def confirm_radio_button(self, minimum:int=1) -> bool:
        """ Confirm radio button of answer document
        params: int, minimum number of radio button
        return: True if radio button count is more than minimum """
        if len(self.images) < minimum:
            return False
        return True

    def confirm(self) -> bool:
        """ Confirm answer document 
        return: True if QnA is usable """
        print(f"Answer document path: {self.path}")
        return self.QnA.confirm()

class DOCX:
    # qna: QnA class
    # QnA: variabel inside this class

    def __init__(self, path:str):
        """ The answer document

        Parameter
        ---------
        path    : str,
            path to document.docx """
        self.path = path
        self.doc = self.__redefine_doc(docx.Document(path))
        self.__paragraphs_clean = self.__remove_empty_paragraph()
        #self.__remove_textboxt()
        self.QnA = self.__define_QnA()

    @property
    def ext(self) -> str:
        """ return file extension """
        return self.path.split('.')[-1]

    @property
    def qna(self) -> QnA:
        return self.QnA

    def __redefine_doc(self, doc:Document):
        """ Somehow fixed auto-complete problem """
        return doc

    def __remove_empty_paragraph(self):
        return [paragraph for paragraph in self.doc.paragraphs if paragraph.runs]

    def __remove_textboxt(self):
        # FIXME: can not read paragraph if it inside a textbox
        """ Extract paragraph from it's textbox """
        return 0

    @property
    def from_review_page(self) -> bool:
        """ Check if document is from review page or not """
        # if a document is from review page, it will have a 'State' and 'Finished' runs
        state_paragraph = self.__paragraphs_clean[2]
        return ('State' in state_paragraph.runs[0].text) and (state_paragraph.runs[1].text == 'Finished')

    def __define_QnA(self) -> QnA:
        """ Define list of question and it's answer """
        qna = QnA()

        def get_answer_type(choices:list[Paragraph]) -> int:  
            """
            return: int\n
            0 - not-answered question\n
            1 - choices has two different paragraph styles\n
            2 - choices are from review page """

            # check answer paragraph style
            answer_style = [answer.style for answer in choices]
            style_freq = set([answer_style.count(style) for style in answer_style])

            # all answers paragraph style is same
            if len(style_freq) == 1:
                #if from_review_page:
                #    return 2
                #else:
                #    return 0
                return 0
            elif len(style_freq) == 2:
                return 1  

        def get_question(paragraph:Paragraph, keyword:str='Select one:') -> str:
            # a question must be right before keyword or in same paragraph as keyword
            if paragraph.text == keyword:
                question = paragraphs[i-1].text
            elif keyword in paragraph.text:
                question = paragraphs[i].text.split(keyword)[0].strip()
            return question

        def get_answer(choices:list[Paragraph], debug_choices:bool=False) -> str:
            """ Get unique paragraph as an answer """
            if debug_choices:
                print("=========")
                for c in choices:
                    print(c.text)

            answer_type = get_answer_type(choices)
            if answer_type == 0:
                # type 0 is choices with no answer
                return ''
            elif answer_type == 1:
                # type 1 answer is a Paragraph with unique style
                answer_style = [answer.style for answer in choices]
                style_freq = [answer_style.count(style) for style in answer_style]
                return choices[style_freq.index(min(style_freq))].text

            # TODO: get answer based on unique radio buttons (type 2)
            # radio button is a image
            # there should be:
            ## - 4*n radio button (n is number of question) in a page
            ##   one of them could will be selected as an answer and returned
            ## - possibility of a checklist or cross mark next to an answer
            ##   (this will called correction)
            ## - radio button, checklist, and cross mark is an image 

        # remove empty paragraph
        paragraphs = self.__paragraphs_clean
        keyword = "Select one:"

        for i, paragraph in enumerate(paragraphs):
            # define QnA by using "Select one:" as keyword
            if keyword not in paragraph.text:
                continue

            correct_answer_available = False
            correct_answer_keyword = 'The correct answer is: '
            try:
                # possible correct answer confirmed (type 2)
                correct_answer = paragraphs[i+5].text
                if correct_answer_keyword in correct_answer:
                    question = get_question(paragraph)
                    correct_answer = correct_answer.split(correct_answer_keyword)[1]
                    qna.append({'question': question, 'answer': correct_answer})
                    correct_answer_available = True
                    continue
            except:
                pass

            # the four choices of answer must be right after keyword (type 1)
            answer_choices = paragraphs[i+1:i+5]
            if not answer_choices and not correct_answer_available:
                continue

            question = get_question(paragraph)
            answer = get_answer(answer_choices)

            qna.append({'question': question, 'answer': answer})
        
        qna.remove_unanswered()
        return qna

    def confirm(self) -> bool:
        """ Confirm answer document 
        return: True if QnA is usable """
        print(f"Answer document path: {self.path}")
        return self.QnA.confirm()

class TXT:
    # qna: QnA class
    # QnA: variabel inside this class

    def __init__(self, path:str):
        """ The answer document in TXT

        Parameter
        ---------
        path    : str, path to document.txt """
        self.path = path
        QnA_list = self.__open_txt_files()
        QnA_list = self.__clean_up(['Select one', 'Question'], QnA_list)
        self.QnA = self.__define_QnA(QnA_list)
    
    @property
    def ext(self) -> str:
        """ return file extension """
        return self.path.split('.')[-1]

    @property
    def qna(self) -> QnA:
        return self.QnA

    @property
    def from_review_page(self) -> bool:
        return False

    def __open_txt_files(self) -> list[str]:
        """ Open txt file and return list of lines """
        with open(self.path, 'r') as f:
            lines = f.readlines()
            lines.append('\n')
            return lines
        
    def __clean_up(self, keywords:list, QnA:list) -> list[str]:
        """ Remove lines that are contains keywords """
        for line in QnA:
            for keyword in keywords:
                if keyword in line:
                    QnA.remove(line)
    
        return QnA

    def __define_QnA(self, QnA_list) -> QnA:
        qna = QnA()

        for i, line in enumerate(QnA_list):
            if line != '\n':
                continue

            question = QnA_list[i-2]
            answer = QnA_list[i-1]

            if '\n' in question:
                question = question.split('\n')[0]
            if '\n' in answer:
                answer = answer.split('\n')[0]
            
            qna.append({'question':question, 'answer':answer})

        qna.remove_unanswered()
        return qna

    def confirm(self) -> bool:
        """ Confirm answer document
        return: True if QnA is usable """
        print(f"Answer document path: {self.path}")
        return self.QnA.confirm()

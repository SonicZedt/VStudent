# VStudent
A BOT to answer multiple choice quiz in moodle platform such as [vclass](https://v-class.gunadarma.ac.id).

## What VStudent needs
* Internet connection to access vclass platform
* An answer document (.docx or .txt) in certain format to answer the quiz. Read [Answer document format](#answer-document-format) for more information.
* An URL to the quiz in vclass platform

## Answer document format
The answer document should be in .docx, .txt, or .pdf.
### .DOCX
There are two types of .docx document that are currently readable by the BOT, type 1 and type 2.
* Type 1 will scan for unique paragraph style uses by answer choices to determine the answer from the other answer choices.
* Type 2 will scan for string `"The correct answer is:"` occurrences to determine the answer.

> Download format: [answer_type1.docx](https://docs.google.com/document/d/1-GwvMs6aSkNMY6Z2COR7HGlMhGBZqU2j/edit?usp=sharing&ouid=106238154602768730311&rtpof=true&sd=true) or [answer_type2.docx](https://docs.google.com/document/d/120Jpxo3lEEIkZEN2SIiSlxXh1xxdYgnb/edit?usp=sharing&ouid=106238154602768730311&rtpof=true&sd=true)

### .TXT
A .txt document is currently the best and ~~safest~~ readable format for the BOT. The format should be a question, followed by the answer on the next line, and followed by blank line on the next line.
> Download format: [answer.txt](https://drive.google.com/file/d/1mC8Qsa6CcodoxLC1RIfUmcUC2B7HLEN8/view?usp=sharing)

### .PDF
An exported pdf document from review page is preferable.
#### Work principle of .PDF
1. The BOT will extract all text and images from the pdf document along with their coordinates.
2. Extracted images are images of button (radio button) used to select the answer.
3. If an image has more white pixels than specified threshold, it will be considered as an answer.
4. A paragraph from extracted text will be deleted if it contains `"Question"` and `"Mark"` because of these strings are not needed and could mess up with paragraph order.
5. The BOT will scan for string `"The correct answer is:"` occurrences to determine the answer if available. If not, continue to next step.
6. The BOT will scan for string `"Select one:"` occurrences to determine the question and answer choices. The question paragraph would be right before this string `[i-1]` or right with it `[i]` and the four of answer choices would be on the next two to five paragraphs `[i+2:i+6]`.
7. The set of answer choices will be paired with the button images. The answer is determined by how many white pixel is in the button image.

#### Possible issue with .PDF
Any differences in visual arrangement in a PDF document could cause the BOT to fail to do extraction process.

---
## Setup
* Download latest version of VStudent [here](https://github.com/SonicZedt/VStudent/releases)
* Extract
* Open and edit `config.ini` file using any text editor, enter your vclass _username_ and _password_ under login section.

## Configuration
Configration is done in `config.ini` file.

| Section | Key | Type | Description  |
| ------- | --- | ---- | ------ |
| login   | username | str | your vclass username |
| login   | password | str | your vclass password |
| vclass  | login_confirmation | bool | ask for confirmation before login to vclass platform |
| vclass  | submit_quiz_confirmation | bool | ask for confirmation before submitting in last question page |
| vclass  | submit_summary_confirmation | bool | ask for confirmation before submitting in summary page |
| vclass  | answer_delay | int | delay in seconds before moving to the next question |

## Usage
1. Launch BOT executable file (vsg.exe)
2. A file explorer will appear, select the answer document.
3. Paste quiz URL. the URL should be looks like https://v-class.gunadarma.ac.id/mod/quiz/view.php?id=XXXXXX where XXXXXX is the quiz ID.
4. A Firefox webdriver will be opened, and the BOT will attempt to login to vclass using given username and password in `config.ini`.
5. BOT will ask login confirmation if `login_confirmation` is set to `True` in `config.ini` file, otherwise it will automatically login.
6. BOT will go to the quiz page using the given URL and attempt or continue the quiz.
7. After reaching last question, BOT will ask for confirmation before submitting in last question page if all question is successfully answered and `submit_quiz_confirmation` is set to `True` in `config.ini` file, otherwise it will automatically submit.
8. After submitting, BOT will ask for confirmation before submitting in summary page `submit_summary_confirmation` is set to `True` in `config.ini` file, otherwise it will automatically submit.

## Known Issues:
1. Suppose there are two answers with similar words, e. g. __a. IGPB__ and __b. GPB__, both contains __GPB__ in their answer while answer in the answer document is __GPB__, any first option that contains __GPB__ will be selected, thus the __a. IGPB__ will be selected and answer is wrong. [source](https://github.com/SonicZedt/VStudent/blob/5168a4fe80cba582bc3e0634e064bb8fa61758f2/vclass.py#L193-L195).
2. Failed to extract question and answer from type 2 document (.docx) because the paragraph is inside of textbox. [source](https://github.com/SonicZedt/VStudent/blob/5168a4fe80cba582bc3e0634e064bb8fa61758f2/answer.py#L69-L72).
3. Failed to extract question and answer from type 1 document (.txt) with UTF-8 encoding. Temporary workaround is to change the encoding to ANSI which can be done by opening the file in Notepad and save as new document with ANSI is selected as _Encoding_ option.
4. Failed to launch BOT executable file (vsg.exe) if mozila firefox has not been installed. This could be fixed by launching the driver executable inside `driver/` folder.
5. Any differences in visual arrangement in a PDF document could cause the BOT to fail to do extraction process.
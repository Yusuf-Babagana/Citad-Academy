import os
from docx import Document
import re
from xml.etree import ElementTree as ET
from docx.shared import Inches
import base64
from io import BytesIO

def extract_image_from_run(run):
    """
    Extracts an image embedded in a run and returns its base64 representation.
    """
    image_b64 = ''
    if run.element.xpath('.//a:blip'):
        image = run.element.xpath('.//a:blip')[0]
        image_rid = image.attrib['{{{}}}embed'.format(image.nsmap['r'])]
        image_part = run.part.related_parts[image_rid]
        image_bytes = image_part.blob
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    return image_b64

def extract_text_from_paragraph(paragraph):
    """
    Extracts and returns the text, special formatting, and media from a paragraph.
    """
    text = ''
    for run in paragraph.runs:
        if run.bold:
            text += f'<strong>{run.text}</strong>'
        elif run.italic:
            text += f'<em>{run.text}</em>'
        elif run.underline:
            text += f'<u>{run.text}</u>'
        else:
            text += run.text

        # Handling embedded images
        image_b64 = extract_image_from_run(run)
        if image_b64:
            text += f'<img src="data:image/png;base64,{image_b64}" alt="Embedded Image"/>'

    return text.strip()

def is_question_start(text):
    """
    Determines if a given text signifies the start of a question.
    """
    return bool(re.match(r'^\d+\.', text))

def parse_option(text):
    """
    Parses an option text and identifies if it's the correct answer.
    """
    match = re.match(r'^(A|B|C|D)\.\s*(\*?)(.*)', text, re.DOTALL)
    if match:
        return {'text': match.group(3).strip(), 'is_correct': bool(match.group(2))}
    return None

def parse_word_document(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    doc = Document(file_path)
    questions = []
    current_question = None
    current_topic = None
    current_subtopic = None
    current_instruction = None

    for para in doc.paragraphs:
        text = extract_text_from_paragraph(para)
        if not text:
            continue

        if text.startswith('Topic:'):
            current_topic = text[len('Topic:'):].strip()
            continue
        elif text.startswith('Subtopic:'):
            current_subtopic = text[len('Subtopic:'):].strip()
            continue
        elif text.startswith('Instructions:'):
            current_instruction = text[len('Instructions:'):].strip()
            continue

        if is_question_start(text) or current_question is None:
            if current_question:
                questions.append(current_question)
            current_question = {
                'topic': current_topic,
                'subtopic': current_subtopic,
                'instructions': current_instruction,
                'text': text,
                'options': [],
                'explanation': ''
            }

        elif current_question is not None:
            option = parse_option(text)
            if option:
                current_question['options'].append(option)
            elif text.lower().startswith('explanation:'):
                current_question['explanation'] = text[len('Explanation:'):].strip()
            else:
                current_question['text'] += ' ' + text

    if current_question:
        questions.append(current_question)

    return questions

# Example usage
# questions = parse_word_document('path_to_your_word_document.docx')

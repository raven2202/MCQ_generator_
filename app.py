from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import spacy
import random
from PyPDF2 import PdfReader

app = Flask(__name__)
Bootstrap(app)

nlp = spacy.load("en_core_web_sm")


def generate_mcqs(text, num_questions=5):
    if not text or not isinstance(text, str) or len(text.strip()) < 100:
        return []

    doc = nlp(text)

    sentences = [sent for sent in doc.sents if len(sent.text.strip().split()) > 5]
    if not sentences:
        return []

    all_entities_and_chunks = list(
        set([ent.text.strip() for ent in doc.ents] + [chunk.text.strip() for chunk in doc.noun_chunks]))

    num_questions = min(num_questions, len(sentences))
    if num_questions <= 0:
        return []

    selected_sentences = random.sample(sentences, num_questions)
    mcqs = []

    for sent_doc in selected_sentences:
        potential_answers = [ent.text.strip() for ent in sent_doc.ents] + [chunk.text.strip() for chunk in
                                                                           sent_doc.noun_chunks]
        potential_answers = list(set([ans for ans in potential_answers if len(ans) > 1]))

        if not potential_answers:
            continue

        subject = random.choice(potential_answers)
        question_stem = sent_doc.text.replace(subject, "______")

        answer_choices = [subject]

        distractors = [d for d in all_entities_and_chunks if d.lower() != subject.lower()]

        num_distractors_to_sample = min(len(distractors), 3)
        if num_distractors_to_sample > 0:
            final_distractors = random.sample(distractors, num_distractors_to_sample)
            answer_choices.extend(final_distractors)

        random.shuffle(answer_choices)

        try:
            correct_answer_index = answer_choices.index(subject)
            correct_answer_letter = chr(65 + correct_answer_index)
        except ValueError:
            continue

        mcqs.append((question_stem, answer_choices, correct_answer_letter))

    return mcqs


def process_pdf(file):
    text = ""
    try:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception:
        return ""
    return text


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = ""
        if 'files[]' in request.files:
            files = request.files.getlist('files[]')
            for file in files:
                if file and file.filename.endswith('.pdf'):
                    text += process_pdf(file)
                elif file and file.filename.endswith('.txt'):
                    text += file.read().decode('utf-8', errors='ignore')
        else:
            text = request.form['text']

        num_questions = int(request.form.get('num_questions', 5))
        mcqs = generate_mcqs(text, num_questions=num_questions)
        mcqs_with_index = [(i + 1, mcq) for i, mcq in enumerate(mcqs)]
        return render_template('mcqs.html', mcqs=mcqs_with_index)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
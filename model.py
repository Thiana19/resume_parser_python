from flask import Flask, request, render_template
import os
import pdfplumber
import re

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def extract_text_from_pdf(pdf_path):
    text = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() if page.extract_text() else ''
    return text

def parse_information(text):
    profile = {}
    education = []
    experience = []

    # Regular expressions adjusted for the specific format of the provided CV
    profile['Name'] = re.search(r'(?i)^(.+)', text).group().strip() if re.search(r'(?i)^(.+)', text) else 'Not found'
    profile['Phone'] = re.search(r'\(\+33\)\s*([\d\s]+)', text).group(1).strip() if re.search(r'\(\+33\)\s*([\d\s]+)', text) else 'Not found'
    profile['Email'] = re.search(r'([\w\.-]+@[\w\.-]+\.\w+)', text).group(1).strip() if re.search(r'([\w\.-]+@[\w\.-]+\.\w+)', text) else 'Not found'
    
    # Extract experience details
    experience_text = re.findall(r'(\d{4})\s*-\s*(\d{4}|present)\s*:\s*(.+?)(?=\d{4}|\Z)', text, re.DOTALL | re.IGNORECASE)
    for exp in experience_text:
        year_from, year_to, desc = exp
        experience.append({'Year From': year_from, 'Year To': year_to if year_to != 'present' else 'Now', 'Description': desc.strip()})

    # Extract education details
    education_text = re.findall(r'(\d{4})\s+(.+?)(?=\d{4}|\Z)', text, re.DOTALL | re.IGNORECASE)
    for edu in education_text:
        year, desc = edu
        education.append({'Year': year, 'Description': desc.strip()})

    return profile, education, experience

@app.route('/', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Extract text from PDF
            text = extract_text_from_pdf(file_path)

            # Parse the resume into profile, education, and experience sections
            profile, education, experience = parse_information(text)

            # Render parsed data
            return render_template('result.html', profile=profile, education=education, experience=experience)
        else:
            return "Invalid file type. Please upload a PDF file."
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)

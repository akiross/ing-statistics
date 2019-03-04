import os
import re
import moment
import statistics
from datetime import datetime
from decimal import Decimal
from bs4 import BeautifulSoup
from flask import Flask, request


UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['html', 'xls'])  # txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 512 * 1024  # 512K


def parse_data(content):
    soup = BeautifulSoup(content, 'html.parser')
    header, table = None, []
    for tr in soup.table.contents:
        if tr.td.string is None:
            break  # Stop on first empty row
        # First iteration is header
        date, _, reason, description, amount = map(lambda e: str(e.string), tr.contents)

        parsed = re.search('[0-9,+ -]+', amount)
        if parsed:
            amount = Decimal(parsed.group(0).replace(' ', '').replace(',', '.'))
            date = datetime.strptime(date, '%d/%m/%Y')
            table.append((date, reason, description, amount))
        else:
            header = (date, reason, description, amount)

    return header, table


def render_stats(table):
    table = sorted(table)
    start_date, end_date = table[0][0], table[-1][0]
    start_date = start_date.strftime("%d %b %Y")
    end_date = end_date.strftime("%d %b %Y")
    return f'''
        <div><b>Periodo:</b> <span>{start_date} - {end_date}</span>
        <div><b>Bilancio:</b> <span>{sum(r[-1] for r in table)} €</span>
        <div><b>Entrate:</b> <span>{sum(r[-1] for r in table if r[-1] > 0)} €</span>
        <div><b>Uscite:</b> <span>{sum(r[-1] for r in table if r[-1] < 0)} €</span>
    '''


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    template = '''
    <!doctype html>
    <title>{title}</title>
    <h1>{title}</h1>
    '''
    form = '''
    <form method=post enctype=multipart/form-data>
        <div><input type="file" name="file"></div>
        <div><input type="submit" value="Carica"></div>
    </form>
    '''

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return template.format(title='Manca la parte del file')
        file_data = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file_data.filename == '':
            return template.format(title='Nessun file selezionato')
        if file_data and allowed_file(file_data.filename):
            header, table = parse_data(file_data.read())
            return template.format(title='Statistiche') + render_stats(table)
    return template.format(title='Carica file') + form

from flask import Flask, render_template, request
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)


# Читаем ключи из файла
scope = ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    '/home/sizematters/mysite/creds.json', scope
)
gc = gspread.authorize(credentials)

spreadsheet = gc.open('Rita\'s results')
worksheet = spreadsheet.sheet1


@app.route('/')
def main_page():
    data = get_as_dataframe(worksheet)

    data = data.dropna(how='all')

    if data.empty:
        first = 1
    else:
        big = data.type.to_list().count('big')
        small = data.type.to_list().count('small')
        if big > small:
            first = 0
        else:
            first = 1
    if first:
        link = 'big'
    else:
        link = 'small'
    return(render_template('index.html', link=link, stop=0, type=link))


@app.route('/small', methods=['GET'])
def small():
    tp = request.args.get('type')
    if request.args.get('age'):
        age = request.args.get('age')
    else:
        age = 0
    if request.args.get('stop') == '1':
        big = request.args.get('big')
        link = 'finish'
        stop = 0
    else:
        big = ''
        link = 'big'
        stop = 1
    print('small', link)
    return(render_template('small.html', link=link, stop=stop, age=age, big=big, type=tp))

@app.route('/big')
def big():
    tp = request.args.get('type')
    if request.args.get('age'):
        age = request.args.get('age')
    else:
        age = 0
    if request.args.get('stop') == '1':
        small = request.args.get('small')
        link = 'finish'
        stop = 0
    else:
        small = ''
        link = 'small'
        stop = 1
    print('big', link)
    return(render_template('big.html', link=link, stop=stop, age=age, small=small, type=tp))


@app.route('/finish')
def finish():
    data = {
        'age': request.args.get('age'),
        'type': request.args.get('type'),
        'big': request.args.get('big'),
        'small': request.args.get('small')
    }
    df = pd.DataFrame([data])
    table = get_as_dataframe(worksheet).dropna(how='all').iloc[:,:4]
    df = pd.concat([table, df])
    set_with_dataframe(worksheet, df)
    return(render_template('finish.html'))

if __name__ == '__main__':
    app.run()
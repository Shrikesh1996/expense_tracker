from flask import Flask, render_template, request, redirect, send_file, session, url_for
import pandas as pd
from datetime import datetime
import os


app = Flask(__name__)
app.secret_key = 'simplekey'

STATIC_USERNAME = 'karmoreshrikesh0@gmail.com'
STATIC_PASSWORD = 'SecAuth01#'

FILE_NAME = 'expenses.xlsx'
COLUMNS = ['Date', 'Amount', 'Description', 'Category']

if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=COLUMNS)
    df.to_excel(FILE_NAME, index=False)

def load_data():
    return pd.read_excel(FILE_NAME)

def save_data(df):
    df.to_excel(FILE_NAME, index=False)

# ---------------- Authentication ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == STATIC_USERNAME and request.form['password'] == STATIC_PASSWORD:
            session['user'] = request.form['username']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.before_request
def require_login():
    if request.endpoint not in ('login', 'static') and 'user' not in session:
        return redirect(url_for('login'))

# ---------------- Routes ----------------

@app.route('/', methods=['GET', 'POST'])
def index():
    df = load_data()
    if request.method == 'POST':
        amount = request.form['amount']
        description = request.form['description']
        category = request.form['category']
        date = datetime.now().strftime('%Y-%m-%d')
        new_data = pd.DataFrame([[date, amount, description, category]], columns=COLUMNS)
        df = pd.concat([df, new_data], ignore_index=True)
        save_data(df)
        return redirect('/')

    filter_date = request.args.get('date')
    filter_cat = request.args.get('category')
    filtered_df = df
    if filter_date:
        filtered_df = filtered_df[filtered_df['Date'] == filter_date]
    if filter_cat:
        filtered_df = filtered_df[filtered_df['Category'] == filter_cat]

    expenses = filtered_df.values.tolist()
    total = filtered_df['Amount'].sum()
    return render_template('index.html', expenses=expenses, total=total)

@app.route('/delete', methods=['POST'])
def delete():
    df = load_data()
    selected_index = int(request.form['selected_index'])
    df.drop(index=selected_index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    save_data(df)
    return redirect('/')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    df = load_data()
    if request.method == 'GET':
        idx = int(request.args.get('selected_index'))
        row = df.iloc[idx]
        return render_template('edit.html', index=idx, row=row)
    if request.method == 'POST':
        idx = int(request.form['index'])
        df.at[idx, 'Amount'] = request.form['amount']
        df.at[idx, 'Description'] = request.form['description']
        df.at[idx, 'Category'] = request.form['category']
        save_data(df)
        return redirect('/')

@app.route('/export_csv')
def export_csv():
    return send_file(FILE_NAME, as_attachment=True)

@app.route('/display')
def display():
    df = load_data()
    df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M')
    summary = df.groupby(['Month', 'Category'])['Amount'].sum().reset_index()
    summary = summary.pivot(index='Month', columns='Category', values='Amount').fillna(0)
    summary = summary.reset_index()
    return render_template('display.html', tables=[summary.to_html(classes='table table-bordered', index=False)], titles=summary.columns.values)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

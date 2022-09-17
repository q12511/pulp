from flask import Flask, make_response, redirect, render_template, request
import pandas as pd
from problem import Scheduring

app = Flask(__name__)

def check_request(request):
  workers = request.files['workers']
  shift = request.files['shift']
  wish = request.files['wish']

  if workers.filename == '':
    return False
  if shift.filename == '':
    return False
  if wish.filename == '':
    return False

  return True

def preprocess(request):
  workers = request.files['workers']
  shift = request.files['shift']
  wish = request.files['wish']

  w_df = pd.read_csv(workers)
  s_df = pd.read_csv(shift)
  wish_df = pd.read_csv(wish, index_col=0)

  return w_df, s_df, wish_df

def postprocess(solution_df):
  solution_html = solution_df.to_html(header=True, index=True)
  return solution_html

@app.route('/', methods=['GET', 'POST'])
def solve():
  if request.method == 'GET':
    return render_template('index.html', solution_html=None)

  if not check_request(request):
    return redirect(request.url)

  w_df, s_df, wish_df = preprocess(request)
  solution_df = Scheduring(w_df, s_df, wish_df).solve()
  solution_html = postprocess(solution_df)
  return render_template('index.html', solution_html=solution_html)

@app.route('/download', methods=['POST'])
def download():
  solution_html = request.form.get('solution_html')
  solution_df = pd.read_html('solution_df')[0]
  solution_csv = solution_df.to_csv(index=False)
  response = make_response()
  response.data = solution_csv
  response.headers['Content-Type'] = 'text/csv'
  response.headers['Content-Disposition'] = 'attachment;filename=solution.csv'
  return response

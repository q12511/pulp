from flask import Flask, make_response, request
import pandas as pd

from problem import Scheduring

app = Flask(__name__)


def preprocess(request):
  workers = request.files['workers']
  shift = request.files['shift']
  wish = request.files['wish']

  w_df = pd.read_csv(workers)
  s_df = pd.read_csv(shift)
  wish_df = pd.read_csv(wish, index_col=0)

  return w_df, s_df, wish_df

def postprocess(solution_df):
  solution_csv = solution_df.to_csv(index=False)
  response = make_response()
  response.data = solution_csv
  response.headers['Content-Type'] = 'text/csv'
  return response

@app.route('/api', methods=['POST'])
def solve():
  w_df, s_df, wish_df = preprocess(request)
  solution_df = Scheduring(w_df, s_df, wish_df).solve()
  response = postprocess(solution_df)
  return response

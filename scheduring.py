#%%
import pulp
import pandas as pd

class ShiftScheduring():
  def __init__(self, w_df, s_df, wish_df, name='ShiftProblem'):
    self.w_df = w_df
    self.s_df = s_df
    self.wish_df = wish_df
    self.name = name
    self.prob = self._formulate()

  def _formulate(self):
    # model instance
    prob = pulp.LpProblem('ShiftScheduring', pulp.LpMaximize)

    # number of days
    ND = 30

    # worker_list
    W = self.w_df['worker_id'].tolist()

    # day_list
    D = [d for d in range(1, ND+1)]

    # shift_list
    S = self.s_df['shift_sign'].tolist()
    #print(S[6])

    # worker day and shift pair list
    WDS = [(w,d,s) for w in W for d in D for s in S]
    # worker assign shift varliable
    x = pulp.LpVariable.dicts('x', WDS, cat='Binary')

    # 2連休あるかないか
    y = pulp.LpVariable.dicts('y', [(w,d) for w in W for d in D[:-1]], cat='Binary')

    z = pulp.LpVariable.dicts('z', [(w,d) for w in W for d in D[:-2]], cat='Binary')

    #prob += -2 * pulp.lpSum(y[w,d] for w in W for d in D[:-1]) + 8 * pulp.lpSum(z[w,d] for w in W for d in D[:-2])

    # (0) 各作業員はそれぞれの日に一つのシフトにつく
    for w in W:
      for d in D:
        prob += pulp.lpSum([x[w,d,s] for s in S]) == 1


    # (1) 各日に一人の作りを割り当てる
    #作り集合
    W_cook = [row.worker_id for row in self.w_df.itertuples() if row.G_flag == 1]
    W_Ncook = [row.worker_id for row in self.w_df.itertuples() if row.G_flag == 0]
    #print(W_cook)
    for d in D:
      prob += pulp.lpSum([x[w,d,S[5]] + x[w,d,S[6]] for w in W_cook]) == 1
      prob += pulp.lpSum([x[w,d,S[5]] + x[w,d,S[6]] for w in W_Ncook]) == 0

    # (2) 朝3人　昼３人　夜３人
    S_M = [row.shift_sign for row in self.s_df.itertuples() if row.morning == 1]
    S_D = [row.shift_sign for row in self.s_df.itertuples() if row.daytime == 1]
    S_N = [row.shift_sign for row in self.s_df.itertuples() if row.night == 1]
    #print(S_M)
    #print(S_D)
    #print(S_N)

    # (2).1 朝3人　昼３人　夜2人
    for d in D:
      prob += pulp.lpSum([x[w,d,s] for s in S_M for w in W]) == 3
      prob += pulp.lpSum([x[w,d,s] for s in S_D for w in W]) == 3
      prob += pulp.lpSum([x[w,d,s] for s in S_N for w in W]) == 2

    # (3) 5連続勤務　禁止
    for w in W:
      for d in D[4:]:
        prob += pulp.lpSum([x[w,d - h,s] for h in range(4 + 1) for s in S[:7]]) <= 4

    # (4) B は一人
    for d in D:
      prob += pulp.lpSum([x[w,d,S[4]] for w in W]) == 1

    # (5) G　２連続　禁止
    for w in W_cook:
      for d in D[2:]:
        prob += pulp.lpSum([x[w,d - h,S[5]] + x[w,d - h,S[6]] for h in range(2 + 1)]) <= 1

    # (6) GB は一回まで
    for w in W_cook:
      prob += pulp.lpSum([x[w,d,S[6]] for d in D]) <= 1

    # (7) 必ず１回は２連休
    # 2連休
    for w in W:
      for d in D[:-1]:
        prob += x[w,d,S[7]] + x[w,d+1,S[7]] -1 <= y[w,d]
        prob += x[w,d,S[7]] + x[w,d+1,S[7]] >= 2 * y[w,d]
    # ３連休
    for w in W:
      for d in D[:-2]:
        prob += x[w,d,S[7]] + x[w,d+1,S[7]] + x[w,d+2,S[7]] - 2 <= z[w,d]
        prob += x[w,d,S[7]] + x[w,d+1,S[7]] + x[w,d+2,S[7]] >= 3 * z[w,d]

    # 2連休　3連休　回数制限
    for w in W:
      prob += pulp.lpSum(y[w,d] for d in D[:-1]) >= 1
      prob += pulp.lpSum(z[w,d] for d in D[:-2]) == 0

    #print(W, D)

    # (8) 希望休
    for m in range(len(self.wish_df)):
      for n in range(len(self.wish_df.columns)):
        if self.wish_df.iat[m,n] == 1:
          prob += x[W[m],D[n],S[7]] == 1

    return {'prob': prob, 'variable': {'x': x}, 'list': {'W': W, 'D': D, 'S': S}}

  def solve(self):
    #　求解
    status = self.prob['prob'].solve()
    #print(('Status:', pulp.LpStatus[status]))

    x = self.prob['variable']['x']
    W = self.prob['list']['W']
    D = self.prob['list']['D']
    S = self.prob['list']['S']

    wds = [[0 for d in range(len(D))] for w in range(len(W))]

    # 表示
    for w in W:
      #print('worker', w, end="  ")
      for d in D:
        for i, s in enumerate(S):
          if x[w,d,s].value() == 1.0:
            #print(w, d)
            if i == 0:
              #print("A", end='  ')
              wds[w-1][d-1] = 'A'
            if i == 1:
              #print("AD", end=' ')
              wds[w-1][d-1] = 'AD'
            if i == 2:
              #print("D", end='  ')
              wds[w-1][d-1] = 'D'
            if i == 3:
              #print("B", end='  ')
              wds[w-1][d-1] = 'DB'
            if i == 4:
              #print("DB", end=' ')
              wds[w-1][d-1] = 'B'
            if i == 5:
              #print("G", end='  ')
              wds[w-1][d-1] = 'G'
            if i == 6:
              #print("GB", end=' ')
              wds[w-1][d-1] = 'GB'
            if i == 7:
              #print("V", end='  ')
              wds[w-1][d-1] = 'V'
            else:
              pass
      #print()

    solution_df = pd.DataFrame(wds, columns=D, index=W)
    return solution_df

if __name__ == '__main__':
  w_df = pd.read_csv('worker.csv')
  s_df = pd.read_csv('shift.csv')
  wish_df = pd.read_csv('wish.csv', index_col=0)

  prob = ShiftScheduring(w_df, s_df, wish_df)

  solution_df = prob.solve()

  print('Solustion: \n', solution_df)
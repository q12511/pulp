#%%
import pulp
import pandas as pd

# number of days
ND = 30

w_df = pd.read_csv('worker.csv')
s_df = pd.read_csv('shift.csv')

# model instance
prob = pulp.LpProblem('ShiftScheduring', pulp.LpMaximize)

# worker_list
W = w_df['worker_id'].tolist()
#print(W)

# day_list
D = [d for d in range(1, ND+1)]

# shift_list
S = s_df['shift_sign'].tolist()
#print(S)

# worker day and shift pair list
WDS = [(w,d,s) for w in W for d in D for s in S]
# worker assign shift varliable
x = pulp.LpVariable.dicts('x', WDS, cat='Binary')

# (0) 各作業員はそれぞれの日に一つのシフトにつく
for w in W:
  for d in D:
    prob += pulp.lpSum([x[w,d,s] for s in S]) == 1


# (1) 各日に一人の作りを割り当てる
#作り集合
W_cook = [row.worker_id for row in w_df.itertuples() if row.G_flag == 1]
W_Ncook = [row.worker_id for row in w_df.itertuples() if row.G_flag == 0]
#print(W_cook)
for d in D:
  prob += pulp.lpSum([x[w,d,S[5]] for w in W_cook]) == 1
  prob += pulp.lpSum([x[w,d,S[5]] for w in W_Ncook]) == 0

# (2) 朝3人　昼３人　夜３人
S_M = [row.shift_sign for row in s_df.itertuples() if row.morning == 1]
S_D = [row.shift_sign for row in s_df.itertuples() if row.daytime == 1]
S_N = [row.shift_sign for row in s_df.itertuples() if row.night == 1]
#print(S_M)
#print(S_D)
#print(S_N)

# (2).1 朝3人　昼３人　夜2人
for d in D:
  prob += pulp.lpSum([x[w,d,S[0]] + x[w,d,S[1]] for w in W]) == 3
  prob += pulp.lpSum([x[w,d,S[1]] + x[w,d,S[2]] + x[w,d,S[4]] for w in W]) == 3
  prob += pulp.lpSum([x[w,d,S[3]] + x[w,d,S[4]] for w in W]) == 2

# (3) 5連続勤務　禁止
for w in W:
  for d in D[4:]:
    prob += pulp.lpSum([x[w,d - h,s] for h in range(4 + 1) for s in S[:6]]) <= 4

# (4) B は一人
for d in D:
  prob += pulp.lpSum([x[w,d,S[4]] for w in W]) == 1

# (5) G　２連続　禁止
for w in W:
  for d in D[2:]:
    prob += pulp.lpSum([x[w,d - h,S[5]] for h in range(2 + 1)]) <= 1

# (6) 必ず１回は２連休
for w in W:
  for d in D[2:]:
    prob += pulp.lpSum([x[w,d - h,S[6]] for h in range(2 + 1)]) >= 1

#　求解
status = prob.solve()
print(('Status:', pulp.LpStatus[status]))

'''
for i in range(1, ND):
  print(i, end='                           ')
print()
for j in range(6):
  for i in range(1, ND+1):
    print(i, end='   ')
print()
'''

print('          ', end='')
for d in D:
  if d < 10:
    print(d, end='  ')
  else:
    print(d, end=' ')
print()

for w in W:
  print('worker', w, end="  ")
  for d in D:
    for i, s in enumerate(S):
      if x[w,d,s].value() == 1.0:
        
        if i == 0:
          print("A", end='  ')
        if i == 1:
          print("AD", end=' ')
        if i == 2:
          print("D", end='  ')
        if i == 3:
          print("B", end='  ')
        if i == 4:
          print("DB", end=' ')
        if i == 5:
          print("G", end='  ')
        if i == 6:
          print("V", end='  ')
        else:
          #print(i, end=' ')
          pass
      #print(x[w,d,s].value(), end=' ')
  print()


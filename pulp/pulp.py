#%%
import pulp
import pandas as pd

# number of days
ND = 7

w_df = pd.read_csv('worker.csv')
s_df = pd.read_csv('shift.csv')

# model instance
prob = pulp.LpProblem('ShiftScheduring', pulp.LpMaximize)

# worker_list
W = w_df['worker_id'].tolist()
#print(W)

# day_list
D = [d for d in range(1, ND)]

# shift_list
S = s_df['shift_sign'].tolist()
#print(S)

# worker day and shift pair list
WDS = [(w,d,s) for w in W for d in D for s in S]
# worker assign shift varliable
x = pulp.LpVariable.dicts('x', WDS, cat='Binary')

# (1) 各作業員はそれぞれの日に一つのシフトにつく
for w in W:
  for d in D:
    prob += pulp.lpSum([x[w,d, s] for s in S]) == 1

# (2) 朝3人　昼３人　夜３人　作り１人

# (3) 5連続勤務　禁止

# (4) G　２連続　禁止

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


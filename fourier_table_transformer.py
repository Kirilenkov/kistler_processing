import pandas as pd
import os

hard_path = 'C:/Users/Kirill/Desktop'
os.chdir(hard_path)

df = pd.read_csv('kistler_fourier.csv', delimiter=';')
micro_df_list = []
macro_df_list = []
for i in range(df.__len__()):
    snippet = df.loc[[i]]
    inf = df.iloc[i, 0].split(' ')
    suff = inf[-1][0:3]
    name = inf[0]
    trigg = int(suff[-1])
    eyes = trigg % 2
    if eyes == 1:
        suff += '_EO'
    elif eyes == 0:
        suff += '_EC'
    clms = [c + '_' + suff for c in snippet.columns]
    snippet.columns = clms
    snippet.drop(columns=clms[0], inplace=True)
    # snippet.reset_index(inplace=True)
    snippet.set_index(pd.Index([0]), inplace=True)
    print(snippet)
    micro_df_list.append(snippet)
    if trigg == 8:
        line = pd.concat(micro_df_list, axis=1, sort=True)
        print(line)
        micro_df_list.clear()


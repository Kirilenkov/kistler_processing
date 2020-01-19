import pandas as pd
import os

hard_path = 'C:/Users/Kirill/Desktop'
os.chdir(hard_path)

df = pd.read_csv('kistler_fourier.csv', delimiter=';')
micro_df_list = []
macro_df_list = []
table = pd.DataFrame()
for i in range(df.__len__()):
    snippet = df.loc[[i]]
    inf = df.iloc[i, 0].split(' ')
    suff = inf[-1][0:3]
    name = inf[0]
    trigg = int(suff[-1])
    eyes = trigg % 2
    if eyes == 1:
        suff += '_EC'
    elif eyes == 0:
        suff += '_EO'
    clmns = [c + '_' + suff for c in snippet.columns]
    snippet.columns = clmns
    snippet.drop(columns=clmns[0], inplace=True)
    snippet.set_index(pd.Index([name]), inplace=True)
    micro_df_list.append(snippet)
    if trigg == 8:
        line = pd.concat(micro_df_list, axis=1, sort=True)
        print(line)
        macro_df_list.append(line)
        micro_df_list.clear()
table = pd.concat(macro_df_list, axis=0)
writer = pd.ExcelWriter('kistler_fourier_ultimate.xlsx')
table.to_excel(writer, sheet_name='Fourier', index=True)
writer.save()

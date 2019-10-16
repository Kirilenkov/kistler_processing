from inputpath import path_setter
import os
import pandas as pd

message =  'Введите полный путь к папке с логфайлами стабилоплатформы kistler: '
hard_path = 'C:/Users/Kirill/Desktop/results/res'
path_setter(hard_path, message=message)
files = os.listdir(path='.')
print('File list: ')
for i in files:
    print(i)

df = pd.DataFrame()


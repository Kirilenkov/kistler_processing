from inputpath import path_setter
import os
import pandas as pd
from math import sqrt

message = 'Введите полный путь к папке с логфайлами стабилоплатформы Kistler: '
hard_path = 'C:/Users/Kirill/Desktop/kistler/main'
path_setter(hard_path, message=message)
# only files less than 500000 bytes:
files = list(filter(lambda f: os.path.getsize(f) < 500000 and not 'No_outliers' in f, os.listdir(path='.')))
print('File list: ')
for i in files:
    print(i)

alpha_avg = 0.01
alpha_var = 0.01
'''-------Input alpha part------'''
while True:
    try:
        alpha_param = float(input('Введите коэффициент сглаживания для среднего в интервале (0, 1):\n'))
        if 0 < alpha_param < 1:
            alpha_avg = alpha_param
            break
        else:
            print('Вы вышли за пределы интервала (0, 1)')
    except Exception as e:
        print(e)
        print('Ведите десятичное дробное через точку в интервале от 0 до 1')

while True:
    try:
        alpha_param = float(input('Введите коэффициент сглаживания для дисперсии в интервале (0, 1):\n'))
        if 0 < alpha_param < 1:
            alpha_var = alpha_param
            break
        else:
            print('Вы вышли за пределы интервала (0, 1)')
    except Exception as e:
        print(e)
        print('Ведите десятичное дробное через точку в интервале от 0 до 1')
'''-----------------------------'''

writer = pd.ExcelWriter('../kistler_alphas_{0:s}_{1:s}.xlsx'.format(str(alpha_avg), str(alpha_var)))

def outlier_check(value, mean, std):
    if mean + 3*std < value or mean - 3*std > value:
        return True
    else:
        return False

def exp_avg(curr_val, prev_avg, alpha=alpha_avg):
    return (1 - alpha)*prev_avg + curr_val*alpha

def exp_variance(curr_val, prev_variance, prev_avg, alpha=alpha_var):
    diff = curr_val - prev_avg
    incr = alpha * diff
    return (1 - alpha) * (prev_variance + diff * incr)

for file in files:

    df = pd.read_csv(file, names=['Time', 'X', 'Y', 'Cue_X', 'Cue_Y'], sep='\t', skip_blank_lines=True, skiprows=19, error_bad_lines=False, engine='python')
    X_mean = df.mean(axis=0).loc['X']
    Y_mean = df.mean(axis=0).loc['Y']
    X_std = df.std(axis=0).loc['X']
    Y_std = df.std(axis=0).loc['Y']

    X_avg = X_mean
    Y_avg = Y_mean

    X_variance = X_std**2
    Y_variance = Y_std**2

    X_counter = 0
    Y_counter = 0

    deletion_key = set()
    print('----------------------------------------\n'
        'Processing {!r} ...'.format(file))

    for i in range(df.__len__()):

        cvx = df.loc[i, 'X']
        tx = int(outlier_check(cvx, X_avg, sqrt(X_variance)))
        X_counter += tx
        df.loc[i, 'Cue_X'] = tx
        if tx == 1:
            deletion_key.add(i)
            print('File {1:s}. X outlier line: {0:d}'.format(i, file))
        X_variance = df.loc[i, 'exp_X_var'] = exp_variance(cvx, X_variance, X_avg)
        X_avg = df.loc[i, 'exp_X_avg'] = exp_avg(cvx, X_avg)

        cvy = df.loc[i, 'Y']
        ty = int(outlier_check(cvy, Y_avg, sqrt(Y_variance)))
        Y_counter += ty
        df.loc[i, 'Cue_Y'] = ty
        if ty == 1:
            deletion_key.add(i)
            print('File {1:s}. Y outlier line: {0:d}'.format(i, file))
        Y_variance = df.loc[i, 'exp_Y_var'] = exp_variance(cvy, Y_variance, Y_avg)
        Y_avg = df.loc[i, 'exp_Y_avg'] = exp_avg(cvy, Y_avg)

    print('\nFor file {0!r},\n'
        'the number of X drop-down lines is: {1:d},\n'
        'the number of Y drop-down lines is: {2:d}'.format(file, X_counter, Y_counter))


    df.drop(deletion_key, inplace=True)
    df.drop(columns=['Cue_X', 'Cue_Y', 'exp_X_var', 'exp_Y_var', 'exp_X_avg', 'exp_Y_avg'], inplace=True)
    with open('No_outliers_alphas_' + str(alpha_avg) + '_' + str(alpha_var) + '_' + file, 'w', encoding='utf-8') as f:
        f.write(df.to_string(header = True, index = False))

    df.to_excel(writer, sheet_name=file[:-4], index=False)
    writer.save()

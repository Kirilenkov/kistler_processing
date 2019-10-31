from inputpath import path_setter
import os
import pandas as pd
from math import sqrt
from datetime import datetime as dt

message = 'Введите полный путь к папке с логфайлами стабилоплатформы Kistler: '
hard_path = 'C:/Users/Kirill/Desktop/kistler/main'
path_setter(hard_path, message=message)
MAX_BYTES = 950000
# only files less than MAX_BYTES:
files = list(filter(lambda fl: os.path.getsize(fl) < MAX_BYTES and 'without_outliers' not in fl, os.listdir(path='.')))
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
date = dt.today().strftime("%d-%m-%Y_%H-%M-%S")
writer = pd.ExcelWriter('../kistler_alphas_{0:s}_{1:s}_{2:s}.xlsx'.format(str(alpha_avg), str(alpha_var), date))


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


def main():
    for file in files:
        df = pd.read_csv(file, names=['Time', 'X', 'Y', 'Cue_X', 'Cue_Y'], sep='\t', skip_blank_lines=True,
                         skiprows=19, error_bad_lines=False, engine='python')
        '''start values: classic mean & standard deviation'''
        x_avg = df.mean(axis=0).loc['X']
        y_avg = df.mean(axis=0).loc['Y']
        x_std = df.std(axis=0).loc['X']
        y_std = df.std(axis=0).loc['Y']

        x_variance = x_std**2
        y_variance = y_std**2

        x_counter = 0
        y_counter = 0

        deletion_key = set()
        print('----------------------------------------\n'
              'Processing {!r} ...'.format(file))

        for index in range(df.__len__()):
            cvx = df.loc[index, 'X']
            tx = int(outlier_check(cvx, x_avg, sqrt(x_variance)))
            x_counter += tx
            df.loc[index, 'Cue_X'] = tx
            if tx == 1:
                deletion_key.add(index)
                print('File {1:s}. X outlier line: {0:d}'.format(index, file))
            x_variance = df.loc[index, 'exp_X_var'] = exp_variance(cvx, x_variance, x_avg)
            x_avg = df.loc[index, 'exp_X_avg'] = exp_avg(cvx, x_avg)

            cvy = df.loc[index, 'Y']
            ty = int(outlier_check(cvy, y_avg, sqrt(y_variance)))
            y_counter += ty
            df.loc[index, 'Cue_Y'] = ty
            if ty == 1:
                deletion_key.add(index)
                print('File {1:s}. Y outlier line: {0:d}'.format(index, file))
            y_variance = df.loc[index, 'exp_Y_var'] = exp_variance(cvy, y_variance, y_avg)
            y_avg = df.loc[index, 'exp_Y_avg'] = exp_avg(cvy, y_avg)

        print('\nFor file {0!r},\n'
              'the number of X drop-down lines is: {1:d},\n'
              'the number of Y drop-down lines is: {2:d}'.format(file, x_counter, y_counter))

        df.drop(deletion_key, inplace=True)
        df.drop(columns=['Cue_X', 'Cue_Y', 'exp_X_var', 'exp_Y_var', 'exp_X_avg', 'exp_Y_avg'], inplace=True)
        with open('without_outliers_alphas_' + str(alpha_avg) + '_' + str(alpha_var) + '_' + file, 'w',
                  encoding='utf-8') as f:
            f.write(df.to_string(header=True, index=False))

        df.to_excel(writer, sheet_name=file[:-4], index=False)
        writer.save()


if __name__ == "__main__":
    main()


# В эксель писать только количество аутлаеров для х и у. Подумать над методами проверки
# для соотвтевтия размера и формата файла. А также проверять на соответвие переменным
# скорость/сила

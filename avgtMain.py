from pandas import DataFrame, Series, NA, read_csv
import os


etn = 73 # от экватора до полюса
wte = 289 # с запада на восток
altCount = 12 # количество высот

# etn = 3
# wte = 5
# altCount = 3

step = wte * altCount

temps = None


# def openFile(path):
#     df = read_csv(path, sep='\s+', header=False)
#     return df


def checkForErrorsAvgTmp(filePath, x, y, EW):
    errors = []
    if filePath == "":
        errors.append("Не указан путь к файлу")
    else:
        if not os.path.isfile(filePath):
            errors.append("Файл, по указанному пути, не существует")
        else:
            global temps
            temps = read_csv(filePath, sep='\s+', header=None)

    try:
        x = float(x)
        y = float(y)
        if EW == 2:
            x = 180 - x + 180

        if x > 180 or x < 0:
            errors.append("Неправильно указана координата X")

        if y > 90 or y < 0:
            errors.append("Неправильно указана координата Y")
    except:
        errors.append("Неправильно введены координаты")

    return x, y, errors


def calcAvgTmp(x, y):
    x = int(x / 1.25)
    y = int(y / 1.25)

    avgTemps = []
    idx = 0
    length = temps.index[-1] + 1
    for i in range(0, altCount):
        tempOnAlt = []
        for j in range(0, length, step):
            tempOnAlt.append(temps.iloc[x + j + idx, y])
        idx += wte
        avgTemps.append(tempOnAlt)

    dfTemps = DataFrame(avgTemps)
    dfTemps.replace(-999.9, NA, inplace=True)

    return dfTemps.mean(axis=1).values
from pandas import DataFrame, NA, read_csv, Series, concat, cut
import numpy as np


meridians = 289
levels = 12
# meridians = 5
# levels = 3
step = meridians * levels


def toBins(min, max, step):
    max = max > 0 and max + 1

    return [i for i in np.arange(min, max, step)]


def prepareDF(df, alt, oneLay=False):
    truncatedDataFrames = []

    idxalt = meridians * (alt - 1)

    for i in range(idxalt, df.index[-1]+1, step):
        truncatedDataFrames.append(df.truncate(i, i+meridians-1))
    truncatedDF = concat(truncatedDataFrames, ignore_index=True)
    truncatedDF.replace(-999.9, np.nan, inplace=True)

    df = DataFrame()

    if oneLay:
        df[0] = truncatedDF.values.flatten()
    else:
        idx = 0
        for i in range(3):
            tempDF = truncatedDF.truncate(idx, idx + 23, 1)
            # tempDF = truncatedDF.truncate(idx, idx, 1)
            df[i] = tempDF.values.flatten()
            idx += 24
            # idx += 1

    return df


def getDataFromDF(df, bins):
    newDF = DataFrame(df)
    newDF['intv'] = cut(df, bins=bins, right=False)

    data = {}

    cnt = newDF.value_counts()
    pct = round(newDF.value_counts(normalize=True) * 100, 2)
    data['counts'] = cnt.values
    data['percents'] = pct.values
    data['mean'] = newDF.groupby('intv')[0].mean().values
    data['sum'] = newDF.groupby('intv')[0].sum().values
    data['min'] = newDF.groupby('intv')[0].min().values
    data['max'] = newDF.groupby('intv')[0].max().values
    data['countsSUM'] = cnt.sum()
    data['percentsSUM'] = round(pct.sum(), 1)
    data['bins'] = bins

    return data


def calcDF(path, intervals, alt, oneLay=False) -> dict:
    workingDF = prepareDF(read_csv(path, sep='\s+', header=None), alt, oneLay)
    workingBins = []
    for i in range(0, len(intervals), 3):
        workingBins.append(toBins(intervals[i], intervals[i+1], intervals[i+2]))

    data = {}

    # group_counts2 = df2['Интервалы'].value_counts()  # Количество значений
    # group_percentages2 = df2['Интервалы'].value_counts(normalize=True) * 100  # Процент
    # group_means2 = df2.groupby('Интервалы')['p_pol'].mean()  # Среднее значение
    # sum_per_bin2 = df2.groupby('Интервалы')['p_pol'].sum()  # Сумма
    # min_per_bin2 = df2.groupby('Интервалы')['p_pol'].min()  # Максимальное
    # max_per_bin2 = df2.groupby('Интервалы')['p_pol'].max()  # Минимальное
    # sum5 = result2['Количество'].sum()
    # sum6 = result2['Процент'].sum()
    # print("Сумма чисел:", sum5)
    # print("Сумма, %:", round(sum6, 1))

    for i in workingBins:
        idx = workingBins.index(i)
        data[idx] = getDataFromDF(workingDF[idx].values.flatten(), i)

    return data
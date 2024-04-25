import re
import glob
import os

months = {
    'Jan': '1',
    'Feb': '2',
    'Mar': '3',
    'Apr': '4',
    'May': '5',
    'Jun': '6',
    'Jul': '7',
    'Aug': '8',
    'Sep': '9',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}

def createStatString(stat):
    statString = f"Год: {stat['year']}\n" \
                 f"Месяц: {stat['month']}\n" \
                 f"Количество измерений: {stat['cnt']}\n\n" \
                 f"Число   Час   Начало   Кол-во строк\n"
    stat.pop('cnt')
    stat.pop('year')
    stat.pop('month')
    for k, v in stat.items():
        for i in range(0, len(v), 3):
            date = i == 0 and k or "  "
            statString += f'{date}{v[i]:>9s}{v[i + 1]:>9s}{v[i + 2]:>15s}\n'
    return statString


def convertFiles(directory, doStat):
    if not os.path.isdir(directory):
        return False

    convDir = directory + '/converted'
    if not os.path.isdir(convDir):
        os.mkdir(convDir)

    for name in glob.iglob('*.txt', root_dir=directory):
        toFile = []
        stat = {'cnt': 0}
        with open(directory + '/' + name, "r") as file:
            adding = False
            newLines = []

            n = 1
            day = 0
            hour = 0

            for line in file.readlines():
                if not adding:
                    if re.search(r' \d\dZ ', line):  # Новое
                        words = line.split()
                        year = words[-1]
                        month = months[words[-2]]
                        day = words[-3]
                        hour = words[-4][:-1]  # Новое ---------------------------------------------------|
                        newLines.append(f" {year}{month:>4s}{str(int(day)):>4s}{str(int(hour)):>4s}     ")
                                                # год    # цифра месяца         # день     # 00 или 12 часов
                        if not stat.get(day):
                            stat[day] = [hour]
                        else:
                            stat[day].append(hour)

                        stat['cnt'] += 1

                        if not stat.get('year'):
                            stat['year'] = year

                        if not stat.get('month'):
                            stat['month'] = month

                        adding = True

                else:
                    try:
                        hPa = float(re.search(r'[0-9.]+', line).group())
                        lnmb = re.sub('\s{7}', " -999.9", line)
                        newLines.append(lnmb)
                    except:
                        length = len(newLines)
                        if length > 1:
                            strLength = str(length - 1)
                            newLines[0] = newLines[0] + strLength + "\n"

                            stat[day].append(str(n + 1))
                            stat[day].append(strLength)
                            n += length

                            toFile.extend(newLines)
                            newLines = []
                            adding = False

        with open(convDir + '/' + name[:-4] + 'converted.txt', "w") as file:  # Новое
            file.writelines(toFile)

        if doStat:
            statDir = directory + '/stat'
            if not os.path.isdir(statDir):
                os.mkdir(statDir)
            with open(statDir + '/' + name[:-4] + 'stat.txt', "w", encoding="utf-8") as file:  # Новое
                file.write(createStatString(stat))

    return True
import requests
import re
import datetime


def make_links(kol_vo):
    """Функция получает в качестве параметра количество необходимых ссылок и возвращает список с параметрами для
    создания ссылок requests.get. Ход работы: получает (год, месяц, день) для текущего дня, затем получает
    datetime-список (год, месяц, день) для генерации ссылок (каждая с разницей в 7 дней от текущего дня), создает
    возвращаемый список.
    :param kol_vo:
    :return:
    """
    local_time = datetime.date.today()
    delta = datetime.timedelta(days=7)
    links_time_date = []
    for x in range(kol_vo):
        a = local_time - delta * x
        links_time_date.append(a)

    links_time = []
    for x in links_time_date:
        a = [x.year, x.month, x.day]
        links_time.append(a)

    links = []
    for x in range(len(links_time)):
        links.append({'school': '1000007501154', 'tab': 'week', 'year': '', 'month': '', 'day': ''})
    for x in range(len(links_time)):
        links[x]['year'] = str(links_time[x][0])
        links[x]['month'] = str(links_time[x][1])
        links[x]['day'] = str(links_time[x][2])
    return links


def get_results(f_rating_tmp):
    tmp = [r'title="Фо', r"title='З"]
    for z in tmp:
        f_rating_tmp = re.sub(z + r'''[^'"]+''', '', f_rating_tmp)
    # Разделение строки на список
    f_rating_tmp = re.split(r'title="', f_rating_tmp)
    tmp = []

    # поиск предметов с оценкой
    for x in range(len(f_rating_tmp)):
        if not re.findall('data-num', f_rating_tmp[x]):
            tmp.append(x)
    tmp.reverse()

    # удаление элементов без оценки
    for x in tmp:
        f_rating_tmp.pop(x)

    subject = []
    # запись в subject названия предметов
    for x in f_rating_tmp:
        tmp = re.match(r'[^"]+', x)
        subject.append(','.join(re.findall(r"match='[^']+", str(tmp)))[7:])

    results = []
    # запись в results оценки
    for x in f_rating_tmp:
        tmp = ','.join(re.findall(r'''data-num="0">[^<]+''', x))
        results.append(tmp[13:])

    # список индексов повторяющихся предметов
    tmp = []
    for x in range(len(subject)):
        try:
            a = subject.index(subject[x], x + 1)
        except ValueError:
            pass
        else:
            results[x] += ', ' + results[a]
            tmp.append(a)
    tmp.sort(reverse=True)
    for x in tmp:
        results.pop(x)
        subject.pop(x)
    results_dict = {}
    for x in range(len(subject)):
        results_dict[subject[x]] = results[x]
    return results_dict


def dict_results(b):
    subjects = b[0]
    for x in range(1, len(b)):
        for y in b[x].keys():
            if y in subjects:
                subjects[y] += ', ' + b[x][y]
            else:
                subjects[y] = b[x][y]
    return subjects


session = requests.Session()
session.headers.update({'user-agent': '''Chrome/86.0.4240.193'''})
passw = {'login': 'olegmerezhko', 'password': '1Spontanius'}
session.post('https://login.kundelik.kz/login', data=passw)
session.cookies.update(dict(session.cookies.items()))
rating_site = session.get('''https://kundelik.kz/feed''')
session.headers.update({'user-agent': '''Chrome/86.0.4240.193''',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'same-site',
                        'Sec-Fetch-User': '?1',
                        'Referer': '''https://kundelik.kz/''',
                        'Connection': 'keep-alive'
                        })

num = int(input('Введите количество недель, за которое нужны оценки: '))
links_times = make_links(num)
results = []
for x in links_times:
    rating_site = session.get(
        '''https://schools.kundelik.kz/marks.aspx''', params=x)
    rating_site = rating_site.text
    if re.findall('diarydays', rating_site):
        f_rating = str(re.findall(r'diarydays[^\n]*', rating_site))
        if re.findall('data-num', f_rating):
            tmp = get_results(f_rating)
            results.append(tmp)
        else:
            print('Нет оценок')
    else:
        print('Nooo')
res = dict_results(results)
for x in res.keys():
    print(x, end=': ')
    print(res[x])

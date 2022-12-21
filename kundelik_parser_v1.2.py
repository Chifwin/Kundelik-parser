import requests
import re
import datetime


def make_links(num, school_num: int):
    """Функция получает в качестве параметра количество необходимых ссылок и возвращает список с параметрами для
    создания ссылок requests.get. Ход работы: получает (год, месяц, день) для текущего дня, затем получает
    datetime-список (год, месяц, день) для генерации ссылок (каждая с разницей в 7 дней от текущего дня), создает
    возвращаемый список.
    :param school_num:
    :param num:
    :return:
    """
    local_time = datetime.date.today()
    delta = datetime.timedelta(days=7)
    links_time_date = []
    for x in range(num):
        a = local_time - delta * x
        links_time_date.append(a)

    links_time = []
    for x in links_time_date:
        a = [x.year, x.month, x.day]
        links_time.append(a)

    links = []
    for x in range(len(links_time)):
        links.append({'school': str(school_num), 'tab': 'week', 'year': '', 'month': '', 'day': ''})
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
    subjects = {}
    for x in range(len(b)):
        for y in b[x].keys():
            if y in subjects:
                subjects[y] += ', ' + b[x][y]
            else:
                subjects[y] = b[x][y]
    return subjects


def get_school_num(a):
    """Из кода страницы kundelik.kz/feed получает код школы ученика, и возвращает его"""
    a = re.findall(r'''"schools":\W?{"id":"\d+''', a)
    a = re.findall(r'"(\d+)', a[0])
    school_num = a[0]
    return school_num


session = requests.Session()
session.headers.update({'user-agent': '''Chrome/86.0.4240.193'''})
login = input('Введите логин от kundelik.kz/: ')
passw = input('Введите пароль: ')
passw = {'login': login, 'password': passw}
while 1:
    try:
        session.post('https://login.kundelik.kz/login', data=passw, timeout=1)
        rating_site = session.get('''https://kundelik.kz/feed''')
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        input('Проблемы при подключении к сайту kundelik.kz. Попробуйте проверить интернет-соединение, и нажмите\
Enter для продолжения выполнения программы, либо закройте данное приложение')
    else:
        break

while rating_site.url != '''https://kundelik.kz/feed''':
    login = input('Вы введи неверный логин/пароль от kundelik.kz/. Пожалуйста, введите верный логин: ')
    passw = input('Введите пароль: ')
    passw = {'login': login, 'password': passw}
    session.post('https://login.kundelik.kz/login', data=passw)
    rating_site = session.get('''https://kundelik.kz/feed''')
rating_site = rating_site.text
school_num = get_school_num(rating_site)

session.cookies.update(dict(session.cookies.items()))  # Обновляет куки для перехода по сайту
session.headers.update({'user-agent': '''Chrome/86.0.4240.193''',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'same-site',
                        'Sec-Fetch-User': '?1',
                        'Referer': '''https://kundelik.kz/''',
                        'Connection': 'keep-alive'
                        })  # Обновляет заголовки, как будто я с kundelik.kz/feed
num = int(input('Введите количество недель, считая от текущего дня, за которое нужны оценки: '))
links_times = make_links(num, school_num)
results = []
for x in links_times:
    try:
        rating_site = session.get(
            '''https://schools.kundelik.kz/marks.aspx''', params=x, timeout=1)
    except requests.exceptions.Timeout:
        print('Проблемы с получением оценок за ', '{0}.{1}.{2}.'.format(x['year'], x['month'], x['day']))
    except requests.exceptions.ConnectionError:
        print('Проблемы с интернет-соединением при получении оценок за ', '{0}.{1}.{2}.'.format(x['year'], x['month'],
                                                                                                x['day']))
    else:
        rating_site = rating_site.text
        if re.findall('diarydays', rating_site):
            f_rating = str(re.findall(r'diarydays[^\n]*', rating_site))
            if re.findall('data-num', f_rating):
                tmp = get_results(f_rating)
                results.append(tmp)
            else:
                print('Нет оценок за ', '{0}.{1}.{2}.'.format(x['year'], x['month'], x['day']))
        else:
            print('Что-то пошло не такю')
res = dict_results(results)
if len(res) == 0:
    print('Нет оценок за выбранный период')
print('')
for x in res.keys():
    print(x, end=': ')
    print(res[x])
print('')
input('Нажмите Enter для выхода из программы')

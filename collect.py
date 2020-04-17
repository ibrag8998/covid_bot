#!/usr/bin/env python
from json import dump, load

import requests
from pendulum import now


def get_date():
    dt = now('Europe/Moscow')
    return f'{dt.year}-{dt.month:02}-{dt.day:02}'


def write(data):
    with open('data.json', 'w') as f:
        dump(data, f, ensure_ascii=False)


def read():
    try:
        with open('data.json') as f:
            return load(f)
    except:
        return [0] * 9


def get_russia(data):
    ru_data = [[i['cases'], i['cured'], i['deaths']] \
            for i in [i for i in data if i.get('ru', False)]]
    s = [0, 0, 0]
    for i in ru_data:
        s = [s[j] + i[j] for j in range(3)]
    return s


def get_dagestan(data):
    return [[i['cases'], i['cured'], i['deaths']] \
            for i in data \
            if i.get('name') == 'Республика Дагестан'][0]


def collect_ru_dag():
    s = requests.Session()
    u = 'https://yandex.ru/maps/api/covid?ajax=1'
    try:
        csrf_token = s.get(u).json()['csrfToken']
        r = s.get(u + '&csrfToken=' + csrf_token)
        data = r.json()['data']['items']
    except:
        return None
    russia = get_russia(data)
    dagestan = get_dagestan(data)
    return russia, dagestan


def collect_world():
    u = 'https://api.covid19api.com/summary'
    r = requests.get(u)
    if r.ok:
        data = r.json()['Global']
        return [
            data['TotalConfirmed'],
            data['TotalRecovered'],
            data['TotalDeaths']
        ]
    else:
        return None


def calc_diff(actual, prev):
    return [actual[i] - prev[i] for i in range(9)]


def collect_data():
    world = collect_world()
    ru, dag = collect_ru_dag()
    data = world + ru + dag
    prev_data = read()
    diff = calc_diff(data, prev_data)
    write(data)
    return data, diff


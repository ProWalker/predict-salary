import os

import requests

from dotenv import load_dotenv
from terminaltables import AsciiTable


def request_hh_api(endpoint, params):
    url = f'https://api.hh.ru/{endpoint}'
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def request_superjob_api(method_name, key, params=None):
    url = f'https://api.superjob.ru/2.0/{method_name}'
    headers = {
        'X-Api-App-Id': key
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_superjob_vacancies(key, params):
    vacancies = []
    params['page'] = 0
    while True:
        page_response = request_superjob_api('vacancies', key, params)
        vacancies.extend(page_response['objects'])
        if not page_response['more']:
            break
        params['page'] += 1

    page_response['objects'] = vacancies
    return page_response


def get_hh_vacancies(params):
    page_response = {}
    vacancies = []
    params['page'] = 0
    pages_number = 1
    while params['page'] < pages_number:
        page_response = request_hh_api('vacancies', params)
        vacancies.extend(page_response['items'])
        pages_number = page_response['pages']
        params['page'] += 1

    page_response['items'] = vacancies
    return page_response


def predict_salary(salary_from, salary_to):
    if salary_from is None and salary_to is None:
        return None
    if salary_from is None:
        return salary_to * 0.8
    if salary_to is None:
        return salary_from * 1.2
    return (salary_from + salary_to) / 2


def predict_rub_salary_hh(vacancy):
    salary = vacancy['salary']
    if salary['currency'] != 'RUR':
        return None
    return predict_salary(salary['from'], salary['to'])


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def get_vacancy_statistic(vacancy_objects, predict_salary_func):
    statistic = {}
    vacancies_processed = 0
    vacancy_salaries = []
    for vacancy in vacancy_objects:
        salary = predict_salary_func(vacancy)
        if salary is not None:
            vacancy_salaries.append(salary)
            vacancies_processed += 1

    vacancy_salaries.sort()
    mid_index = int(len(vacancy_salaries) / 2)
    statistic['vacancies_processed'] = vacancies_processed
    statistic['average_salary'] = vacancy_salaries[mid_index]
    return statistic


def create_table(title, vacancies_statistic):
    table = []
    table_headers = [
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата',
    ]
    table.append(table_headers)
    for lang, statistic in vacancies_statistic.items():
        table_row = [
            lang,
            statistic['vacancies_found'],
            statistic['vacancies_processed'],
            statistic['average_salary'],
        ]
        table.append(table_row)

    return AsciiTable(table, title)


def main():
    load_dotenv()
    superjob_api_key = os.getenv('SUPERJOB_API_KEY')
    hh_vacancies_statistic = {}
    sj_vacancies_statistic = {}
    languages = [
        'Javascript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'C',
        'Go',
        'Objective-C',
    ]
    hh_params = {
        'text': '',
        'search_field': 'name',
        'area': 1,
        'only_with_salary': True,
    }
    for language in languages:
        hh_params['text'] = f'Программист {language}'
        hh_vacancies = get_hh_vacancies(hh_params)
        if hh_vacancies['found'] > 100:
            hh_vacancy_statistic = get_vacancy_statistic(hh_vacancies['items'], predict_rub_salary_hh)
            hh_vacancies_statistic[language] = {}
            hh_vacancies_statistic[language]['vacancies_found'] = hh_vacancies['found']
            hh_vacancies_statistic[language]['vacancies_processed'] = hh_vacancy_statistic['vacancies_processed']
            hh_vacancies_statistic[language]['average_salary'] = hh_vacancy_statistic['average_salary']

    sj_params = {
        'town': 4,
        'catalogues': 48,
        'keywords[0][srws]': 1,
        'keywords[0][skwc]': 'and',
        'keywords[0][keys]': '',
    }
    for language in languages:
        sj_params['keywords[0][keys]'] = f'Программист {language}'
        sj_vacancies = get_superjob_vacancies(superjob_api_key, params=sj_params)
        if sj_vacancies['total'] > 0:
            sj_vacancy_statistic = get_vacancy_statistic(sj_vacancies['objects'], predict_rub_salary_sj)
            sj_vacancies_statistic[language] = {}
            sj_vacancies_statistic[language]['vacancies_found'] = sj_vacancies['total']
            sj_vacancies_statistic[language]['vacancies_processed'] = sj_vacancy_statistic['vacancies_processed']
            sj_vacancies_statistic[language]['average_salary'] = sj_vacancy_statistic['average_salary']

    hh_table = create_table('HH Moscow', hh_vacancies_statistic)
    sj_table = create_table('SuperJob Moscow', sj_vacancies_statistic)

    print(hh_table.table)
    print(sj_table.table)


if __name__ == '__main__':
    main()

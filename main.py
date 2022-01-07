import os

import requests

from dotenv import load_dotenv
from terminaltables import AsciiTable
from itertools import count


def request_hh_api(endpoint, params):
    url = f'https://api.hh.ru/{endpoint}'
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def request_superjob_api(method_name, api_key, params=None):
    url = f'https://api.superjob.ru/2.0/{method_name}'
    headers = {
        'X-Api-App-Id': api_key
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_superjob_vacancies(api_key, search_text, town, catalogues):
    vacancies = []
    vacancies_total = 0
    params = {
        'town': town,
        'catalogues': catalogues,
        'keywords[0][srws]': 1,
        'keywords[0][skwc]': 'and',
        'keywords[0][keys]': search_text,
    }
    for page in count(0):
        params['page'] = page
        page_response = request_superjob_api('vacancies', api_key, params)
        vacancies.extend(page_response['objects'])
        vacancies_total = page_response['total']
        if not page_response['more']:
            break

    return vacancies, vacancies_total


def get_hh_vacancies(search_text, search_field, area):
    vacancies = []
    vacancies_found = 0
    params = {
        'text': search_text,
        'search_field': search_field,
        'area': area,
    }
    for page in count(0):
        params['page'] = page
        page_response = request_hh_api('vacancies', params)
        vacancies.extend(page_response['items'])
        vacancies_found = page_response['found']
        if page >= page_response['pages']:
            break

    return vacancies, vacancies_found


def predict_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return None
    if not salary_from:
        return salary_to * 0.8
    if not salary_to:
        return salary_from * 1.2
    return (salary_from + salary_to) / 2


def predict_rub_salary_hh(vacancy):
    salary = vacancy['salary']
    if not salary or salary['currency'] != 'RUR':
        return None
    return predict_salary(salary['from'], salary['to'])


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def get_vacancy_statistic(vacancies, predict_salary_func):
    vacancies_processed = 0
    vacancy_salaries = []
    average_salary = 0
    for vacancy in vacancies:
        salary = predict_salary_func(vacancy)
        if salary:
            vacancy_salaries.append(salary)
            vacancies_processed += 1

    if vacancies_processed:
        average_salary = sum(vacancy_salaries) // vacancies_processed

    return vacancies_processed, average_salary


def get_hh_language_statistic(language, area):
    hh_vacancies, hh_vacancies_found = get_hh_vacancies(
        f'Программист {language}',
        'name',
        area
    )
    hh_vacancies_processed, hh_average_salary = get_vacancy_statistic(hh_vacancies, predict_rub_salary_hh)
    language_statistic = {
        'vacancies_found': hh_vacancies_found,
        'vacancies_processed': hh_vacancies_processed,
        'average_salary': hh_average_salary,
    }
    return language_statistic


def get_sj_language_statistic(language, area, industry, api_key):
    sj_vacancies, sj_vacancies_total = get_superjob_vacancies(
        api_key,
        f'Программист {language}',
        area,
        industry
    )
    sj_vacancies_processed, sj_average_salary = get_vacancy_statistic(sj_vacancies, predict_rub_salary_sj)
    language_statistic = {
        'vacancies_found': sj_vacancies_total,
        'vacancies_processed': sj_vacancies_processed,
        'average_salary': sj_average_salary,
    }
    return language_statistic


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
    hh_areas = {
        'Moscow': 1,
    }
    sj_areas = {
        'Moscow': 4,
    }
    sj_industries = {
        'Development, programming': 48,
    }
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
    for language in languages:
        hh_vacancies_statistic[language] = get_hh_language_statistic(
            language,
            hh_areas['Moscow']
        )
        sj_vacancies_statistic[language] = get_sj_language_statistic(
            language,
            sj_areas['Moscow'],
            sj_industries['Development, programming'],
            superjob_api_key
        )

    hh_table = create_table('HH Moscow', hh_vacancies_statistic)
    sj_table = create_table('SuperJob Moscow', sj_vacancies_statistic)

    print(hh_table.table)
    print(sj_table.table)


if __name__ == '__main__':
    main()

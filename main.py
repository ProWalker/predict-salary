import requests


def hh_api_request(endpoint, params):
    url = f'https://api.hh.ru/{endpoint}'
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_vacancies(search_text, area=113):
    page_response = {}
    vacancies = []
    params = {
        'text': search_text,
        'search_field': 'name',
        'area': area,
        'only_with_salary': True,
        'page': 0
    }
    pages_number = 1
    while params['page'] < pages_number:
        page_response = hh_api_request('vacancies', params)
        vacancies.extend(page_response['items'])
        pages_number = page_response['pages']
        params['page'] += 1

    page_response['items'] = vacancies

    return page_response


def predict_rub_salary(vacancy):
    salary = vacancy['salary']
    if salary['currency'] == 'RUR':
        if salary['from'] is None:
            return salary['to'] * 0.8
        if salary['to'] is None:
            return salary['from'] * 1.2
        return (salary['from'] + (salary['to'])) / 2
    return None


# def get_hh_vacancies_statistic(languages):
#     hh_vacancies_statistic = {}
#     for language in languages:
#         hh_vacancies = get_vacancies(f'Программист {language}', areas['Moscow'])
#         if hh_vacancies['found'] >= 100:
#             hh_vacancies_statistic[language] = {}
#             hh_vacancies_statistic[language]['vacancies_found'] = hh_vacancies['found']
#             vacancies_processed = 0
#             vacancy_rub_salaries = []
#             for vacancy in hh_vacancies['items']:
#                 rub_salary = predict_rub_salary(vacancy)
#                 if rub_salary is not None:
#                     vacancy_rub_salaries.append(rub_salary)
#                     vacancies_processed += 1
#
#             hh_vacancies_statistic[language]['vacancies_processed'] = vacancies_processed
#             vacancy_rub_salaries.sort()
#             mid_index = int(len(vacancy_rub_salaries) / 2)
#             hh_vacancies_statistic[language]['average_salary'] = vacancy_rub_salaries[mid_index]


def main():
    hh_vacancies_statistic = {}
    areas = {
        'Moscow': 1,
    }
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

    # for language in languages:
    #     hh_vacancies = get_vacancies(f'Программист {language}', areas['Moscow'])
    #     if hh_vacancies['found'] >= 100:
    #         hh_vacancies_statistic[language] = {}
    #         hh_vacancies_statistic[language]['vacancies_found'] = hh_vacancies['found']
    #         vacancies_processed = 0
    #         vacancy_rub_salaries = []
    #         for vacancy in hh_vacancies['items']:
    #             rub_salary = predict_rub_salary(vacancy)
    #             if rub_salary is not None:
    #                 vacancy_rub_salaries.append(rub_salary)
    #                 vacancies_processed += 1
    #
    #         hh_vacancies_statistic[language]['vacancies_processed'] = vacancies_processed
    #         vacancy_rub_salaries.sort()
    #         mid_index = int(len(vacancy_rub_salaries) / 2)
    #         hh_vacancies_statistic[language]['average_salary'] = vacancy_rub_salaries[mid_index]
    #
    # print(hh_vacancies_statistic)


if __name__ == '__main__':
    main()


import urllib.parse
from config import proxy
import requests as req
from bs4 import BeautifulSoup
from functools import cache

base_url = 'https://home.mephi.ru'
urls = [f'https://home.mephi.ru/study_groups?level={i}&organization_id={j}&term_id=16'
        for i in range(5) for j in (1, 2, 12)] + ['https://home.mephi.ru/study_groups?organization_id=2&term_id=16']

session = req.Session()
session.proxies = {proxy}


def get_group_url(group_num: str) -> str:
    for url in urls:
        resp = session.get(url)
        soup = BeautifulSoup(resp.text, 'html5lib')
        a = soup.find('a', text=lambda t: t and t.startswith(group_num))
        if a:
            ret_url = urllib.parse.urljoin(base_url, a['href'])
            return ret_url
    return ""


@cache
def get_lesson_day(url: str) -> dict:
    if 'date=' not in url:
        url = urllib.parse.urljoin(url, 'day')
    schedule = {}
    resp = session.get(url)
    soup = BeautifulSoup(resp.text, 'html5lib')

    wrapper = soup.body.find('div', id='wrapper')
    content_wrapper = wrapper.find('div', id='page-content-wrapper').div

    if content_wrapper.contents[13].text == 'Занятий не найдено':
        schedule['header'] = 'Занятий не найдено'
        schedule['lessons'] = []
        return schedule

    schedule_block = content_wrapper.find_all('div', attrs={'id': '', 'class': ''})[1]

    schedule['header'] = schedule_block.h3.contents[2][1:-1]
    schedule['lessons'] = []

    for les in schedule_block.div.children:
        if les.name is None:
            continue

        lesson_dict = {
            'time': les.find('div', attrs={'class': 'lesson-time'}).text.replace(' ', '').replace(' ', ''),
            'name': les.find('div', attrs={'class': 'lesson-lessons'}).div.div.contents[6][1:-1],
            'type': les.find('div', attrs={'class': 'label label-default label-lesson'}).text
        }
        lecture = les.find(
            'div', attrs={'class': 'lesson-lessons'}).div.div.find('span', attrs={'class': 'text-nowrap'})
        lesson_dict['lecture'] = None if lecture is None else lecture.a.text.replace(' ', ' ')
        lesson_dict['audience'] = ''
        if '>' in str(les.find('div', attrs={'class': 'pull-right'}).a):
            lesson_dict['audience'] = str(les.find(
                'div', attrs={'class': 'pull-right'}).a).split('>')[1].replace('</a', '')

        schedule['lessons'].append(lesson_dict)

    return schedule


# @cache
# def get_all_lessons_days(url: str) -> list:
#     schedule = []
#     day = {}
#     resp = session.get(url)
#     soup = BeautifulSoup(resp.text, 'html5lib')
#
#     wrapper = soup.body.find('div', id='wrapper')
#     content_wrapper = wrapper.find('div', id='page-content-wrapper').div
#
#     if content_wrapper.contents[13].text == 'Занятий не найдено':
#         day['header'] = 'Занятий не найдено'
#         day['lessons'] = []
#         schedule.append(day)
#         return schedule
#     contents = [content_wrapper.find_all('div', attrs={'id': '', 'class': 'lesson-was'}),
#                 content_wrapper.find_all('div', attrs={'id': '', 'class': ''})]
#     for content in contents:
#         for schedule_block in content:
#             if '\n' in str(schedule_block.h3):
#                 day['header'] = str(schedule_block.h3).split('\n')[2]
#             day['lessons'] = []
#             for les in schedule_block.find_all('div', attrs={'id': '', 'class': 'list-group-item'}):
#                 if les.name is None:
#                     continue
#                 lesson_dict = {
#                     'time': les.find('div', attrs={'class': 'lesson-time'}).text.replace(' ', '').replace(' ', ''),
#                     'name': les.find('div', attrs={'class': 'lesson-lessons'}).div.div.contents[6][1:-1],
#                     'type': les.find('div', attrs={'class': 'label label-default label-lesson'}).text
#                 }
#                 lecture = les.find(
#                     'div', attrs={'class': 'lesson-lessons'}).div.div.find('span', attrs={'class': 'text-nowrap'})
#                 lesson_dict['lecture'] = None if lecture is None else lecture.a.text.replace(' ', ' ')
#                 day['lessons'].append(lesson_dict)
#             if day['lessons']:
#                 schedule.append(day)
#                 day = {}
#     return schedule


@cache
def get_all_lessons_days(url: str) -> list:
    schedule = []
    day = {}
    resp = session.get(url)
    soup = BeautifulSoup(resp.text, 'html5lib')

    wrapper = soup.body.find('div', id='wrapper')
    content_wrapper = wrapper.find('div', id='page-content-wrapper').div

    if content_wrapper.contents[13].text == 'Занятий не найдено':
        day['header'] = 'Занятий не найдено'
        day['lessons'] = []
        return schedule
    contents = [content_wrapper.find_all('div', attrs={'id': '', 'class': 'lesson-was'}),
                content_wrapper.find_all('div', attrs={'id': '', 'class': ''})]
    for content in contents:
        for schedule_block in content:
            if '\n' in str(schedule_block.h3):
                day['header'] = str(schedule_block.h3).split('\n')[2]
            day['lessons'] = []
            for les in schedule_block.find_all('div', attrs={'id': '', 'class': 'list-group-item'}):
                if les.name is None:
                    continue
                lesson_dict = {
                    'time': les.find('div', attrs={'class': 'lesson-time'}).text.replace(' ', '').replace(' ', ''),
                    'name': les.find('div', attrs={'class': 'lesson-lessons'}).div.div.contents[6][1:-1],
                    'type': les.find('div', attrs={'class': 'label label-default label-lesson'}).text
                    if les.find('div', attrs={'class': 'label label-default label-lesson'}) else ''
                }
                lecture = les.find(
                    'div', attrs={'class': 'lesson-lessons'}).div.div.find('span', attrs={'class': 'text-nowrap'})
                lesson_dict['lecture'] = None if lecture is None else lecture.a.text.replace(' ', ' ')
                lesson_dict['audience'] = ''
                if les.find('div', attrs={'class': 'pull-right'}).span:
                    lesson_dict['audience'] = les.find('div', attrs={'class': 'pull-right'}).span.text
                elif '>' in str(les.find('div', attrs={'class': 'pull-right'}).a):
                    lesson_dict['audience'] = str(les.find(
                        'div', attrs={'class': 'pull-right'}).a).split('>')[1].replace('</a', '')
                day['lessons'].append(lesson_dict)
            if day['lessons']:
                schedule.append(day)
                day = {}

    return schedule


@cache
def normalize_lesson_day(url: str, info: str) -> str:
    schedule = get_lesson_day(url)

    msg = '\n'.join((
        f'Расписание на {info}:\n\n*{schedule["header"]}*\n',
        *[f'Пара №{index + 1} (*{les["time"]}*) *{les["name"]}* ({les["type"]})\n'
          f'{"_" + les["lecture"] + "_" if les["lecture"] else ""} {les["audience"]}\n'
          for index, les in enumerate(schedule['lessons'])]
    ))
    return msg


@cache
def normalize_week_lesson_days(url: str, offset: int, info: str) -> str:
    url = url.replace('/schedule', f'/week?offset={offset}/')
    schedule = get_all_lessons_days(url)
    msg = [f'Расписание на {info}:']
    for day in schedule:
        msg.extend([f'\n\n*{day["header"]}*\n'])
        msg.extend([f'\nПара №{index + 1} (*{les["time"]}*) {les["name"]} ({les["type"]})\n'
                    f'{"_" + les["lecture"] + "_" if les["lecture"] else ""} {les["audience"]}\n'
                    for index, les in enumerate(day['lessons'])])
    return ''.join(msg).strip()


if __name__ == '__main__':
    # print(get_group_url('с22-701'))
    print(get_all_lessons_days('https://home.mephi.ru/study_groups/15242/week?offset=1'))
    # get_all_lessons_days(get_week_lesson_days('https://home.mephi.ru/study_groups/15242/schedule', 1, 'lol'))

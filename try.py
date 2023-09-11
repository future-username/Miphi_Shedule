from app import get_group_url
import urllib.parse
import requests as req
from bs4 import BeautifulSoup

base_url = 'https://home.mephi.ru'

responses = {}

session = req.Session()


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
                }
                lecture = les.find(
                    'div', attrs={'class': 'lesson-lessons'}).div.div.find('span', attrs={'class': 'text-nowrap'})
                lesson_dict['lecture'] = None if lecture is None else lecture.a.text.replace(' ', ' ')
                day['lessons'].append(lesson_dict)
            if day['lessons']:
                schedule.append(day)
                day = {}

    return schedule


def get_week_lesson_days(url: str) -> str:
    schedule = get_all_lessons_days(url)
    msg = ''
    for day in schedule:
        msg_lines = [
            f'\n*{day["header"]}*\n\n',
            *[f'*{les["time"]}* {les["name"]} {"_" + les["lecture"] + "_" if les["lecture"] else ""}\n' for les in
              day['lessons']]
        ]
        msg += ''.join(msg_lines)
    return msg.strip()


print(get_week_lesson_days('https://home.mephi.ru/study_groups/15242/week?offset=1/'))
# get_lesson_day()

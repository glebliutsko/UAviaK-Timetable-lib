from . import Lesson

import requests
import operator
from bs4 import BeautifulSoup
import datetime


class Timetable:
    URL_TIMETABLE = 'http://www.uaviak.ru/pages/raspisanie-/'

    def __init__(self):
        self.lessons = []
        self.date = None

    def find(self, **kwargs):
        tb = Timetable()

        for lesson in self.lessons:
            for attr in kwargs:
                if getattr(lesson, attr) == kwargs[attr]:
                    tb.append_lesson(lesson)

        return tb

    def sort(self, attr: str = 'number', reverse: bool = False):
        self.lessons.sort(key=operator.attrgetter(attr), reverse=reverse)

    def list(self, fild):
        if not fild in Lesson.ATTR:
            raise ValueError('Not found fild')

        value_filds = set()
        for lesson in self.lessons:
            value_filds.add(getattr(lesson, fild))

        return list(value_filds)

    def append_lesson(self, lesson: Lesson or str or list):
        if isinstance(lesson, Lesson):
            self.lessons.append(lesson)
        elif isinstance(lesson, str) or isinstance(lesson, list):
            self.lessons.append(Lesson.parse_line(lesson))
        else:
            raise TypeError()

    def _parse_date(self, str_with_date: str or list):
        if isinstance(str_with_date, str):
            str_with_date = str_with_date.split()

        # Строка с датой может быть 2 форматов, с предлогом "на", пример
        #     Расписание на 01.01.1970
        # и без
        #     Расписание 01.01.1970
        if 'на' in str_with_date:
            str_with_date.remove('на')

        split_date = str_with_date[1].split('.')
        date = datetime.date(day=int(split_date[0]), month=int(split_date[1]), year=int(split_date[2]))
        if self._is_new_date(date):
            self.date = date

    def _is_new_date(self, date):
        return self.date is None or self.date < date

    @classmethod
    def is_lesson_line(cls, line: str or list):
        if isinstance(line, str):
            line = line.split()
        if len(line) == 0:
            return False

        return len(line[0]) >= 2 and line[0][:2].isnumeric() and line[0][-1] != ','

    @classmethod
    def load(cls):
        result = requests.get(Timetable.URL_TIMETABLE)

        soap = BeautifulSoup(result.text, "html.parser")
        soap_timetable = soap.find_all(class_='scrolling-text')[1:]

        table_text = ''
        for i in soap_timetable:
            i.find(class_='title').extract()
            table_text += i.get_text()

        return cls.__parse_text(table_text)

    @classmethod
    def __parse_text(cls, text: str):
        tb = cls()
        lines = text.splitlines()

        for line in lines:
            split_line = line.split()
            if len(split_line) == 0:
                continue

            if split_line[0] == 'Расписание':
                tb._parse_date(split_line)
            elif cls.is_lesson_line(split_line):
                tb.append_lesson(split_line)

        return tb

    def __getitem__(self, item):
        return self.lessons[item]

    def __len__(self):
        return len(self.lessons)

    def __str__(self):
        return str(self.lessons)

    def __repr__(self):
        return str(self.lessons)
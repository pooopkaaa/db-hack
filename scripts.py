import os
import sys
import argparse
import random
import django
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from datacenter.models import Schoolkid, Mark, Chastisement,\
                              Lesson, Commendation, Subject

COMMENDATION_TEXTS = [
    'Молодец!',
    'Отлично!',
    'Хорошо!',
    'Гораздо лучше, чем я ожидал!',
    'Ты меня приятно удивил!',
    'Великолепно!',
    'Прекрасно!',
    'Ты меня очень обрадовал!',
    'Именно этого я давно ждал от тебя!',
    'Сказано здорово – просто и ясно!',
    'Ты, как всегда, точен!',
    'Очень хороший ответ!',
    'Талантливо!',
    'Ты сегодня прыгнул выше головы!',
    'Я поражен!',
    'Уже существенно лучше!',
    'Потрясающе!',
    'Замечательно!',
    'Прекрасное начало!',
    'Так держать!',
    'Ты на верном пути!',
    'Здорово!',
    'Это как раз то, что нужно!',
    'Я тобой горжусь!',
    'С каждым разом у тебя получается всё лучше!',
    'Мы с тобой не зря поработали!',
    'Я вижу, как ты стараешься!',
    'Ты растешь над собой!',
    'Ты многое сделал, я это вижу!',
    'Теперь у тебя точно все получится!',
]


def get_schoolkid(name):
    return Schoolkid.objects.get(full_name__contains=name)


def check_subject_for_year_of_study(schoolkid_year_of_study, subject):
    return Subject.objects.get(title=subject,
                               year_of_study=schoolkid_year_of_study)


def fix_marks(schoolkid):
    Mark.objects.filter(schoolkid=schoolkid,
                        points__lt=4)\
                        .update(points=5)
    return 'Оценки исправлены для -> {} из {} {} класса'.format(
            schoolkid.full_name,
            schoolkid.year_of_study,
            schoolkid.group_letter)


def remove_chastisements(schoolkid):
    Chastisement.objects.filter(schoolkid=schoolkid).delete()
    return 'Жалобы удалены для -> {} из {} {} класса'.format(
            schoolkid.full_name,
            schoolkid.year_of_study,
            schoolkid.group_letter)


def create_commendation(schoolkid, schoolkid_subject):
    schoolkid_subject_lesson = Lesson.objects.filter(
            year_of_study=schoolkid.year_of_study,
            group_letter=schoolkid.group_letter,
            subject__title=schoolkid_subject)\
            .order_by('?')\
            .first()
    Commendation.objects.create(
            text=random.choice(COMMENDATION_TEXTS),
            created=schoolkid_subject_lesson.date,
            schoolkid=schoolkid,
            teacher=schoolkid_subject_lesson.teacher,
            subject=schoolkid_subject_lesson.subject)
    return 'Похвала по предмету {} добавлена для -> {} из {} класса'.format(
            schoolkid_subject,
            schoolkid.full_name,
            schoolkid.year_of_study,
            schoolkid.group_letter)


def get_command_line_args():
    parser = argparse.ArgumentParser(
            description='Помогаем изменять значения в базе \
                        данных электронного дневника')
    parser.add_argument('-n',
                        '--name',
                        type=str,
                        required=True,
                        help='Укажите имя и фамилию ученика')
    parser.add_argument('-s',
                        '--subject',
                        required=True,
                        help='Укажите название предмета за который \
                        хотите получить похвалу')
    return parser.parse_args()


def main():
    try:
        args = get_command_line_args()
        schoolkid = get_schoolkid(args.name)
        print(fix_marks(schoolkid))
        print(remove_chastisements(schoolkid))
        check_subject_for_year_of_study(
                schoolkid.year_of_study,
                args.subject)
        print(create_commendation(schoolkid, args.subject))
    except Schoolkid.DoesNotExist:
        print('Ошибка: Ученика с таким именем не существует. '
              'Исправьте имя ученика...')
    except Schoolkid.MultipleObjectsReturned:
        print('Ошибка: Учеников с таким именем много. Уточните имя ученика...')
    except Subject.DoesNotExist:
        print('Ошибка: Такого предмета у заданного ученика не существует. '
              'Исправьте название предмета...')


if __name__ == '__main__':
    main()

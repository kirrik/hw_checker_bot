import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status != 'approved':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=params)
        return homework_statuses.json()

    except Exception as e:
        print(f'Что-то не так с запросом. Ошибка: {e}')


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            homeworks = new_homework.get('homeworks', [])
            current_timestamp = new_homework.get(
                'current_date', int(time.time()))
            if homeworks:
                send_message(parse_homework_status(homeworks[0]))
            time.sleep(300)

        except KeyError as err:
            print(f'Ключ не найден в списке ДЗ. Ошибка: {err}')

        except KeyboardInterrupt:
            print(f'Вы прервали выполнение программы.')
            os.abort()

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(60)


if __name__ == '__main__':
    main()

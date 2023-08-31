import telebot
from telebot import types
import psycopg2
from config import host, user, password, db_name, token


bot = telebot.TeleBot(token)


def connect():
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name,
    )
    return connection


def is_correct_user(head, from_user):
    try:
        connect()

        with connect().cursor() as cursor:
            cursor.execute(
                f"SELECT name FROM public.heads WHERE name = '{head}'"
            )
            if cursor.fetchone() is not None:
                return True

    except Exception as _ex:
        print('[INFO] Error with PSQL:', _ex)

    finally:
        connect().close()
        print('[INFO] PSQL connection closed')


def process(head, from_user):
    try:
        connect()

        with connect().cursor() as cursor:
            cursor.execute(
                f'SELECT * FROM public.{head}'
            )
            data = cursor.fetchall()
            for row in data:
                if row[1] is not None:
                    bot.send_message(from_user, f'У пользователя {row[0]} ЭЦП кончается {row[1]}')
                else:
                    bot.send_message(from_user, f'У пользователя {row[0]} нет ЭЦП!')

    except Exception as _ex:
        print('[INFO] Error with PSQL:', _ex)

    finally:
        connect().close()
        print('[INFO] PSQL connection closed')



@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bot.send_message(message.from_user.id, "👋 Здравствуйте! Пожалуйста, введите Вашу фамилию, чтобы я смог помочь.", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if is_correct_user(message.text, message.from_user.id):
        process(message.text, message.from_user.id)

bot.infinity_polling(timeout=10, long_polling_timeout = 5)

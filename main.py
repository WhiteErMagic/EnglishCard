
import random

from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
from DataBase import DataBase
import os


known_users = []
userStep = {}

state_storage = StateMemoryStorage()
token_bot = os.getenv('TOKENBOT')
bot = TeleBot(token_bot, state_storage=state_storage)
print('Start telegram bot...')


class Command:
    ADD_WORD = 'Добавить слово ➕'
    CANCEL = 'Отмена'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class UserSteps:
    ADD_WORD = 1
    ADD_TRANSLATE = 2
    DELETE_WORD = 3
    START = 0


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = UserSteps.START
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    cid = message.chat.id
    if cid not in known_users:
        known_users.append(cid)
        userStep[cid] = UserSteps.START
        bot.send_message(cid, "Hello, stranger, let study English...")
    markup = types.ReplyKeyboardMarkup(row_width=2)

    buttons = []
    target_word = data_base.select_word(cid)
    translate = data_base.select_translation(target_word, cid)
    others = data_base.select_examples(cid, target_word)
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)

    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    cid = message.chat.id
    userStep[cid] = UserSteps.DELETE_WORD
    next_btn = types.KeyboardButton(Command.NEXT)
    cancel_add = types.KeyboardButton(Command.CANCEL)
    buttons = [next_btn, cancel_add]
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Отправьте слово для удаления', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    cid = message.chat.id
    userStep[cid] = UserSteps.ADD_WORD
    next_btn = types.KeyboardButton(Command.NEXT)
    cancel_add = types.KeyboardButton(Command.CANCEL)
    buttons = [next_btn, cancel_add]
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Отправьте слово', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == Command.CANCEL)
def cancel(message):
    cid = message.chat.id
    userStep[cid] = UserSteps.START
    data_base.cancel()
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons = [next_btn, add_word_btn, delete_word_btn]
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Продолжаем', reply_markup=markup)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    cid = message.chat.id
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if userStep[cid] == UserSteps.ADD_WORD:
            data['target_word'] = text
            next_btn = types.KeyboardButton(Command.NEXT)
            cancel_add = types.KeyboardButton(Command.CANCEL)
            buttons = [next_btn, cancel_add]
            userStep[cid] = UserSteps.ADD_TRANSLATE
            markup.add(*buttons)
            bot.send_message(message.chat.id, 'Перевод для ' + data['target_word'], reply_markup=markup)
        elif userStep[cid] == UserSteps.ADD_TRANSLATE:
            data_base.add_word(cid, data['target_word'], text)
            userStep[cid] = UserSteps.START
            next_btn = types.KeyboardButton(Command.NEXT)
            add_word_btn = types.KeyboardButton(Command.ADD_WORD)
            delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
            buttons = [next_btn, add_word_btn, delete_word_btn]
            markup = types.ReplyKeyboardMarkup(row_width=2)
            markup.add(*buttons)
            bot.send_message(message.chat.id, 'Слово добавлено', reply_markup=markup)
        elif userStep[cid] == UserSteps.DELETE_WORD:
            userStep[cid] = UserSteps.START
            data_base.delete_word(cid, text)
            next_btn = types.KeyboardButton(Command.NEXT)
            add_word_btn = types.KeyboardButton(Command.ADD_WORD)
            delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
            buttons = [next_btn, add_word_btn, delete_word_btn]
            markup = types.ReplyKeyboardMarkup(row_width=2)
            markup.add(*buttons)
            bot.send_message(message.chat.id, 'Продолжаем', reply_markup=markup)
        else:
            if text == target_word:
                hint = show_target(data)
                hint_text = ["Отлично!❤", hint]
                next_btn = types.KeyboardButton(Command.NEXT)
                add_word_btn = types.KeyboardButton(Command.ADD_WORD)
                delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
                buttons = [next_btn, add_word_btn, delete_word_btn]
                hint = show_hint(*hint_text)
            else:
                next_btn = types.KeyboardButton(Command.NEXT)
                add_word_btn = types.KeyboardButton(Command.ADD_WORD)
                delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
                buttons = [next_btn, add_word_btn, delete_word_btn]
                for btn in buttons:
                    if btn.text == text:
                        btn.text = text + '❌'
                        break
                hint = show_hint("Допущена ошибка!",
                                 f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")

            markup.add(*buttons)
            bot.send_message(message.chat.id, hint, reply_markup=markup)


if __name__ == '__main__':
    data_base = DataBase()
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling(skip_pending=True)
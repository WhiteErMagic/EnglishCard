import random

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
import os
from models import Words, Translation, StatusWords, create_tables


class DataBase:

    PASSWORD = os.getenv('PASSWORD')
    NAMEBASE = os.getenv('NAMEBASE')
    LOGIN = os.getenv('LOGIN')

    DSN = f'postgresql://{LOGIN}:{PASSWORD}@localhost:5432/{NAMEBASE}'
    engine = ''
    session = None

    def __init__(self):
        self.engine = sqlalchemy.create_engine(self.DSN)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.WORD_ADDED = 1
        self.WORD_DELETED = 0
        create_tables(self.engine, self.session)

    def select_translation(self, word, cid):
        """
            Получение перевода слова

            Args:
                word (str):  слово для перевода
                cid (ind): идентификатор пользователя

            Returns:
                str: перевод слова
        """
        # StatusWords для хранения признаков добавления и удаления пользователем
        # слов, что бы управлять отображением этих слов
        # первый запрос для слов, добавленных пользователем
        query1 = self.session.query(Words.word) \
            .select_from(Words) \
            .join(StatusWords,
                  Words.id == StatusWords.word_id) \
            .filter(StatusWords.id_user == cid) \
            .join(Translation, Translation.word_id == Words.id) \
            .filter(Translation.value == word)

        # второй запрос для слов, определенных вначале для всех пользователей
        query2 = self.session.query(Words.word) \
            .select_from(Words) \
            .join(StatusWords,
                  Words.id == StatusWords.word_id,
                  isouter=True) \
            .filter(StatusWords.word_id == None) \
            .join(Translation, Translation.word_id == Words.id) \
            .filter(Translation.value == word)

        result = query1.union(query2).all()
        for c in result:
            value = c[0]

        return value

    def select_word(self, cid):
        """
            Получение случайного слова

            Args:
                cid (ind): идентификатор пользователя

            Returns:
                str: слово
        """
        # StatusWords для хранения признаков добавления и удаления пользователем
        # слов, что бы управлять отображением этих слов
        # первый запрос для слов, добавленных пользователем
        query1 = self.session.query(Translation.id) \
            .select_from(Translation) \
            .join(StatusWords,
                  Translation.word_id == StatusWords.word_id) \
            .filter(StatusWords.id_user == cid and StatusWords.status == self.WORD_ADDED)

        # второй запрос для слов, определенных вначале для всех пользователей
        query2 = self.session.query(Translation.id) \
            .select_from(Translation) \
            .join(StatusWords,
                  Translation.word_id == StatusWords.word_id,
                  isouter=True) \
            .filter(StatusWords.id_user == None)

        result = query1.union(query2).all()
        index = random.choice(result)[0]

        query = self.session.query(Translation.value) \
            .select_from(Translation) \
            .filter(Translation.id == index)

        result = query[0][0]

        return result

    def session_close(self):
        self.session.close()

    def select_examples(self, cid, word):
        """
            Получение 4 варианта перевода слова

            Args:
                cid (ind): идентификатор пользователя
                word (str):  слово для перевода

            Returns:
                list: список из 4 переводов
        """
        examples = [word]

        # StatusWords для хранения признаков добавления и удаления пользователем
        # слов, что бы управлять отображением этих слов
        # первый запрос для слов, добавленных пользователем
        query1 = self.session.query(Translation.id) \
            .select_from(Translation) \
            .join(StatusWords,
                  Translation.word_id == StatusWords.word_id) \
            .filter(StatusWords.id_user == cid and StatusWords.status == self.WORD_ADDED
                    and Translation.value != word)

        # второй запрос для слов, определенных вначале для всех пользователей
        query2 = self.session.query(Translation.id) \
            .select_from(Translation) \
            .join(StatusWords,
                  Translation.word_id == StatusWords.word_id,
                  isouter=True) \
            .filter(Translation.value != word and StatusWords.id_user == None)

        result_id = query1.union(query2).all()

        ind = 4
        if len(result_id) < 4:
            ind = len(result_id)

        # 4 варианта для перевода
        while len(examples) < ind:
            x = random.choice(result_id)[0]
            query = self.session.query(Translation.value) \
                .select_from(Translation) \
                .filter(Translation.id == x)

            result = query.all()[0][0]
            if result not in examples:
                examples.append(result)

        return examples

    def add_word(self, cid, word, translate):
        """
            Добавляет новое слова

            Args:
                cid (ind): идентификатор пользователя
                word (str):  новое слово
                translate (str):  перевод
        """
        result = self.session.query(Words).filter(Words.word == word).all()

        if len(result) == 0:
            word_id = self.session.query(func.max(Words.id)).all()[0][0]
            if word_id != None:
                word_id += 1
            else:
                word_id = 1
            new_word = Words(id=word_id, word=word)
            self.session.add(new_word)

            translation_id = self.session.query(func.max(Translation.id)).all()[0][0]
            if translation_id != None:
                translation_id += 1
            else:
                translation_id = 1
            self.session.add(Translation(id=translation_id, word_id=new_word.id, value=translate))
        else:
            new_word = result[0]

        status_id = self.session.query(func.max(StatusWords.id)).all()[0][0]
        if status_id != None:
            status_id += 1
        else:
            status_id = 1
        self.session.add(StatusWords(id=status_id, word_id=new_word.id, id_user=cid, status=1))

        self.session.commit()

    def cancel(self):
        self.session.rollback()

    def delete_word(self, cid, word):
        """
            Удаляет слово

            Args:
                cid (ind): идентификатор пользователя
                word (str):  слово
        """
        result = self.session.query(Words).filter(Words.word == word).all()
        if len(result) > 0:
            word = result[0]
            self.session.query(StatusWords).filter(StatusWords.word_id == word.id
                                                       and StatusWords.id_user == cid).delete()
            self.session.commit()

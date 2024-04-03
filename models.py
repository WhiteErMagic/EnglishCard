import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Table, String, MetaData, insert

meta = MetaData()
Base = declarative_base()

class Words(Base):
    __tablename__ = 'words'

    id = sq.Column('id', sq.Integer, primary_key=True, autoincrement=True, nullable=True)
    word = sq.Column('word', sq.String(length=40), unique=True)

    translations = relationship('Translation', back_populates='words')
    status = relationship('StatusWords', back_populates='words')


class Translation(Base):
    __tablename__ = 'translation'

    id = sq.Column('id', sq.Integer, primary_key=True, autoincrement=True, nullable=True)
    word_id = sq.Column('word_id', sq.Integer, sq.ForeignKey('words.id'), nullable=False)
    value = sq.Column('value', sq.String(length=50), unique=True)

    words = relationship('Words', back_populates='translations')


class StatusWords(Base):
    __tablename__ = 'status_words'

    id = sq.Column('id', sq.Integer, primary_key=True, autoincrement=True, nullable=True)
    word_id = sq.Column('word_id', sq.Integer, sq.ForeignKey('words.id'), nullable=False)
    id_user = sq.Column('id_user', sq.Integer, nullable=False)
    status = sq.Column('status', sq.Integer, nullable=False)

    words = relationship('Words', back_populates='status')


def create_tables(engine, session):
    """
        Инициализирует таблицы

        Args:
            engine (engine): engine
            session (Session):  сессия
    """
    words = Table(
        'words', meta,
        sq.Column('id', sq.Integer, primary_key=True, autoincrement=True, nullable=True),
        sq.Column('word', String(40), unique=True),
    )

    translation = Table(
        'translation', meta,
        sq.Column('id', sq.Integer, primary_key=True, autoincrement=True, nullable=True),
        sq.Column('word_id', sq.Integer, sq.ForeignKey('words.id'), nullable=False),
        sq.Column('value', sq.String(length=50), unique=True),
    )

    status_words = Table(
        'status_words', meta,
        sq.Column('id', sq.Integer, primary_key=True, autoincrement=True, nullable=True),
        sq.Column('word_id', sq.Integer, sq.ForeignKey('words.id'), nullable=False),
        sq.Column('id_user', sq.Integer, nullable=False, index=True),
        sq.Column('status', sq.Integer, nullable=False),
    )

    meta.create_all(engine)
    q = session.query(Words)
    if len(q.all()) == 0:
        objects = []
        objects += [
            Words(id=1, word='Мир'),
            Words(id=2, word='Солнце'),
            Words(id=3, word='Улица'),
            Words(id=4, word='Город'),
            Words(id=5, word='Пирог'),
            Words(id=6, word='Погода'),
            Words(id=7, word='Лето'),
            Words(id=8, word='Снег'),
            Words(id=9, word='Мороженое'),
            Words(id=10, word='Корабль'),
            Translation(id=1, word_id=1, value='Peace'),
            Translation(id=2, word_id=2, value='Sun'),
            Translation(id=3, word_id=3, value='Streat'),
            Translation(id=4, word_id=4, value='Сity'),
            Translation(id=5, word_id=5, value='Pie'),
            Translation(id=6, word_id=6, value='Weather'),
            Translation(id=7, word_id=7, value='Summer'),
            Translation(id=8, word_id=8, value='Snow'),
            Translation(id=9, word_id=9, value='Ice cream'),
            Translation(id=10, word_id=10, value='Ship')
        ]

        session.bulk_save_objects(objects)
        session.commit()




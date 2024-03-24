import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

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
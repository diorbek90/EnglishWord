from .base import *

def init_db():
    if db.is_closed():
        db.connect()
    db.create_tables([Theme, Word])

def create_theme(theme):
    with db.connection_context():
        Theme.create(theme_name=theme)

def create_word(word, translated, id):
    with db.connection_context():
        Word.create(word=word, translated=translated, theme_id=id)

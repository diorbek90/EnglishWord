from .base import *
import random

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

def is_there_theme(theme):
    with db.connection_context():
        return Theme.select().where(Theme.theme_name == theme).exists() 
    
def delete_theme_by_id(theme_id):
    with db.connection_context():
        theme = Theme.get_by_id(theme_id)
        theme.delete_instance(recursive=True)
        
def delete_word_by_id(word_id):
    with db.connection_context():
        word = Word.get_by_id(word_id)
        word.delete_instance()
        
def get_random_theme_id():
    with db.connection_context():
        themes = list(Theme.select())
        if themes:
            return random.choice(themes).id
        return None
    
def get_random_word_and_translated_by_theme_id(theme_id):
    """it's function that returrns random word and its translated word by theme id"""
    with db.connection_context():
        words = list(Word.select().where(Word.theme_id == theme_id))
        if words:
            word = random.choice(words)
            return word.word, word.translated
        return None, None

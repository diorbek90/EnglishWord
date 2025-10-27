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
        

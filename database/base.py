from peewee import SqliteDatabase, Model, CharField, ForeignKeyField

db = SqliteDatabase("words.db")


class Theme(Model):
    
    theme_name = CharField()
    
    class Meta:
        database = db
        
class Word(Model):
    
    word = CharField()
    translated = CharField()
    theme = ForeignKeyField(Theme, backref="words")
    
    class Meta:
        database = db
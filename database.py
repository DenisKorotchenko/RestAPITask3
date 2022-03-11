from peewee import *


conn = SqliteDatabase('task3.sqlite')


class BaseDBModel(Model):
    class Meta:
        database = conn


class PromoDB(BaseDBModel):
    id = PrimaryKeyField(null=False)
    name = TextField(null=False)
    description = TextField(null=True)

    class Meta:
        table_name = 'promo'


class ParticipantDB(BaseDBModel):
    id = PrimaryKeyField(null=False)
    name = TextField(null=False)
    promo_id = ForeignKeyField(PromoDB, id)

    class Meta:
        table_name = 'participant'


class PrizeDB(BaseDBModel):
    id = PrimaryKeyField(null=False)
    description = TextField(null=False)
    promo_id = ForeignKeyField(PromoDB, id)

    class Meta:
        table_name = 'prize'


#conn.drop_tables([PromoDB, ParticipantDB, PrizeDB])
conn.create_tables([PromoDB, ParticipantDB, PrizeDB])


def close_db():
    conn.close()

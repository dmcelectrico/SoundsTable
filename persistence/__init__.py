import logging
import sqlite3
from telebot.types import User # FIXME: Create custom User

LOG = logging.getLogger('LaVidaModerna_Bot.persistence')

INTEGER = 'INTEGER'
TEXT = 'TEXT'
BOOLEAN = 'BOOLEAN'
default_column_type = TEXT  # E.g., INTEGER, TEXT, NULL, REAL, BLOB

""" |  id   |   filename    |   text    |   tags    |"""
"""  INTEGER      TEXT          TEXT        TEXT     """
sounds_table = 'sounds'
sounds_col_id = 'id'  # name of the PRIMARY KEY column
sounds_col_id_type = INTEGER
sounds_col_filename = 'filename'  # name of the new column
sounds_col_text = 'text'  # name of the new column
sounds_col_tags = 'tags'  # name of the new column
sounds_index_name = 'index_filename'

""" | id | is_bot | first_name | last_name | username | language_code | num_queries | num_results | """
"""   INT BOOLEAN       TEXT        TEXT        TEXT        TEXT           INTEGER      INTEGER     """
users_table = 'users'
users_col_id = 'id'
users_col_id_type = INTEGER
users_col_is_bot = 'is_bot'
users_col_is_bot_type = BOOLEAN
users_col_first_name = 'first_name'
users_col_last_name = 'last_name'
users_col_username = 'username'
users_col_language_code = 'language_code'
users_col_num_queries = 'num_queries'
users_col_num_results = 'num_results'
users_col_num_type = INTEGER


class SqLite:

    def __init__(self, db_file):
        if not db_file:
            db_file = 'db.sqlite'
        LOG.debug('Persistence layer started: sqlite3')
        self.sqlite_file = db_file  # name of the sqlite database file

        # Connecting to the database file
        self.connection = sqlite3.connect(self.sqlite_file)
        self.cursor = self.connection.cursor()
        self.startup()

    def startup(self):
        tables = self.get_tables()
        LOG.debug('Tables currently in db: %s', str(tables))
        # Table checking
        if sounds_table not in tables:
            self.create_table_sounds()
        if users_table not in tables:
            self.create_table_users()

    def get_sounds(self):
        sql = 'SELECT * FROM {tn};'
        self.cursor.execute(sql.format(tn=sounds_table))
        result_set = self.cursor.fetchall()
        LOG.debug("get_sounds: Obtained: %d rows.", len(result_set))
        sounds = map_to_sounds(result_set)
        return sounds

    def get_sound(self, id=None, filename=None):
        sql = 'SELECT * FROM {tn} WHERE {query};'
        query = resolve_where(id, filename)
        self.cursor.execute(sql.format(tn=sounds_table, id=id, query=query))
        result_set = self.cursor.fetchall()
        sounds = map_to_sounds(result_set)
        return sounds

    def add_sound(self, id, filename, text, tags):
        LOG.info('Adding sound: %s %s', id, filename)
        self.cursor.execute('INSERT INTO {tn} VALUES ({id}, "{filename}", "{text}", "{tags}")'
                            .format(tn=sounds_table, id=id, filename=filename, text=text, tags=tags))
        self.commit()

    def delete_sound(self, sound):
        LOG.info('Deleting sound %s', str(sound))
        sql = 'DELETE FROM {tn} WHERE {query};'

        query = resolve_where_from_sound(sound)

        self.cursor.execute(sql.format(tn=sounds_table, query=query))
        self.commit()

    def add_or_update_user(self, user):
        users = self.get_user(user.id)
        if len(users) > 0:
            db_user = users[0]
            LOG.debug('User %s %s already exist.', user.id, user.username)
            if db_user != user:
                LOG.info('Updating user %s %s', db_user.id, db_user.username)
                sql = 'UPDATE {table_name} SET ' \
                      '{is_bot} = {is_bot_value}, ' \
                      '{first_name} = {first_name_value},' \
                      '{last_name} = {last_name_value},' \
                      '{username} = {username_value},' \
                      '{language_code} = {language_code_value}' \
                      'WHERE {id} = {id_value};'
            else:
                return None
        else:
            LOG.info('Adding user %s %s', user.id, user.username)
            sql = 'INSERT OR IGNORE INTO {table_name} ' \
                  '({id}, ' \
                  '{is_bot}, ' \
                  '{first_name}, ' \
                  '{last_name}, ' \
                  '{username}, ' \
                  '{language_code}) VALUES ' \
                  '({id_value}, ' \
                  '{is_bot_value},' \
                  '{first_name_value}' \
                  '{last_name_value}' \
                  '{username_value}' \
                  '{language_code_value}' \
                  ')'
        sql.format(table_name=users_table,
                   id=users_col_id, id_value=user.id,
                   is_bot=users_col_is_bot, is_bot_value=user.is_bot,
                   first_name=users_col_first_name, first_name_value=user.first_name,
                   last_name=users_col_last_name, last_name_value=user.last_name,
                   username=users_col_username, username_value=user.username,
                   language_code=users_col_language_code, language_code_value=user.language_code
                   )
        LOG.debug('Executing sql: %s', sql)
        self.cursor.execute(sql)

    def get_user(self, id=None, username=None):
        query_id = "id = '{id}' "
        query_username = "username = '{username}' "
        query = None
        if id and username:
            query = query_id + 'AND ' + query_username
        elif id:
            query = query_id
        elif username:
            query = query_username

        query = query.format(id=id, username=username)
        sql = 'SELECT * FROM {table_name} WHERE {query}'.format(table_name=users_table, query=query)
        LOG.debug('Executing sql: %s', sql)
        self.cursor.execute(sql)
        result_set = self.cursor.fetchall()
        users = map_to_users(result_set)
        return users

    def add_user_query(self):
        pass

    def add_user_result(self):
        pass

    def commit(self):
        self.connection.commit()

    def close(self):
        # Committing changes and closing the connection to the database file
        self.connection.commit()
        self.connection.close()

    def create_db(self):
        self.create_table_sounds()

    def upgrade_db(self):
        pass

    def get_tables(self):
        sql = 'SELECT name FROM sqlite_master WHERE type=\'table\';'
        self.cursor.execute(sql)
        tables = list(sum(self.cursor.fetchall(), ()))
        return tables

    def create_table_sounds(self):
        """ SOUND INDEX TABLE """
        LOG.info('Creating table %s', sounds_table)
        sounds_sql_create_table = 'CREATE TABLE {tn} ({id} {idft} PRIMARY KEY, \
                                {fn} {fnft}, \
                                {txt} {txtft}, \
                                {tags} {tagsft})'.format(tn=sounds_table,
                                                         id=sounds_col_id, idft=sounds_col_id_type,
                                                         fn=sounds_col_filename, fnft=default_column_type,
                                                         txt=sounds_col_text, txtft=default_column_type,
                                                         tags=sounds_col_tags, tagsft=default_column_type)
        sounds_sql_create_index = 'CREATE UNIQUE INDEX {iname} \
                                    ON {tn}({col});'.format(iname=sounds_index_name,
                                                            tn=sounds_table, col=sounds_col_filename)
        LOG.debug("Running query: %s", sounds_sql_create_table)
        self.cursor.execute(sounds_sql_create_table)

        LOG.debug("Running query: %s", sounds_sql_create_index)
        self.cursor.execute(sounds_sql_create_index)

    def create_table_users(self):
        """ User info table. """
        LOG.info('Creating table %s', users_table)
        users_sql_create_table = 'CREATE TABLE {table_name} ({id} {id_type} PRIMARY KEY,' \
            '{is_bot} {is_bot_type},' \
            '{first_name} {first_name_type},' \
            '{last_name} {last_name_type},' \
            '{username} {username_type},' \
            '{language_code} {language_code_type},' \
            '{num_queries} {num_queries_type},' \
            '{num_results} {num_results_type}' \
            ')'.format(table_name=users_table, id=users_col_id, id_type=users_col_id_type,
                       is_bot=users_col_is_bot, is_bot_type=users_col_is_bot_type,
                       first_name=users_col_first_name, first_name_type=default_column_type,
                       last_name=users_col_last_name, last_name_type=default_column_type,
                       username=users_col_username, username_type=default_column_type,
                       language_code=users_col_language_code, language_code_type=default_column_type,
                       num_queries=users_col_num_queries, num_queries_type=users_col_num_type,
                       num_results=users_col_num_results, num_results_type=users_col_num_type)
        LOG.debug("Running query: %s", users_sql_create_table)
        self.cursor.execute(users_sql_create_table)

    def create_table_query_history(self):
        """ TODO: User interaction activity history
        Data to store:
         - index PK INTEGER
         - user_id FK
         - from_group? Can I get this? BOOLEAN
         - timestamp TIMESTAMP
         - query text STRING
         - results INTEGER
        """
        pass

    def create_table_result_history(self):
        """ TODO: Sound result sent history
        Data to store:
         - index PK INTEGER
         - user_id FK
         - sound_id FK
         - to group? Can I get this? BOOLEAN
         - timestamp TIMESTAMP
        """
        pass


def map_to_sounds(result_set):
    sounds = []
    for row in result_set:
        sound = map_to_sound(row)
        sounds.append(sound)
    return sounds


def map_to_sound(row):
    """
       Mapper to sound object
    {
      "id": "12345678"
      "text": "La palanca de emergencia",
      "tags": "la palanca de emergencia julio",
      "filename": "laPalancaDeEmergencia.ogg"
    }
    """
    sound = dict()
    sound["id"] = str(row[0])
    sound["filename"] = row[1]
    sound["text"] = row[2]
    sound["tags"] = row[3]
    return sound


def map_to_users(result_set):
    users = []
    for row in result_set:
        user = map_to_user(row)
        users.append(user)
    return users


def map_to_user(row):
    """
       Mapper to User object
    {
        'id': 183712,
        'is_bot': False,
        'first_name': 'first name',
        'username': 'username',
        'last_name': None,
        'language_code': 'en-US'
    }
    """
    user = User(row[0], row[1], row[2],
                last_name=row[3], username=row[4], language_code=row[5], num_queries=row[6], num_results=row[7])
    return user


def resolve_where_from_sound(sound):
    id = None
    filename = None
    if 'id' in sound:
        id = sound['id']
    elif 'filename' in sound:
        filename = sound['filename']

    return resolve_where(id, filename)


def resolve_where(id, filename):
    query_id = "id = '{id}' "
    query_filename = "filename = '{filename}' "
    query = None
    if id and filename:
        query = query_id + 'AND ' + query_filename
    elif id:
        query = query_id
    elif filename:
        query = query_filename

    query = query.format(id=id, filename=filename)
    return query

import logging
from pony.orm import *

LOG = logging.getLogger('LaVidaModerna_Bot.persistence')
db = Database()


class Sound(db.Entity):
    id = PrimaryKey(int)
    filename = Required(str, index=True, unique=True)
    text = Required(str)
    tags = Required(str)
    uses = Required(int)


class User(db.Entity):
    id = PrimaryKey(int)
    is_bot = Required(bool)
    first_name = Required(str)
    last_name = Optional(str)
    username = Optional(str)
    language_code = Optional(str)
    num_queries = Required(int)
    num_results = Required(int)


class Database:

    def __init__(self, provider, filename=None, host=None, user=None, password=None, database_name=None, ):
        if provider == 'mysql':
            LOG.info('Starting persistence layer using MySQL on %s db: %s', host, database_name)
            LOG.debug('MySQL data: host --> %s, user --> %s, db --> %s, password empty --> %s',
                      host, user, database_name, str(password is None))
            db.bind(provider='mysql', host=host, user=user, passwd=password, db=database_name, create_db=True)
        elif provider == 'postgres':
            LOG.info('Starting persistence layer using PostgreSQL on %s db: %s', host, database_name, create_db=True)
            LOG.debug('PostgreSQL data: host --> %s, user --> %s, db --> %s, password empty --> %s',
                      host, user, database_name, str(password is None))
            db.bind(provider='postgres', host=host, user=user, password=password, database=database_name, create_db=True)
        elif filename is not None:
            LOG.info('Starting persistence layer on file %s using SQLite.', filename)
            db.bind(provider='sqlite', filename=filename, create_db=True)
        else:
            LOG.info('Starting persistence layer on memory using SQLite.')
            db.bind(provider='sqlite', filename=':memory:')

        db.generate_mapping(create_tables=True)

    @db_session
    def get_sounds(self):
        query = Sound.select()
        sounds = [{'id': sound.id, 'filename': sound.filename, 'text': sound.text, 'tags': sound.tags,
                   'uses': sound.uses} for sound in query]
        LOG.debug("get_sounds: Obtained: %s", str(sounds))
        return sounds

    @db_session
    def get_sound(self, id=None, filename=None):
        if not id:
            sound = Sound.get(filename=filename)
        else:
            sound = Sound.get(id=id, filename=filename)
        return sound

    @db_session
    def add_sound(self, id, filename, text, tags):
        LOG.info('Adding sound: %s %s', id, filename)
        Sound(id=id, filename=filename, text=text, tags=tags, uses=0)
        commit()

    @db_session
    def delete_sound(self, sound):
        LOG.info('Deleting sound %s', str(sound))
        Sound.get(filename=sound['filename']).delete()

    def add_or_update_user(self, user):
        pass

    def get_user(self, id=None, username=None):
       pass

    def add_user_query(self):
        pass

    def add_user_result(self):
        pass

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

import logging
import sqlite3

LOG = logging.getLogger('LaVidaModerna_Bot.persistence')

TABLE_SOUNDS = 'sounds'  # name of the table to be created


class SqLite:

    def __init__(self, db_file='db.sqlite'):
        LOG.debug('Persistence layer started: sqlite3')
        self.sqlite_file = db_file  # name of the sqlite database file

        # Connecting to the database file
        self.connection = sqlite3.connect(self.sqlite_file)
        self.cursor = self.connection.cursor()

    def startup(self):
        tables = self.get_tables()
        LOG.debug('Tables currently in db: %s', str(tables))
        # Table checking
        if 'sounds' not in tables:
            self.create_table_sounds()

    def get_sounds(self):
        sql = 'SELECT * FROM {tn};'
        self.cursor.execute(sql.format(tn=TABLE_SOUNDS))
        result_set = self.cursor.fetchall()
        LOG.debug("get_sounds: Obtained: %d rows.", len(result_set))
        sounds = map_to_sounds(result_set)
        return sounds

    def add_sound(self, id, filename, text, tags):
        LOG.info('Adding sound: %s %s', id, filename)
        self.cursor.execute('INSERT INTO {tn} VALUES ({id}, "{filename}", "{text}", "{tags}")' \
              .format(tn=TABLE_SOUNDS, id=id, filename=filename, text=text, tags=tags))
        self.commit()


    def delete_sound(self, id):
        LOG.info('Deleting sound %s', id)
        sql = 'DELETE FROM {tn} WHERE id = {id};'
        self.cursor.execute(sql.format(tn=TABLE_SOUNDS, id=id))
        self.commit()

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
        LOG.info('Creating table sounds')
        col_id = 'id'  # name of the PRIMARY KEY column
        col_id_type = 'INTEGER'
        col_filename = 'filename'  # name of the new column
        col_text = 'text'  # name of the new column
        col_tags = 'tags'  # name of the new column
        default_column_type = 'TEXT'  # E.g., INTEGER, TEXT, NULL, REAL, BLOB

        # Creating a new SQLite table with 1 column
        self.cursor.execute('CREATE TABLE {tn} ({id} {idft} PRIMARY KEY, \
                                {fn} {fnft}, \
                                {txt} {txtft}, \
                                {tags} {tagsft})'
                            .format(tn=TABLE_SOUNDS,
                                    id=col_id, idft=col_id_type,
                                    fn=col_filename, fnft=default_column_type,
                                    txt=col_text, txtft=default_column_type,
                                    tags=col_tags, tagsft=default_column_type))


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

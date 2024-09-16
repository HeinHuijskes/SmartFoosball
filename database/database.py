import os
from queries import *
from psycopg2.errors import InvalidCatalogName, ObjectInUse, UndefinedObject, UndefinedFunction

FILE_PATH = './sql/...'
EXTENSION = '.sql'
DATABASES = [sqlFile[:-4] for sqlFile in os.listdir(FILE_PATH) if sqlFile.endswith('.sql')]

def installDatabaseSQL(database, file_path, extension=EXTENSION):
    try:
        try:
            destroyDB(database)
            print(f'Dropped database "{database}"')
        except InvalidCatalogName:
            print(f'Did not drop database "{database}", it does not exist (yet).')

        createDB(database)
        print(f'Created database "{database}"')
        connection = connectDB(database=database)
        executeSQLFile(file_path + database + extension, connection)
        print(f'Added tables to database "{database}" from file "{database + extension}"')
    except ObjectInUse as error:
        print(f'Error, cannot establish connection, {error}')
    except (UndefinedFunction, UndefinedObject) as error:
        print(f'Error: An extension is likely missing. See the README for more info. Error details: {error}')


def installDatabasesSQL(databases, file_path, extension=EXTENSION):
    print(f'Intializing databases: {", ".join(DATABASES)}')
    for database in databases:
        installDatabaseSQL(database, file_path, extension)


installDatabasesSQL(DATABASES, FILE_PATH, EXTENSION)

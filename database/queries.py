import sys
sys.path.append('../SmartFoosball')

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import InvalidCatalogName

from env import HOST, PORT, STANDARD_DB, USER, PASSWORD

def connectDB(database=STANDARD_DB, user=USER, password=PASSWORD):
    '''Connect to a postgres database.\n
    Enter arguments to override settings in `./localenv.py`'''
    return psycopg2.connect(database=database, user=user, password=password, host=HOST, port=PORT)

def connect(user=USER, password=PASSWORD):
    '''Connect to postgres without a database.\n
    Enter arguments to override settings in `./localenv.py`'''
    return psycopg2.connect(user=user, password=password, host=HOST, port=PORT)

def checkDBConnection(connection):
    '''If no connection is given, return a new connection according to standard settings'''
    if connection == None:
        return connectDB()
    else:
        return connection

def executeSQL(SQL, connection=None, closeConnection=False):
    '''Execute SQL over a postgres connection'''
    connection = checkDBConnection(connection)
    cursor = connection.cursor()
    cursor.execute(SQL)
    connection.commit()
    cursor.close()
    if closeConnection:
        connection.close()

def executeSQLAutoCommit(SQL, connection, closeConnection=False):
    '''Execute SQL over a postgres connection with isolation level autocommit.\n
    Used for CREATE DATABASE and DROP DATABASE'''
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    executeSQL(SQL, connection, closeConnection)

def selectSQL(SQL, connection=None, closeConnection=False):
    '''Execute a SELECT statement and return the result'''
    connection = checkDBConnection(connection)
    cursor=connection.cursor()
    cursor.execute(SQL)
    rows = cursor.fetchall()
    connection.commit()
    cursor.close()
    if closeConnection:
        connection.close()
    return rows

def getForeignKeys(tableName, connection=None, closeConnection=False):
    connection = checkDBConnection(connection)
    SQL="""SELECT
        tc.table_name AS table_name,
        kcu.column_name AS column_name,
        ccu.table_name AS referenced_table,
        ccu.column_name AS referenced_column
    FROM
        information_schema.table_constraints AS tc
    JOIN
        information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
    JOIN
        information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
    WHERE
        tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_name = '""" + tableName + """';
    """
    return selectSQL(SQL, connection, closeConnection)

def getTables(connection=None, closeConnection=False):
    connection = checkDBConnection(connection)
    SQL="""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        ;"""
    return selectSQL(SQL, connection, closeConnection)

def getTableColumns(table, connection=None, closeConnection=False):
    '''Return the name and type of all columns in a table'''
    connection = checkDBConnection(connection)
    SQL="""
        SELECT column_name, data_type FROM information_schema.columns
        WHERE table_name = '""" + table + """'
        ORDER BY ordinal_position
        ;"""
    return selectSQL(SQL, connection, closeConnection)

def createDB(dbName, user=USER, password=PASSWORD):
    '''Create a new database'''
    SQL = "CREATE DATABASE " + dbName + ";"
    executeSQLAutoCommit(SQL, connect(user, password))

def forceCreateDB(dbName, user=USER, password=PASSWORD):
    '''Force create a database, drop any potential existing database with the same name'''
    try:
        destroyDB(dbName)
    except InvalidCatalogName:
        pass
    createDB(dbName, user, password)

def destroyDB(dbName, user=USER, password=PASSWORD):
    '''Drop a database. THIS DELETES ALL DATA IN IT.'''
    SQL = "DROP DATABASE " + dbName + ";"
    executeSQLAutoCommit(SQL, connect(user, password))

def createTable(tableName: str, fields: list[str], connection=None, closeConnection=False):
    '''Create a new table\n
        Parameters:
            `tableName: str` New table name\n
            `tableFields: [str]` New fields in SQL format (e.g. `["test_name VARCHAR (50)"]`)
    '''
    connection = checkDBConnection(connection)
    tableFields = ', '.join(fields)
    SQL="""
        CREATE TABLE public.""" + tableName + """ (
            """ + tableFields + """
        );"""
    executeSQL(SQL, connection, closeConnection)

def addTableColumn(tableName: str, column: str, connection=None, closeConnection=False):
    '''Add a new column to a given table'''
    connection = checkDBConnection(connection)
    SQL="""ALTER TABLE """ + tableName + """ ADD """ + column + """;"""
    executeSQL(SQL, connection, closeConnection)

def insertIntoTable(tableName: str, columns: list[str], values: list[str], connection=None, closeConnection=False):
    '''Insert values into a table\n
        Parameters:
            `tableName: str` Table name\n
            `columns: [str]` Array of column names\n
            `values: [str]` Array of values to insert, corresponding to the columns
    '''
    connection = checkDBConnection(connection)
    # Convert table and column arrays to the correct strings
    tableColumns = ', '.join(columns)
    tableValues = "','".join(values)
    SQL = """INSERT INTO """ + tableName + """ (""" + tableColumns + """) VALUES('""" + tableValues +"""')"""
    executeSQL(SQL, connection, closeConnection)

def executeSQLFile(filepath, connection=None, closeConnection=False):
    '''Execute an SQL script in a .sql file.\n
        Note: cannot create databases, since ISOLATION_LEVEL_AUTOCOMMIT is not set.
    '''
    connection = checkDBConnection(connection)
    SQL=open(filepath, "r").read()
    executeSQL(SQL, connection, closeConnection)
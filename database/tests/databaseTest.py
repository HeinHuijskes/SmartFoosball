import sys
sys.path.append('./src')

from database.queries import *

# Test values
DB_NAME = 'test_database'
TABLE_NAME = 'test_table'
TABLE_FIELDS = ["test_id SERIAL PRIMARY KEY", "test_name VARCHAR (50) UNIQUE NOT NULL"]
TABLE_COLUMNS = ['test_name']
TABLE_VALUES = ['This is a test value']
SQL = "SELECT * FROM " + TABLE_NAME + ";"

forceCreateDB(DB_NAME)
connection = connectDB(database=DB_NAME)

createTable(TABLE_NAME, TABLE_FIELDS, connection)
columns = getTableColumns(TABLE_NAME, connection)
print(f'Columns: {", ".join([column[0] for column in columns])}')

insertIntoTable(TABLE_NAME, TABLE_COLUMNS, TABLE_VALUES, connection)
result = selectSQL(SQL, connection)
print(f'test_name values: "{", ".join([res[1] for res in result])}"')
print(f'Foreign: {getForeignKeys(TABLE_NAME, connection, closeConnection=True)}')

destroyDB(DB_NAME)


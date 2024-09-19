import sys
sys.path.append('./src')

from psycopg2.errors import InvalidCatalogName

from queries import createDB, destroyDB
from DBObjects import Database

class PythonDatabase():
    def __init__(self, name) -> None:
        self.name = name
        try:
            destroyDB(name)
        except InvalidCatalogName:
            pass
        createDB(name)
    
    def get(self):
        return Database(self.name)

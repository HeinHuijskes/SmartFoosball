import sys
sys.path.append('./database')

from install import *
from queries import *

installDatabasesSQL(DATABASES, FILE_PATH, EXTENSION)

insertIntoTable('ballcoordinates', ['x', 'y', 'angle', 'magnitude'], ['4.20', '6.9', '180.180', '10.0'], closeConnection=True)
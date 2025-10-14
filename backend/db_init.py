import sqlite3

db_con = sqlite3.connect('parkingtracker.db')

cursor = db_con.cursor()
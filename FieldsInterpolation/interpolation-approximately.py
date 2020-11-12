# -*- coding: utf-8 -*-

from difflib import SequenceMatcher
import sqlite3
import re
import time

limit = float(input("Enter limit: "))
inter = int(input("Enter 1- to interpolate, 0-not connect: "))
nearest = int(input("Enter 1- to connect to nearest, 0-not connect: "))
db_file = input("File for interpolation: ")
table = input("Table's name for interpolation: ")
accurancy = float(input("Enter how much accurancy is: "))
acc_name = input("Enter name for accurancy calculation: ")
col = {}
d = input('Enter columna with their position by space like(name1=position1 name2=posiotion2): ').split(' ')
for i in d:
    i = i.split('=')
    col[i[0]] = int(i[1])
columns = list(col.keys())
columns.pop(-1)
nr_d = int(input("Enter columns position with houses numbers: "))
id_x, id_y = int(input('Enter position of x: ')), int(
    input('Enter position of y: '))


def create_connection(db_file):
    """ create a database connection to the SQLite database specified by db_file
    :param db_file: database file"""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return None


def fnd_num(string):
    try:
        pattern = re.compile('\\d+')
        tmp = pattern.search(string)
        if tmp:
            return int(pattern.search(string).group())
        else:
            return 0
    except:
        return 0


def make_str(obj):
    global table, columns, col
    string = ''
    for i in columns:
        string += f"{i} = \"{obj[col[i]]}\"  AND "
    string = string[:len(string)-5]
    return string


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def remove(al, obj, allnull, ids):
    global accurancy, col, nr_d
    lst = al[:]
    for i in al:
        if not fnd_num(i[nr_d]) or i[0] in ids:
            lst.remove(i)
        elif i[col[acc_name]] != None and obj[col[acc_name]] == None:
            lst.remove(i)
        elif i[col[acc_name]] == None and obj[col[acc_name]] != None:
            lst.remove(i)
        elif i[col[acc_name]] and obj[col[acc_name]]:
            if similar(i[col[acc_name]], obj[col[acc_name]]) < accurancy and i in lst:
                lst.remove(i)
        else:
            continue

    low_l = sorted(list(filter(lambda x: fnd_num(x[nr_d]) <= fnd_num(
        obj[nr_d]), lst)), key=lambda x: fnd_num(x[nr_d]), reverse=True)
    high_l = sorted(list(filter(lambda x: fnd_num(x[nr_d]) >= fnd_num(
        obj[nr_d]), lst)), key=lambda x: fnd_num(x[nr_d]))

    if not low_l:
        low_l = [0]
    if not high_l:
        high_l = [0]
    return low_l[0], high_l[0]


def fnd_sim(obj, cursor, al, allnull, ids):
    global limit, columns, table
    rowid = obj[0]
    if not fnd_num(obj[nr_d]):
        cursor.execute(
            f"UPDATE {table} SET INFO=\"No interpolation\" WHERE ROWID={rowid}")
        return 0

    obj_low, obj_high = remove(al, obj, allnull, ids)
    if not obj_high or not obj_low:
        cursor.execute(
            f"UPDATE {table} SET INFO=\"No interpolation\" WHERE ROWID={rowid}")
        return 0

    num_low = int(fnd_num(obj_low[nr_d]))
    num_high = int(fnd_num(obj_high[nr_d]))
    x_low, y_low = obj_low[id_x], obj_low[id_y]
    x_high, y_high = obj_high[id_x], obj_high[id_y]
    num = int(fnd_num(obj[nr_d]))
    num_avg = abs(num_high - num_low)

    if num_avg < limit:
        if obj_low == obj_high:
            x = (x_high + x_low)/2
            y = (y_high + y_low)/2
            cursor.execute(
                f"UPDATE {table} SET x={x},y={y},INFO=\"connect to {obj_low[nr_d]}\" WHERE ROWID={rowid}")
            return 0
        elif num == num_low:
            x = x_low
            y = y_low
            cursor.execute(
                f"UPDATE {table} SET x={x},y={y},INFO=\"connect to {obj_low[nr_d]}\" WHERE ROWID={rowid}")
            return 0
        elif num == num_high:
            x = x_high
            y = y_high
            cursor.execute(
                f"UPDATE {table} SET x={x},y={y},INFO=\"connect to {obj_high[nr_d]}\" WHERE ROWID={rowid}")
            return 0
        else:
            grt = num - num_low
            x = x_low + ((x_high - x_low)/num_avg * grt)
            y = y_low + ((y_high - y_low)/num_avg * grt)
            cursor.execute(
                f"UPDATE {table} SET x={x},y={y},INFO=\"interpolation btwn {obj_low[nr_d]} & {obj_high[nr_d]}\" WHERE ROWID={rowid}")
            return 0
    else:
        cursor.execute(
            f"UPDATE {table} SET INFO=\"No interpolation\" WHERE ROWID={rowid}")
        return 0


def sim_conn(obj, cursor, al, allnull, ids):
    global limit, columns, table
    rowid = obj[0]
    if not fnd_num(obj[nr_d]):
        cursor.execute(
            f"UPDATE {table} SET INFO=\"No interpolation\" WHERE ROWID={rowid}")
        return 0

    obj_low, obj_high = remove(al, obj, allnull, ids)

    if not obj_high and not obj_low:
        cursor.execute(
            f"UPDATE {table} SET INFO=\"Nothing\" WHERE ROWID={rowid}")
        return 0
    elif not obj_high:
        obj_high = obj_low
    elif not obj_low:
        obj_low = obj_high

    num_low = int(fnd_num(obj_low[nr_d]))
    num_high = int(fnd_num(obj_high[nr_d]))
    x_low, y_low = obj_low[id_x], obj_low[id_y]
    x_high, y_high = obj_high[id_x], obj_high[id_y]
    num = int(fnd_num(obj[nr_d]))

    if (abs(num - num_low) < limit) and (abs(num - num_low) <= abs(num - num_high)):
        x = x_low
        y = y_low
        cursor.execute(
            f"UPDATE {table} SET x={x},y={y},INFO=\"Connect to nearest {obj_low[nr_d]}\" WHERE ROWID={rowid}")
        return 0
    elif (abs(num - num_high) < limit) and (abs(num - num_high) < abs(num - num_low)):
        x = x_high
        y = y_high
        cursor.execute(
            f"UPDATE {table} SET x={x},y={y},INFO=\"Connect to nearest {obj_high[nr_d]}\" WHERE ROWID={rowid}")
        return 0
    else:
        cursor.execute(
            f"UPDATE {table} SET INFO=\"Over limit\" WHERE ROWID={rowid}")
        return 0


def interpol(db_file):
    global table, limit, columns
    conn = create_connection(db_file)
    cursor = conn.cursor()
    cursor.execute(f"ALTER TABLE {table} ADD COLUMN INFO TEXT;")
    cursor.execute(f"SELECT * FROM {table} WHERE x is NULL AND y is NULL;")
    allnull = cursor.fetchall()
    ids = [i[0] for i in allnull]
    print(len(allnull), ' to calculate;')
    for num, i in enumerate(allnull):

        if num % 100 == 0:
            cursor.commit()
            print(num)
        sql_low = f"SELECT *  FROM {table} WHERE (x is NOT NULL AND {make_str(i)});"
        cursor.execute(sql_low)
        al = cursor.fetchall()
        fnd_sim(i, cursor, al, allnull, ids)
    conn.commit()


def inter_conn(db_file):
    global table, limit, columns
    conn = create_connection(db_file)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE x is NULL AND y is NULL;")
    allnull = cursor.fetchall()
    print(len(allnull), ' to calculate;')
    ids = [i[0] for i in allnull]

    for num in allnull:
        if num % 100 == 0:
            cursor.commit()
            print('Making: ', num)
        sql_low = f"SELECT *  FROM {table} WHERE (x is NOT NULL AND {make_str(i)});"
        cursor.execute(sql_low)
        al = cursor.fetchall()
        sim_conn(i, cursor, al, allnull, ids)
    conn.commit()


start_time = time.time()
if __name__ == '__main__':
    print('Start')
    if inter:
        interpol(db_file)
    if nearest:
        inter_conn(db_file)
    print('Succesfully', time.time() - start_time)

# -*- coding: utf-8 -*-

import re
import sqlite3
import time

limit = int(input("Enter limit: "))
inter = int(input("Enter 1- to interpolate, 0-not connect: "))
nearest = int(input("Enter 1- to connect to nearest, 0-not connect: "))
db_file = input("File for interpolation: ")
table = input("Table's name for interpolation: ")
columns = input(
    "Enter columns names for checking(using space between): ").split()
hs_num = input("Enter column's name with houses numbers: ")
nr_d = int(input("Enter the position of column with houses numbers: "))


def create_connection(db_name):
    """ create a database connection to the SQLite database specified by db_file
    :param db_name: database file"""
    try:
        connection = sqlite3.connect(db_name)
        return connection
    except Exception as e:
        print(e)
    return None


def find_num(string):
    try:
        num = re.search('\\d+', string)
        if num:
            return int(num.group())
        else:
            return 0
    except:
        return 0


def make_str(rowid):
    global table, columns
    string = ''
    for i in columns:
        string += f"{i} IS (SELECT {i} FROM {table} WHERE ROWID={rowid}) AND "
    string = string[:len(string) - 5]
    return string


def sql_obj(rowid, cursor, lst):
    global limit, columns, table, hs_num, nr_d
    cursor.execute(f"SELECT {hs_num} FROM {table} WHERE ROWID={rowid};")
    num_st = str(cursor.fetchone()[0])
    num = find_num(num_st)

    sql_low = f"SELECT *  FROM {table} WHERE (CAST({hs_num} AS NUMERIC)<= (SELECT CAST(\"{num_st}\" AS NUMERIC)) AND x is NOT NULL AND {make_str(rowid)}) ORDER BY CAST({hs_num} AS NUMERIC) DESC LIMIT 1;"
    sql_high = f"SELECT *  FROM {table} WHERE (CAST({hs_num} AS NUMERIC) >= (SELECT CAST(\"{num_st}\" AS NUMERIC)) AND x is NOT NULL AND {make_str(rowid)}) ORDER BY CAST({hs_num} AS NUMERIC) ASC LIMIT 1;"

    notfind = True
    while notfind:
        cursor.execute(sql_low)
        obj_low = cursor.fetchone()
        cursor.execute(sql_high)
        obj_high = cursor.fetchone()

        if not obj_low or not obj_high:
            break
        elif obj_high[0] not in lst and obj_low[0] not in lst:
            break
        elif obj_high[0] not in lst and obj_low[0] in lst:
            notfind = True
            sql_low = f"SELECT *  FROM {table} WHERE (CAST({hs_num} AS NUMERIC)< (SELECT CAST(\"{obj_low[nr_d]}\" AS NUMERIC)) AND x is NOT NULL AND {make_str(rowid)}) ORDER BY CAST({hs_num} AS NUMERIC) DESC LIMIT 1;"
        elif obj_high[0] in lst and obj_low[0] not in lst:
            notfind = True
            sql_high = f"SELECT *  FROM {table} WHERE (CAST({hs_num} AS NUMERIC) > (SELECT CAST(\"{obj_high[nr_d]}\" AS NUMERIC)) AND x is NOT NULL AND {make_str(rowid)}) ORDER BY CAST({hs_num} AS NUMERIC) ASC LIMIT 1;"
        elif obj_high[0] in lst and obj_low[0] in lst:
            notfind = True
            sql_high = f"SELECT *  FROM {table} WHERE (CAST({hs_num} AS NUMERIC) > (SELECT CAST(\"{obj_high[nr_d]}\" AS NUMERIC)) AND x is NOT NULL AND {make_str(rowid)}) ORDER BY CAST({hs_num} AS NUMERIC) ASC LIMIT 1;"
            sql_low = f"SELECT *  FROM {table} WHERE (CAST({hs_num} AS NUMERIC)< (SELECT CAST(\"{obj_low[nr_d]}\" AS NUMERIC)) AND x is NOT NULL AND {make_str(rowid)}) ORDER BY CAST({hs_num} AS NUMERIC) DESC LIMIT 1;"
        else:
            break
    return obj_low, obj_high, num


def numberss(rowid, obj_low, obj_high, cursor):
    global hs_num, table
    cursor.execute(f"SELECT {hs_num} FROM {table} WHERE ROWID={obj_low[0]};")
    num_low = cursor.fetchone()[0]
    cursor.execute(f"SELECT {hs_num} FROM {table} WHERE ROWID={obj_high[0]};")
    num_high = cursor.fetchone()[0]
    return num_low, num_high


def fnd_coor(lst, obj, cursor):
    global limit, columns, table
    rowid = obj[0]
    obj_low, obj_high, num = sql_obj(rowid, cursor, lst)

    if not obj_high or not obj_low or not num:
        cursor.execute(
            f"UPDATE {table} SET INFO=\"Mistake\" WHERE ROWID={rowid}")
        return 0

    num_l, num_h = numberss(rowid, obj_low, obj_high, cursor)
    num_low = int(find_num(num_l))
    num_high = int(find_num(num_h))
    cursor.execute(f"SELECT x,y FROM {table} WHERE ROWID={obj_low[0]};")
    x_low, y_low = cursor.fetchone()
    cursor.execute(f"SELECT x,y FROM {table} WHERE ROWID={obj_high[0]};")
    x_high, y_high = cursor.fetchone()
    num_avg = abs(num_high - num_low)

    if num_avg < limit:
        if obj_low == obj_high:
            x = (x_high + x_low) / 2
            y = (y_high + y_low) / 2
            cursor.execute(
                f"UPDATE {table} SET x={x},y={y},INFO=\"connect to {num_l}\" WHERE ROWID={rowid}")
            return 0
        elif num == num_low:
            x = x_low
            y = y_low
            cursor.execute(
                f"UPDATE {table} SET x={x},y={y},INFO=\"connect to {num_l}\" WHERE ROWID={rowid}")
            return 0
        elif num == num_high:
            x = x_high
            y = y_high
            cursor.execute(
                f"UPDATE {table} SET x={x},y={y},INFO=\"connect to {num_h}\" WHERE ROWID={rowid}")
            return 0
        else:
            grt = num - num_low
            x = x_low + ((x_high - x_low) / num_avg * grt)
            y = y_low + ((y_high - y_low) / num_avg * grt)
            cursor.execute(
                f"UPDATE {table} SET x={x},y={y},INFO=\"interpolation btwn {num_l} & {num_h}\" WHERE ROWID={rowid}")
            return 0
    else:
        cursor.execute(
            f"UPDATE {table} SET INFO=\"No interpolation\" WHERE ROWID={rowid}")
        return 0


def near_iteration(rowid, cursor, lst):
    global limit, columns, table, hs_num, nr_d
    cursor.execute(f"SELECT {hs_num} FROM {table} WHERE ROWID={rowid};")
    num_st = str(cursor.fetchone()[0])
    num = find_num(num_st)

    sql_low = f"SELECT *  FROM {table} WHERE (CAST({hs_num} AS NUMERIC)<= (SELECT CAST(\"{num_st}\" AS NUMERIC)) AND x is NOT NULL AND {make_str(rowid)}) ORDER BY CAST({hs_num} AS NUMERIC) DESC LIMIT 1;"
    sql_high = f"SELECT *  FROM {table} WHERE (CAST({hs_num} AS NUMERIC) >= (SELECT CAST(\"{num_st}\" AS NUMERIC)) AND x is NOT NULL AND {make_str(rowid)}) ORDER BY CAST({hs_num} AS NUMERIC) ASC LIMIT 1;"
    notfind = True
    while notfind:
        cursor.execute(sql_low)
        obj_low = cursor.fetchone()
        cursor.execute(sql_high)
        obj_high = cursor.fetchone()

        if not obj_high and obj_low:
            obj_high = obj_low
            notfind = False
        elif not obj_low and obj_high:
            obj_low = obj_high
            notfind = False
        elif not obj_high and not obj_low:
            break

        if obj_high[0] not in lst and obj_low[0] not in lst:
            break

        elif obj_high[0] not in lst and obj_low[0] in lst:
            notfind = True
            sql_low = f"SELECT *  FROM {table} WHERE (CAST({hs_num} AS NUMERIC)< (SELECT CAST(\"{num_st}\" AS NUMERIC)) AND x is NOT NULL AND {make_str(rowid)}) ORDER BY CAST({hs_num} AS NUMERIC) DESC LIMIT 1;"
        elif obj_high[0] in lst and obj_low[0] not in lst:
            notfind = True
            sql_high = f"SELECT *  FROM {table} WHERE (CAST({hs_num} AS NUMERIC) > (SELECT CAST(\"{num_st}\" AS NUMERIC)) AND x is NOT NULL AND {make_str(rowid)}) ORDER BY CAST({hs_num} AS NUMERIC) ASC LIMIT 1;"
        else:
            notfind = True
            sql_high = f"SELECT *  FROM {table} WHERE (CAST({hs_num} AS NUMERIC) > (SELECT CAST(\"{num_st}\" AS NUMERIC)) AND x is NOT NULL AND {make_str(rowid)}) ORDER BY CAST({hs_num} AS NUMERIC) ASC LIMIT 1;"
            sql_low = f"SELECT *  FROM {table} WHERE (CAST({hs_num} AS NUMERIC)< (SELECT CAST(\"{num_st}\" AS NUMERIC)) AND x is NOT NULL AND {make_str(rowid)}) ORDER BY CAST({hs_num} AS NUMERIC) DESC LIMIT 1;"
    return obj_low, obj_high, num


def fnd_coor_nearest(lst, obj, cursor):
    global limit, columns, table, hs_num
    rowid = obj[0]
    obj_low, obj_high, num = near_iteration(rowid, cursor, lst)
    if not obj_high or not obj_low or not num:
        cursor.execute(
            f"UPDATE {table} SET INFO=\"No interpolation\" WHERE ROWID={rowid}")
        return 0

    num_l, num_h = numberss(rowid, obj_low, obj_high, cursor)
    num_low = int(find_num(num_l))
    num_high = int(find_num(num_h))
    cursor.execute(f"SELECT x,y FROM {table} WHERE ROWID={obj_low[0]};")
    x_low, y_low = cursor.fetchone()
    cursor.execute(f"SELECT x,y FROM {table} WHERE ROWID={obj_high[0]};")
    x_high, y_high = cursor.fetchone()

    if (abs(num - num_low) < limit) and (abs(num - num_low) <= abs(num - num_high)):
        x = x_low
        y = y_low
        cursor.execute(
            f"UPDATE {table} SET x={x},y={y},INFO=\"Connect to nearest {num_l}\" WHERE ROWID={rowid}")

    elif (abs(num - num_high) < limit) and (abs(num - num_high) < abs(num - num_low)):
        x = x_high
        y = y_high
        cursor.execute(
            f"UPDATE {table} SET x={x},y={y},INFO=\"Connect to nearest {num_h}\" WHERE ROWID={rowid}")

    else:
        cursor.execute(
            f"UPDATE {table} SET INFO=\"Over limit\" WHERE ROWID={rowid}")
        return 0


def fun_interpolation(db_fl):
    conn = create_connection(db_fl)
    cursor = conn.cursor()
    cursor.execute(f"ALTER TABLE {table} ADD COLUMN INFO TEXT;")
    cursor.execute(f"SELECT * FROM {table} WHERE x is NULL AND y is NULL;")
    allnull = cursor.fetchall()
    lst = [i[0] for i in allnull]
    print(len(allnull), ' to calculate; inter')
    for num, i in enumerate(allnull):
        if num % 100 == 0:
            conn.commit()
            print('Making: ', num)
        fnd_coor(lst, i, cursor)
    conn.commit()


def fun_nearest(db_fl):
    conn = create_connection(db_fl)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE x is NULL AND y is NULL;")
    allnull = cursor.fetchall()
    lst = [i[0] for i in allnull]
    print(len(allnull), ' to calculate; near')
    for num, i in enumerate(allnull):
        if num % 100 == 0:
            conn.commit()
            print('Making: ', num)
        fnd_coor_nearest(lst, i, cursor)
    conn.commit()


start_time = time.time()
if __name__ == '__main__':
    if inter:
        fun_interpolation(db_file)
    if nearest:
        fun_nearest(db_file)
print("Time is: ", time.time() - start_time)

#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# @Author  : YangTao
# @blog    : https://ytao.top

import logging
import pymysql
from ytaoCrawl import settings

def _database():
    database = pymysql.Connect(
        host=settings.MYSQL_HOST,
        user=settings.MYSQL_USER,
        passwd=settings.MYSQL_PASSWD,
        database=settings.MYSQL_DATABASE
    )
    return database

def insert_many(sql, val):
    # sql = "insert into account(account, password) value (%s, %s)"
    # val = [
    #     ('ytao', '123456'),
    #     ('tom', '123456')
    # ]
    database = _database()
    datacursor = database.cursor()
    try:
        datacursor.executemany(sql, val)
        database.commit()
    except:
        logging.error("insert_many error !!!")
        database.rollback()
    finally:
        if database != None:
            database.close()
    return datacursor.rowcount

def insert(query, table):
    dict = query.__dict__
    data = dict["_values"]
    keys = ', '.join(data.keys())
    placeholder = ', '.join(['%s'] * len(data))
    values = tuple(data.values())
    sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=placeholder)
    logging.info(sql)
    database = _database()
    datacursor = database.cursor()
    try:
        datacursor.execute(sql, values)
        logging.debug("Insert Successful!!!")
        database.commit()
    except BaseException as e:
        logging.error("数据添加失败：", e)
        database.rollback()
    finally:
        if database != None:
            database.close()
    return datacursor.rowcount

def select(sql):
    database = _database()
    datacursor = database.cursor()
    try:
        datacursor.execute(sql)
        result = datacursor.fetchall()
    except:
        logging.error("select error!!!", sql)
    finally:
        if database != None:
            database.close()
    return result

def delete(sql):
    database = _database()
    datacursor = database.cursor()
    try:
        datacursor.execute(sql)
        database.commit()
    except:
        database.rollback()
    finally:
        if database != None:
            database.close()
    return datacursor.rowcount

def delete_by_id(id, table):
    delete(str.format("DELETE FROM `{0}` WHERE id = '{1}'", table, id))

def update(sql):
    database = _database()
    datacursor = database.cursor()
    try:
        datacursor.execute(sql)
        database.commit()
    except:
        logging.error("update error!!!", sql)
        database.rollback()
    finally:
        if database != None:
            database.close()
    return datacursor.rowcount


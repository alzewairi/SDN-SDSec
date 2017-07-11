#!/usr/bin/python

import sqlite3


class MyDB:

    def __init__(self):
        self.db = sqlite3.connect(':memory:')
        self.cur = self.db.cursor()
        self.sdsec_tables = dict()
        self.sdsec_tables['s'] = 'SWITCHES' + '_' + 'C0'
        self.sdsec_tables['h'] = 'HOSTS' + '_' + 'C0'
        for t in self.sdsec_tables:
            self.create_db(table=self.sdsec_tables[t])

    def __exit__(self, exc_type, exc_value, traceback):
        if isinstance(self.db, sqlite3.Cursor):
            self.cur.close()

    def create_db(self, table):
        # SQLi
        if 'SWITCHES' in table:
            self.cur.execute('''CREATE TABLE {} (ID INTEGER PRIMARY KEY AUTOINCREMENT, SWITCH TEXT, INTERFACE TEXT, IP TEXT, MAC TEXT)'''.format(table))
        elif 'HOSTS' in table:
            self.cur.execute('''CREATE TABLE {} (ID INTEGER PRIMARY KEY AUTOINCREMENT, HOST TEXT, IP TEXT, MAC TEXT, SWITCH TEXT, INTERFACE TEXT, AUTH INTEGER, ACTION INTEGER)'''.format(table))
        self.db.commit()
        print True

    def check_auth(self, ip, mac):
        table_name = self.sdsec_tables['s']
        rows = self.select_db(
            table_name,
            cols='*',
            where="IP = '{}' OR MAC = '{}'".format(ip, mac)
        )
        if rows is not None:
            return False
        table_name = self.sdsec_tables['h']
        rows = self.select_db(
            table_name,
            cols='*',
            where="IP = '{}' OR MAC = '{}'".format(ip, mac)
        )
        if rows is not None:
            return False
        return True

    def add_switch(self):
        t = self.sdsec_tables['s']
        c = ", ".join(('SWITCH', 'INTERFACE', 'IP', 'MAC'))
        ip = '10.10.1.1'
        mac = '00:00:00:00:00:01'
        name = 's1'
        v = "', '".join((name, name, str(ip), str(mac)))
        self.insert_db(t, c, v)

    def add_host(self):
        t = self.sdsec_tables['h']
        c = ", ".join(('HOST', 'IP', 'MAC', 'SWITCH', 'INTERFACE', 'AUTH', 'ACTION'))
        auth = {}
        name = 'h1'
        ip = '10.10.1.1'
        mac = '00:00:00:00:00:02'
        sw_name = 's1'
        sw_intf = 's1-eth1'
        auth[sw_name] = [self.check_auth(ip=str(ip), mac=str(mac)), str(ip), str(mac)]
        action = 'FORWARD' if auth[sw_name][0] else 'DROP'
        v = "', '".join((name, str(ip), str(mac), sw_name, sw_intf, str(auth[sw_name][0]), action))
        self.insert_db(t, c, v)
        return auth

    def insert_db(self, table, cols, values):
        self.cur.execute("INSERT INTO {} ({}) VALUES ('{}')".format(table, cols, values))
        self.db.commit()

    def select_db(self, table, cols='*', where='1=1'):
        self.cur.execute("SELECT {} FROM {} WHERE {}".format(cols, table, where))
        rows = self.cur.fetchall()
        return rows


s = MyDB()
s.add_switch()
s.add_host()



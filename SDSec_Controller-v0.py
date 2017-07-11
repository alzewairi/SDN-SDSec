#!/usr/bin/python

from mininet.node import Controller, OVSController, NOX
import sqlite3
import netaddr
from os import environ


SDSec_DIR = environ['HOME'] + '/pycharmProjects/mininet-test/'


class SDSecController(OVSController):
    """
    Software Defined Security (SDSec) Controller
    """
    def __init__(self, name, cdir=SDSec_DIR, command='python SDSec_Controller.py',
                 cargs='openflow.of_01 --port=%s forwarding.l2_learning openflow.discovery', **kwargs):
        OVSController.__init__(self, name, **kwargs)
        # OVSController.__init__(self, name, cdir=cdir, command=command, cargs=cargs, **kwargs)
        # Define SDSec Table
        self.db = sqlite3.connect(':memory:')
        self.cur = self.db.cursor()
        self.sdsec_tables = []
        self.sdsec_tables.append('switches_{}'.format(name))
        for t in self.sdsec_tables:
            self.create_db(table=t)

    def __exit__(self, exc_type, exc_value, traceback):
        if isinstance(self.db, sqlite3.Cursor):
            self.cur.close()

    def get_tables(self):
        return self.sdsec_tables

    def create_db(self, table):
        # SQLi
        self.cur.execute('CREATE TEMP TABLE {} ('
                         'ID INTEGER PRIMARY KEY AUTOINCREMENT, '
                         'SWITCH TEXT, '
                         'INTERFACE TEXT, '
                         'IP INTEGER, '
                         'MAC TEXT, '
                         'TTL'
                         'ACTION INTEGER)'.format(table))
        self.db.commit()

    def check_node(self, switch, interface, ip, mac):
        rows = self.select_db(
            self.sdsec_tables[0],
            cols='*',
            where="SWITCH = '{}' AND INTERFACE = '{}' AND IP = {} AND MAC = '{}'".format(switch, interface, ip, mac)
        )
        if rows.rowcount < 0: # No ARP
            r = (switch, interface, ip, mac, 'FORWARD')
            self.insert_db(self.sdsec_tables[0], r)
            return None
        else:
            r = (switch, interface, ip, mac, 'DROP')
            self.insert_db(self.sdsec_tables[0], r)
            return rows

    def insert_db(self, table, rows):
        self.cur.executemany('INSERT INTO {} (SWITCH, INTERFACE, IP, MAC, ACTION) '
                             'VALUES (?,?,?,?,?)'.format(table), rows)
        self.db.commit()

    def select_db(self, table, cols='*', where='1=1'):
        rows = self.cur.execute('SELECT {} FROM {} WHERE {}'.format(cols, table, where))
        return rows


controllers = {'SDSec': SDSecController}


def ip2long(ip):
    return int(netaddr.IPAddress(ip))


def long2ip(n):
    return str(netaddr.IPAddress(n))

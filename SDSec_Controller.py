#!/usr/bin/python

from mininet.node import Controller, OVSController, NOX, OVSSwitch, Host
from mininet.net import Mininet
import sqlite3
import sqlitebck
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
        self.sdsec_tables = dict()
        self.sdsec_tables['s'] = 'SWITCHES' + '_' + self.name.upper()
        self.sdsec_tables['h'] = 'HOSTS' + '_' + self.name.upper()
        for t in self.sdsec_tables:
            self.create_db(table=self.sdsec_tables[t])

    def __exit__(self, exc_type, exc_value, traceback):
        if isinstance(self.db, sqlite3.Cursor):
            self.cur.close()

    @classmethod
    def start(self, ctrl, net):
        if isinstance(ctrl, SDSecController):
            OVSController.start(ctrl)
        if isinstance(net, Mininet):
            for sw in net.switches:
                ctrl.add_switch(sw)
                sw.start([ctrl])
            for h in net.hosts:
                # if h.name == 'h1':
                #     h.setIP('10.10.1.1')
                auth = ctrl.add_host(h)
                for i in auth:
                    if not auth[i][0]:
                        r = ctrl.cmd('ovs-ofctl -O OpenFlow13 add-flow %s "priority=%d,dl_src=%s,nw_src=%s,actions=%s"'
                                     % (i, 23823, auth[i][1], auth[i][2], 'drop'))

    def stop(self):
        super(SDSecController, self).stop()
        self.dump_dp("{}sqlite.db".format(SDSec_DIR))
        self.cur.close()

    def create_db(self, table):
        # SQLi
        if 'SWITCHES' in table:
            self.cur.execute('''CREATE TABLE {} (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            SWITCH TEXT,
            INTERFACE TEXT,
            IP TEXT,
            MAC TEXT)'''.format(table))
        elif 'HOSTS' in table:
            self.cur.execute('''CREATE TABLE {} (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            HOST TEXT,
            IP TEXT,
            MAC TEXT,
            SWITCH TEXT,
            INTERFACE TEXT,
            AUTH TEXT,
            ACTION TEXT)'''.format(table))
        self.db.commit()

    def check_auth(self, ip, mac, switch=None, interface=None):
        table_name = self.sdsec_tables['s']
        rows = self.select_db(
            table_name,
            cols='*',
            where="IP = '{}' OR MAC = '{}'".format(ip, mac)
        )
        if len(rows) > 0:
            return False
        table_name = self.sdsec_tables['h']
        rows = self.select_db(
            table_name,
            cols='*',
            where="IP = '{}' OR MAC = '{}'".format(ip, mac)
        )
        if len(rows) > 0:
            return False
        return True

    def add_switch(self, sw):
        if isinstance(sw, OVSSwitch):
            t = self.sdsec_tables['s']
            c = ", ".join(('SWITCH', 'INTERFACE', 'IP', 'MAC'))
            for intf in sw.intfList():
                if intf.name == 'lo':
                    continue
                ip = intf.ip
                if ip is None:
                    ip = sw.params['ip']
                v = "', '".join((sw.name, intf.name, str(ip), str(intf.mac)))
                self.insert_db(t, c, v)

    def add_host(self, h):
        if isinstance(h, Host):
            t = self.sdsec_tables['h']
            c = ", ".join(('HOST', 'IP', 'MAC', 'SWITCH', 'INTERFACE', 'AUTH', 'ACTION'))
            auth = {}
            for intf in h.intfList():
                if intf.name == 'lo':
                    continue
                # auth = simulate_auth()
                sw_name = intf.link.intf1.node.name
                sw_intf = intf.link.intf1.name
                auth[sw_name] = [self.check_auth(ip=str(intf.ip), mac=str(intf.mac)), str(intf.mac), str(intf.ip)]
                action = 'FORWARD' if auth[sw_name][0] else 'DROP'
                v = "', '".join((h.name, str(intf.ip), str(intf.mac), sw_name, sw_intf, str(auth[sw_name][0]), action))
                self.insert_db(t, c, v)
            return auth

    def insert_db(self, table, cols, values):
        self.cur.execute("INSERT INTO {} ({}) VALUES ('{}')".format(table, cols, values))
        self.db.commit()

    def select_db(self, table, cols='*', where='1=1'):
        self.cur.execute("SELECT {} FROM {} WHERE {}".format(cols, table, where))
        return self.cur.fetchall()

    def dump_dp(self, path):
        con = sqlite3.connect(path)
        sqlitebck.copy(self.db, con)
        con.commit()
        con.close()


controllers = {'SDSec': SDSecController}


def ip2long(ip):
    return int(netaddr.IPAddress(ip))


def long2ip(n):
    return str(netaddr.IPAddress(n))


def simulate_auth():
    from random import randint
    return True if randint(0, 100) % 2 == 0 else False

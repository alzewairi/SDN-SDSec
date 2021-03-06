#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    s2 = net.addSwitch('s2', cls=UserSwitch)
    s3 = net.addSwitch('s3', cls=UserSwitch)
    s1 = net.addSwitch('s1', cls=UserSwitch)

    info( '*** Add hosts\n')
    h8 = net.addHost('h8', cls=Host, ip='10.0.3.104', defaultRoute=None)
    h1 = net.addHost('h1', cls=Host, ip='10.0.2.101', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.2.104', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.2.103', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.2.102', defaultRoute=None)
    h6 = net.addHost('h6', cls=Host, ip='10.0.3.102', defaultRoute=None)
    h7 = net.addHost('h7', cls=Host, ip='10.0.3.103', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='10.0.3.101', defaultRoute=None)

    info( '*** Add links\n')
    net.addLink(s1, s2)
    net.addLink(s1, s3)
    net.addLink(s2, h1)
    net.addLink(s2, h2)
    net.addLink(s2, h3)
    net.addLink(s2, h4)
    net.addLink(s3, h5)
    net.addLink(s3, h6)
    net.addLink(s3, h7)
    net.addLink(s3, h8)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s2').start([])
    net.get('s3').start([])
    net.get('s1').start([c0])

    info( '*** Post configure switches and hosts\n')
    s2.cmd('ifconfig s2 10.0.2.1')
    s3.cmd('ifconfig s3 10.0.3.1')
    s1.cmd('ifconfig s1 10.0.1.1')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()


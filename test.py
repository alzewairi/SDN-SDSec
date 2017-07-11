#!/usr/bin/python

from mininet.node import UserSwitch, Host, Controller, OVSController, OVSSwitch
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from SDSec_Controller import *


def define_network():
    """
    Create Mininet network
    """
    info('+++ Defining Mininet Network\n')
    net = Mininet(topo=None,
                  build=False,
                  autoSetMacs=True,
                  ipBase='10.10.0.0/16')

    info('+++ Adding controller\n')
    c0 = net.addController(name='c0',
                           controller=SDSecController,
                           # ip='10.10.0.1',
                           protocol='tcp',
                           port=6633)

    info('+++ Add switches\n')
    m = 2
    switches = []
    for i in xrange(0, m):
        switches.append(net.addSwitch('s%d' % (i+1), cls=OVSSwitch, protocols='OpenFlow13', ip='10.10.%d.1' % (i+1)))

    info('+++ Add hosts\n')
    n = 8
    hosts = []
    for i in xrange(0, n/2):
        hosts.append(net.addHost('h%d' % (i+1), cls=Host, ip='10.10.1.%d' % (i+2), defaultRoute=None))
    for i in xrange(n/2, n):
        hosts.append(net.addHost('h%d' % (i+1), cls=Host, ip='10.10.2.%d' % (i+2), defaultRoute=None))

    info('+++ Add links\n')
    # net.addLink(c0, switches[0])
    # net.addLink(c0, switches[1])
    for i in xrange(0, n/2):
        net.addLink(switches[0], hosts[i])
    for i in xrange(n/2, n):
        net.addLink(switches[1], hosts[i])
    net.addLink(switches[0], switches[1])

    info('+++ Starting network\n')
    net.build()
    info('+++ Starting controllers\n')
    for controller in net.controllers:
        controller.start(controller, net)

    info('+++ Starting switches\n')

    # info('+++ Post configure switches and hosts\n')
    switches[0].cmd('ifconfig s1 10.10.1.1')
    switches[1].cmd('ifconfig s2 10.10.2.1')

    CLI(net)
    net.stop()


def simple_test():
    """
    Create and test a simple network
    """
    define_network()


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('debug')
    simple_test()
    # c0 = SDSecController('c0')

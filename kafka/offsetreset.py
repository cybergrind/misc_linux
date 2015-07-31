import argparse
import os
import logging
import sys


# EXAMPLE: python kafka/offsetreset.py hostname ed-mm

__b = os.path.dirname(__file__)+'/.deps'
sys.path.append(__b)
if not os.path.exists(__b):
    os.system('pip install -t {} kazoo'.format(__b))
from kazoo.client import KazooClient  # noqa


logging.basicConfig()

parser = argparse.ArgumentParser()
parser.add_argument('zkhost', metavar='ZK_HOST', type=str)
parser.add_argument('kfkq', metavar='QUEUE', type=str)
args = parser.parse_args()


def reset(bpath, new_val):
    zk = KazooClient(hosts=args.zkhost)
    zk.start()
    if zk.exists(bpath):  # /offsets
        for child in zk.get_children(bpath):  # offsets/topic
            c = '{0}/{1}'.format(bpath, child)
            print('Topic: {0}'.format(c))
            for c2 in zk.get_children(c):  # offsets/topic/partition
                c2 = '{0}/{1}'.format(c, c2)
                print('Set {0} to {1}'.format(c2, new_val))
                zk.set(c2, new_val)
    else:
        print('Path <{0}> not exists'.format(bpath))
    zk.stop()


def main():
    bpath = args.kfkq
    if len(bpath.split('/')) == 1:
        bpath = '/consumers/{0}/offsets/'.format(bpath)
        print('Expand to {0}'.format(bpath))
    return reset(bpath, b'0')


if __name__ == '__main__':
    main()

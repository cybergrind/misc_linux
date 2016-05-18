#!/usr/bin/env python3
'''
If you  get auth errors run:
$ aws configure set default.s3.signature_version s3v4
$ aws configure set default.ec2.signature_version v4
'''
import sys
import json
from datetime import datetime, timedelta
import subprocess

from aws.const import REGIONS


FMT = '%Y-%m-%dT%H:%M:00'

class Item(object):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, name):
        return self.data[name]

    def __str__(self):
        return '{0[AvailabilityZone]} {0[Timestamp]} - {0[SpotPrice]}'.format(self.data)

class Acc(object):
    def __init__(self):
        self.data = []

    def add(self, data):
        data = data['SpotPriceHistory']
        for s in data:
            s['SpotPrice'] = float(s['SpotPrice'])
            self.data.append(Item(s))
        self.data.sort(key=lambda x: x['SpotPrice'])

    def best(self, num):
        return self.data[:num]


def run(acc, region, instance_type):
    end = datetime.now().strftime(FMT)
    start = (datetime.now()-timedelta(minutes=30)).strftime(FMT)
    params = ['aws', 'ec2', 'describe-spot-price-history', '--instance-types',
              instance_type, '--product-description', "Linux/UNIX (Amazon VPC)",
              '--region', region, '--start-time', start, '--end-time', end]
    print('Region: {}'.format(region))
    print(' '.join(params))
    out = subprocess.run(params, stdout=subprocess.PIPE)
    out = json.loads(out.stdout.decode('utf8'))
    acc.add(out)


def main():
    acc = Acc()
    instance_type = 'm4.large' if len(sys.argv) == 1 else sys.argv[1]
    for region in REGIONS:
        run(acc, region, instance_type)
    for i in acc.best(30):
        print(i)

if __name__ == '__main__':
    main()

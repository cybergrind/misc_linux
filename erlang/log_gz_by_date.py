'''
Create from debug.log.# => debug.log.<date>.gz
Usage: python2 log_gz_by_date.py debug.log.?

Crontab setup for achiving logs for 1 month:
4 15 * * * cd logs && gzip debug.log.0 && mv debug.log.0.gz debug.log.$(date +'\%Y-\%m-\%d' --date='1 days ago').gz
50 4 * * * cd logs && rm -f *.log.$(date +'\%Y-\%m-\%d' --date='31 days ago').gz  
'''
import os
import sys

def main(f):
    fd = open(f)
    pat = fd.read(len('2014-07-22'))
    fd.close()
    if os.path.exists('/usr/bin/pigz'):
        gz_cmd = 'pigz'
    else:
        gz_cmd = 'gzip'
    cmd = '%(gz_cmd)s %(f)s && mv %(f)s.gz debug.%(pat)s.gz'%({'f': f, 'pat': pat,
                                                               'gz_cmd': gz_cmd})
    print('Run: %r'%cmd)
    os.system(cmd)


if __name__ == '__main__':
    for f in sys.argv[1:]:
        main(f)


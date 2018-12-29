
import json
from time import sleep
from string import ascii_lowercase, ascii_uppercase, digits
from itertools import product, islice
from collections import deque
from threading import Thread

BUFFER_SIZE = 50 # number of passwords to be cached
LOW_LEVEL_THRESHOLD = 10
MIN_PWD_LENGTH = 6
MAX_PWD_LENGTH = 20

class PwdGenerator():

  def __init__(self, *args, **kwargs):
    self.l_bound = MIN_PWD_LENGTH
    self.u_bound = MAX_PWD_LENGTH
    self.key_map = {
        'small_letters':ascii_lowercase,
        'capital_letters':ascii_uppercase,
        'digits': digits,
        'symbols': u"`<>{}[]/*-+.!@#$%&*()_=+;:]'\""
    }
    # mapped using key_map
    self.prefix_key = None 
    self.suffix_key = None 
    
    self.prefix_key_len = 0
    self.suffix_key_len = 0
    
    self.prefix_fixed = ""
    self.suffix_fixed = ""
    
    self.suffix_part_confirmed = False
    self.prefix_part_confirmed = False
        
    self.suffix_key_confirmed = False
    self.prefix_key_confirmed = False
    
    self.needed_keys = []

    self.finished = False
    self.isAlive = True

    self.pwd_buffer = deque(maxlen=BUFFER_SIZE*2) # we allow appending unused passwords (connection error)
    
    self.generator_count = 0
    self.buffer_threshold = 1

    self.check_buffer_thread = None
  
  def init(self, data):
    """ init class attributes """
    self.suffix_fixed = data.get('suffix_fixed',None)
    self.prefix_key = data.get("prefix_key",None) # data.get('prefix_key', None)
    self.prefix_key_len = data.get("prefix_key_len", 0)
    self.prefix_key_confirmed = data.get("prefix_key_confirmed", False)
    self.suffix_part_confirmed = data.get("suffix_part_confirmed", False)
    self.buffer_threshold = LOW_LEVEL_THRESHOLD
    
    self.needed_keys = data.get("needed_keys", [])
    new_key_map = data.get("key_map", None) # customize values of needed keys
    if isinstance(new_key_map, dict):
        for k,v in new_key_map.items():
            if k in self.key_map:
                self.key_map[k] = v

    self.generator = data.get("generator_function", self.generator_func())
    self.check_buffer_thread = Thread(name='password_buffer_filler', target=self.pwd_generator)
    self.check_buffer_thread.daemon = True

  def increase_pwd_len(self):
      if self.l_bound < MAX_PWD_LENGTH:
        self.l_bound += 1
        return self.l_bound

  def generator_func(self):
    """ password generator """
    pwd = {
      'prefix' : self.prefix_fixed,
      'body': '',
      'suffix': self.suffix_fixed
    }
    length_part = len(self.prefix_fixed) * self.prefix_part_confirmed \
                + len(self.suffix_fixed) * self.suffix_part_confirmed \
                + self.prefix_key_len * self.prefix_key_confirmed \
                + self.suffix_key_len * self.suffix_key_confirmed
    for n in range(self.l_bound - length_part, self.u_bound + 1): # + 1 (range doesn't access last num)
        for tup in product(self.needed_keys,repeat=n): # to repreat product's input nth time
            for p in product(*(self.key_map[key] for key in tup)):
                pwd['body'] = "".join(p)
                if self.prefix_key in self.key_map.keys():
                  for extra in product(self.key_map[self.prefix_key], repeat=self.prefix_key_len):
                      pwd['prefix'] = self.prefix_fixed + "".join(extra)
                      yield pwd['prefix'] + pwd['body'] + pwd['suffix']
                
                if not self.prefix_part_confirmed:
                    yield pwd['body'] + pwd['suffix']
                
                if self.suffix_key in self.key_map.keys():
                  for extra in product(self.key_map[self.suffix_key], repeat=self.suffix_key_len):
                      pwd['suffix'] = "".join(extra) + self.suffix_fixed
                      yield pwd['prefix'] + pwd['body'] + pwd['suffix']

                if not self.suffix_part_confirmed:
                    yield pwd['prefix'] + pwd['body']
  
  
  def pwd_generator(self):
    " Fill buffer with generated passwords when buffer size reach a critical level"
    try:
        while self.isAlive:
            if len(self.pwd_buffer) < BUFFER_SIZE:
                self.fill_buffer()
            else:
                sleep(3)
    except StopIteration:
        return self.generator_end()

  def stop_generator(self):
    "When you want to exit the programm, you must be out of pooling loop of thread check_buffer_thread"
    self.isAlive = False

  def fill_buffer(self):
    """ Check if the fixed size buffer is in low level, then try to generate
            new passwords to fill it till generator finished """
    while len(self.pwd_buffer) < BUFFER_SIZE:
        try:
            self.pwd_buffer.append(next(self.generator))
            self.generator_count += 1
        except:
            break
    return 

  def skip(self, n):
    """ skip nth iterations in generator and return next iteration """
    # previous_count = self.generator_count
    try:
        pwd = next(islice(self.generator, n, n+1)) 
        self.pwd_buffer.append(pwd)
        self.generator_count += n 
        return pwd
    except StopIteration:
        print("\n Generator finished")
        return self.generator_end()
    finally:
        print("Last Password: [{0}]".format(self.last_pwd))
        pass

  def reset(self):
     self.generator_count = 0
     self.generator = self.generator_func()   

  def generator_end(self):
    self.finished = True
    return "" # in this case empty_string is better than None
  
  @property
  def last_pwd(self):
    return self.pwd_buffer[0] if self.pwd_buffer else ""

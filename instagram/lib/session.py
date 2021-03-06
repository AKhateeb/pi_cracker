# Date: 05/05/2018
# Author: Pure-L0G1C
# Description: Session Handler

from os import remove
from os.path import exists as path 
from csv import DictWriter, DictReader

class Session(object):
 def __init__(self, file_name): # this method has been modified (passlist removed)
  self.file = '.{}_.csv'.format(file_name)

 def exists(self):
  return path(self.file)

 def read(self):
  with open(self.file, 'r') as csvfile:
   session = DictReader(csvfile, delimiter = ',')
   try:return [_ for _ in session][0] # if file is empty, Index error exception will be thrown
   except:pass 

 def write(self, attempts, last_password=None):
  if not attempts:return
  with open(self.file, 'w') as csvfile:
   fieldnames = ['generator_seed'] #, 'last_password']
   writer = DictWriter(csvfile, fieldnames=fieldnames)

   writer.writeheader()
   writer.writerow({ 'generator_seed': int(attempts) }) #, 'last_password': last_password })

 def delete(self):
  if path(self.file):
   try:remove(self.file)
   except:pass 
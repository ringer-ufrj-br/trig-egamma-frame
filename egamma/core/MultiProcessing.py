
__all__ = [ "Pool", "Slot", 'complete']


from egamma.core import LoggingLevel, Messenger
from egamma.core.macros import *
from pprint import pprint
import argparse
import os, time
import subprocess

from colorama import Back, Fore
import colorama
import ROOT
colorama.init(autoreset=True)



def complete(id):
  path = os.getcwd()+'/.done.%d'%(id)
  with open(path,'w'):
    pass


class Slot(object):

  def __init__( self ):
    self.__proc = None
    self.__lock = False

  def lock(self):
    self.__lock=True
  
  def unlock(self):
    self.__lock=False

  def update(self):
    if self.__proc and not self.__proc.poll():
      self.unlock()

  def run(self, command):
    self.__proc = subprocess.Popen(command.split(' '))
    self.lock()

  def isAvailable(self):
    if self.__proc:
      if not self.__proc.poll() is None:
        self.unlock()
    return not self.__lock




class Pool( Messenger ):

  def __init__(self, command, maxJobs, files, output ):
    
    Messenger.__init__(self)
    self.__files = files
    self.__command = command
    self.__output  = output
    self.__slots = [Slot() for _ in range(maxJobs)]
    self.__outputs = []


  def getAvailable(self):
    for slot in self.__slots:
      if slot.isAvailable():
        return slot
    return None

  
  def busy(self):
    for slot in self.__slots:
      if not slot.isAvailable():
        return True
    return False


  def generate(self):

    idx = len(self.__files)
    f = self.__files.pop()
    output = self.__output + '.' + str(idx)
    command = self.__command.replace('%IN', f)
    command = command.replace('%OUT', output)
    command = command.replace('%JOB_ID', str(idx) )
    print(command)
    return command, output, idx


  def run( self ):

    total = len(self.__files)

    while len(self.__files) > 0:

      slot = self.getAvailable()
      if slot:
        print(Back.RED + Fore.WHITE + 'running %d/%d'%(len(self.__files), total))
        #time.sleep(1)
        command, output, idx = self.generate()
        if os.path.exists('.done.%d'%idx):
          MSG_WARNING(self, f"Skip job id {idx}")
          continue
        self.__outputs.append(output)
        slot.run( command )
    
    while self.busy():
      continue


  def merge(self, command):
    command = "hadd -f "+self.__output
    for fname in self.__outputs:
      command += ' '+fname
    os.system(command)
    for fname in self.__outputs:
      os.system( 'rm -rf '+fname)


  #
  # Check if file exist or his consistencels
  #
  def exist(self, f):
    if not os.path.exists(f):
        return False
    else:
      return False










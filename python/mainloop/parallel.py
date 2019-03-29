

__all__ = ['Merge', 'Parallel']

from Gaugi.messenger import LoggingLevel, Logger
from Gaugi.messenger.macros import *

class Merge( Logger ):

  def __init__(self, fList):
    
    Logger.__init__(self)
    from Gaugi.utilities import csvStr2List
    from Gaugi.utilities import expandFolders
    self.fList = csvStr2List ( fList )
    self.fList = expandFolders( fList )
    self.process_pipe = []
    self.output_stack = []
    import random
    import time
    random.seed(time.time())
    self._base_id = random.randrange(100000)



  def launch( self, output, nFilesPerMerge, maxJobs):
    
    import os
    import subprocess
    from pprint import pprint

    def chunks(l, n):
      """Yield successive n-sized chunks from l."""
      for i in xrange(0, len(l), n):
        yield l[i:i + n]
    f = []
    for l in chunks(self.fList, nFilesPerMerge):
      f.append(l)
    fList = f

    while len(fList) > 0:
      if len(self.process_pipe) < int(maxJobs):
        job_id = len(fList)
        f = fList.pop()
        f_str = ''
        for o in f:  f_str+=' '+o
        self.output_stack.append( ('output_%d_%d_merge.root') % (self._base_id, job_id) )
        command = ('hadd -f %s%s') % (self.output_stack[-1],f_str)
        #MSG_INFO( self,  ('adding process into the stack with id %d')%(job_id), extra={'color':'0;35'})
        MSG_INFO( self,  ('adding process into the stack with id %d')%(job_id) )
        proc = subprocess.Popen(command.split(' '))
        pprint(command)
        self.process_pipe.append( (job_id, proc) )
    
      for proc in self.process_pipe:
        if not proc[1].poll() is None:
          #MSG_INFO( self,  ('pop process id (%d) from the stack')%(proc[0]), extra={'color':'0;35'})
          MSG_INFO( self,  ('pop process id (%d) from the stack')%(proc[0]) )
          # remove proc from the pipe
          self.process_pipe.remove(proc)
    
    # Check pipe process
    # Protection for the last jobs
    while len(self.process_pipe)>0:
      for proc in self.process_pipe:
        if not proc[1].poll() is None:
          #MSG_INFO( self,  ('pop process id (%d) from the stack')%(proc[0]), extra={'color':'0;35'})
          MSG_INFO( self,  ('pop process id (%d) from the stack')%(proc[0]) )
          # remove proc from the pipe
          self.process_pipe.remove(proc)
    
    # merge all
    #MSG_INFO( self,  'merge all files...', extra={'color':'0;35'})
    MSG_INFO( self,  'merge all files...')
    f_str = ' '
    for o in self.output_stack:
      f_str+=o+' '
    os.system('hadd %s %s'%(output, f_str))




class Parallel( Logger ):

  def __init__(self, fList):
    
    Logger.__init__(self)
    from Gaugi.utilities import csvStr2List
    from Gaugi.utilities import expandFolders
    self.fList = csvStr2List ( fList )
    self.fList = expandFolders( fList )
    self.process_pipe = []
    self.output_stack = []
    import random
    import time
    random.seed(time.time())
    self._base_id = random.randrange(100000)


  def launch( self, _command, maxJobs ):
    import os
    import subprocess
    from pprint import pprint
    
    while len(self.fList) > 0:
      if len(self.process_pipe) < int(maxJobs):
        job_id = len(self.fList)
        f = self.fList.pop()
        oname = ('output_%d_%d.root') % (self._base_id, job_id) 
       
        if not os.path.isfile('./'+oname):
          self.output_stack.append( ('output_%d_%d.root') % (self._base_id, job_id) )
          command = _command+' '
          command += ('-i %s -o %s') % (f, self.output_stack[-1])
          #MSG_INFO( self,  ('adding process into the stack with id %d')%(job_id), extra={'color':'0;35'})
          MSG_INFO( self,  ('adding process into the stack with id %d')%(job_id) )
          pprint(command)
          proc = subprocess.Popen(command.split(' '))
          self.process_pipe.append( (job_id, proc) )
    
      for proc in self.process_pipe:
        if not proc[1].poll() is None:
          #MSG_INFO( self,  ('pop process id (%d) from the stack')%(proc[0]), extra={'color':'0;35'})
          MSG_INFO( self,  ('pop process id (%d) from the stack')%(proc[0]) )
          self.process_pipe.remove(proc)
    
    # Check pipe process
    # Protection for the last jobs
    while len(self.process_pipe)>0:
      for proc in self.process_pipe:
        if not proc[1].poll() is None:
          #MSG_INFO( self,  ('pop process id (%d) from the stack')%(proc[0]), extra={'color':'0;35'})
          MSG_INFO( self,  ('pop process id (%d) from the stack')%(proc[0]) )
          # remove proc from the pipe
          self.process_pipe.remove(proc)






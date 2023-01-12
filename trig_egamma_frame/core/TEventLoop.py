
__all__ = ['TEventLoop']

from trig_egamma_frame.core         import Messenger, LoggingLevel
from trig_egamma_frame.core         import get_property
from trig_egamma_frame.core         import StatusCode,StatusTool,StatusWTD
from trig_egamma_frame.core         import EventContext
from trig_egamma_frame.core         import StoreGate
from trig_egamma_frame.core.helpers import expand_folders,progressbar
from trig_egamma_frame.core.macros  import *

import collections
import ROOT
import traceback




class TEventLoop( Messenger ):

  def __init__(self, name, **kw):

    # Retrieve all information needed
    Messenger.__init__(self, name)
    fList                   = get_property( kw, 'inputFiles'      , []                             )
    self._ofile             = get_property( kw, 'outputFile'      , "histos.root"                  )
    self._treePath          = get_property( kw, 'treePath'        , None                           )
    self._dataframe         = get_property( kw, 'dataframe'       , None                           )
    self._nov               = get_property( kw, 'nov'             , -1                             )
    self._abort             = get_property( kw, 'abort'           , True                           )
    self._mute_progressbar  = get_property( kw, 'mute_progressbar', False                          )
    self._level             = LoggingLevel.retrieve( get_property(kw, 'level', LoggingLevel.INFO ) )
    

    files = []
    for path in fList:
      # Need to loop over for LCG grid
      for f in path.split(','):
        files.extend( expand_folders( f ) )
    
    self._fList = files
    self._containersSvc  = collections.OrderedDict() # container dict to hold all EDMs
    self._storegateSvc = None # storegate service to hold all hists
    self._t = None # TChain used to hold the ttree files
    self._event = None # TEvent schemma used to read the ttree
    self._entries = None # total number of event inside of the ttree
    self._context = None # Hold the event context

    # Use this to hold the fist good
    self._metadataInputFile = None



  #
  # Initialize all services
  #
  def initialize( self ):

    MSG_INFO( self, 'Initializing TEventLoop...')

    ### Prepare to loop:
    self._t = ROOT.TChain()
    for inputFile in progressbar(self._fList, prefix= "Creating collection tree " ):
      # Check if file exists
      self._f  = ROOT.TFile.Open(inputFile, 'read')
      if not self._f or self._f.IsZombie():
        MSG_WARNING( self, f"Couldn''t open file: {inputfile}")
        continue
      # Inform user whether TTree exists, and which options are available:
      MSG_DEBUG(self, f"Adding file: {inputfile}")
      try:
        # Custon directory token
        if '*' in self._treePath:
          dirname = self._f.GetListOfKeys()[0].GetName()
          treePath = self._treePath.replace('*',dirname)
        else:
          treePath=self._treePath
      except:
        MSG_WARNING( self, f"Couldn't retrieve TTree ({treePath}) from GetListOfKeys!")
        continue

      obj = self._f.Get(treePath)
      if not obj:
        MSG_WARNING( self, f"Couldn't retrieve TTree ({treePath})!")
        MSG_INFO( self, "File available info:")
        self._f.ReadAll()
        self._f.ReadKeys()
        self._f.ls()
        continue
      elif not isinstance(obj, ROOT.TTree):
        MSG_FATAL( self, f"{treePath} is not an instance of TTree!")

      if not self._metadataInputFile:
        self._metadataInputFile = (inputFile, treePath)

      self._t.Add( inputFile+'/'+treePath )
    # Turn all branches off.
    self._t.SetBranchStatus("*", False)

    # Ready to retrieve the total number of events
    self._t.GetEntry(0)
    ## Allocating memory for the number of entries
    self._entries = self._t.GetEntries()

    
    self._context = EventContext(self._t)

    # Create the StoreGate service
    if not self._storegateSvc:
      MSG_INFO( self, "Creating StoreGate...")
      self._storegateSvc = StoreGate( self._ofile )
    else:
      MSG_INFO( self, 'The StoraGate was created for ohter service. Using the service setted by client.')
    
    return StatusCode.SUCCESS



  #
  # Execute the main loop...
  #
  def execute( self ):

    ### Loop over events
    for entry in progressbar(range(self.get_nov()), prefix= "Looping over entries ", mute=self._mute_progressbar):
      
      try:
        self.process(entry)
      except Exception as e:
        print(e)
        traceback.print_exc()
        if self._abort:
          MSG_FATAL(self, f"Abort event {entry}")
        else:
          MSG_ERROR(self, f"Error event {entry}")


    return StatusCode.SUCCESS


  def process(self, entry):

    # retrieve all values from the branches
    context = self.getContext()
    context.setEntry(entry)
    # reading all values from file to EDM pointers.
    # the context hold all EDM pointers
    context.execute()
    # loop over tools...
    for alg in self._alg_tools:
      if alg.status is StatusTool.DISABLE:
        continue
      if alg.execute( context ).isFailure():
        MSG_ERROR( self, f'The tool {alg.name} return status code different of SUCCESS')
      if alg.wtd is StatusWTD.ENABLE:
        MSG_DEBUG(self, f'Watchdog is true in {alg.name}. Skip events')
        # reset the watchdog since this was used
        alg.wtd = StatusWTD.DISABLE
        break


  #
  # Finalize the core
  #
  def finalize( self ):

    MSG_INFO( self, 'Finalizing all tools...')
    for alg in self._alg_tools:
      if alg.isFinalized():
        continue
      if alg.finalize().isFailure():
        MSG_ERROR( self, f'The tool {alg.name} return status code different of SUCCESS')

    MSG_INFO( self, 'Finalizing StoreGate service...')
    self._storegateSvc.write()
    del self._storegateSvc
    MSG_DEBUG( self, "Finalizing file...")
    self._f.Close()
    del self._f
    del self._event
    del self._t
    MSG_DEBUG( self, "Everything was finished... tchau!")
    return StatusCode.SUCCESS


  #
  # Run
  #
  def run( self, nov=-1 ):
    self._nov = nov
    self.initialize()
    self.execute()
    self.finalize()



  def getEntries(self):
    return self._entries

  #
  # User method
  #
  def getEntry( self, entry ):
    self._t.GetEntry( entry )


  def getContext(self):
    return self._context


  # get the storegate pointer
  def getStoreGateSvc(self):
    return self._storegateSvc


  # set the storegate from another external source
  def setStoreGateSvc(self, store):
    self._storegateSvc = store


  # number of event
  def get_nov(self):
    if self._nov < 0 or self._nov > self.getEntries():
      return self.getEntries()
    else:
      return self._nov




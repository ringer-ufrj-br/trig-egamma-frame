
__all__ = ['TEventLoop']

from egamma.kernel       import StatusCode
from egamma.kernel       import EventContext, StoreGate, StatusTool, StatusWTD

import collections
import ROOT
import traceback
from tqdm import tqdm




class TEventLoop( Messenger ):

  def __init__(self, 
               name : str,
               inputFile : str,
               outputFile : str,
               treePath : str,
               dataframe : str,
               nov : int,
               abort : bool,
               mute : bool,
               writeStoregate : bool,
               level : LoggingLevel
               ):

    """
    Initialize the TEventLoop class.

    Args:
      name (str): The name of the TEventLoop.
      inputFile (str): The input file.
      outputFile (str): The output file.
      treePath (str): The path to the tree.
      dataframe (str): The dataframe.
      nov (int): The number of events.
      abort (bool): Whether to abort on error.
      mute (bool): Whether to mute the output.
      writeStoregate (bool): Whether to write the storegate.
      level (LoggingLevel): The logging level.
    """


    self._fList             = inputFile
    self._ofile             = outputFile
    self._treePath          = treePath
    self._dataframe         = dataframe
    self._nov               = nov
    self._abort             = abort
    self._mute              = mute
    self._writeStoregate    = writeStoregate
    self._level             = level
    
    if type(self._fList) is not list:
      self._fList = [self._fList]

    self._containersSvc  = collections.OrderedDict() # container dict to hold all EDMs
    self._storegateSvc = None # storegate service to hold all hists
    self._event = None # TEvent schemma used to read the ttree
 



  #
  # Initialize all services
  #
  def initialize( self ) -> StatusCode:

    logger.info( 'Iiitializing TEventLoop...')
    # Use this to hold the fist good
    self._metadataInputFile = None

    ### Prepare to loop:
    self._t = ROOT.TChain()

    for inputFile in tqdm(self._fList, desc="creating collection tree " ):
      # Check if file exists
      self._f  = ROOT.TFile.Open(inputFile, 'read')
      if not self._f or self._f.IsZombie():
        logger.warning( f"Couldn''t open file: {inputFile}")
        continue
      # Inform user whether TTree exists, and which options are available:
      logger.debug( f"Adding file: {inputFile}")
      try:
        # Custon directory token
        if '*' in self._treePath:
          dirname = self._f.GetListOfKeys()[0].GetName()
          treePath = self._treePath.replace('*',dirname)
        else:
          treePath=self._treePath
      except:
        logger.warning( f"Couldn't retrieve TTree ({treePath}) from GetListOfKeys!")
        continue

      obj = self._f.Get(treePath)
      if not obj:
        logger.warning( f"Couldn't retrieve TTree ({treePath})!")
        MSG_INFO( self, "File available info:")
        self._f.ReadAll()
        self._f.ReadKeys()
        self._f.ls()
        continue
      elif not isinstance(obj, ROOT.TTree):
        logger.fatal( f"{treePath} is not an instance of TTree!")

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
      logger.info( "creating StoreGate...")
      self._storegateSvc = StoreGate( self._ofile )
    else:
      logger.info( 'the StoraGate was created for ohter service. Using the service setted by client.')
    
    return StatusCode.SUCCESS



  #
  # Execute the main loop...
  #
  def execute( self ) -> StatusCode:

    ### Loop over events
    for entry in tqdm(range(self.get_nov()), desc="looping over entries ", disable=self._mute):
      
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
    if self._writeStoregate:
      MSG_INFO(self, f"writting root data into {self._ofile}")
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





__all__ = ['TEventLoop']

import collections
import ROOT
import traceback

from tqdm import tqdm
from trig_egamma_frame import logger
from trig_egamma_frame.kernel import StatusCode, StoreGate, StatusTool, StatusWTD, EventContext
from trig_egamma_frame.enumerators import DataframeSchemma
from expand_folders import expand_folders




def print_root_tree(directory, indent=""):
    # Get keys for the current directory
    keys = directory.GetListOfKeys()
    
    for key in keys:
        obj = key.ReadObj()
        if isinstance(obj, ROOT.TDirectoryFile):
            print(f"{indent}Directory: {obj.GetName()}")
            # Recurse into the directory
            print_root_tree(obj, indent + "  ")
        elif isinstance(obj, ROOT.TTree):
            print(f"{indent}Tree: {obj.GetName()} ({obj.GetEntries()} entries)")
        else:
            print(f"{indent}Object: {obj.GetName()} [{obj.ClassName()}]")




class TEventLoop:

  def __init__(self, 
               name : str,
               inputFile : str,
               outputFile : str,
               treePath : str,
               dataframe : DataframeSchemma = DataframeSchemma.Run2,
               nov : int=-1,
               abort : bool=False,
               mute : bool=False,
               writeStoregate : bool=True,
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
    
    if isinstance(self._fList, str):
      self._fList = expand_folders(self._fList)

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
        print_root_tree(self._f)

        logger.info( "File available info:")
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
          logger.fatal( f"Abort event {entry}")
        else:
          logger.error( f"Error event {entry}")


    return StatusCode.SUCCESS


  def process(self, entry: int) -> None:

    # retrieve all values from the branches
    context = self.getContext()
    context.setEntry(entry)
    # reading all values from file to EDM pointers.
    # the context hold all EDM pointers
    context.execute()

    from trig_egamma_frame.kernel import ToolSvc as toolSvc
    # loop over tools...
    for alg in toolSvc:
      if alg.status is StatusTool.DISABLE:
        continue
      if alg.execute( context ).isFailure():
        logger.fatal( f'The tool {alg.name} return status code different of SUCCESS')
      if alg.wtd is StatusWTD.ENABLE:
        logger.debug( f'Watchdog is true in {alg.name}. Skip events')
        # reset the watchdog since this was used
        alg.wtd = StatusWTD.DISABLE
        break


  #
  # Finalize the core
  #
  def finalize( self ) -> StatusCode:

    logger.info( 'Finalizing all tools...')

    from trig_egamma_frame.kernel import ToolSvc as toolSvc
    for alg in toolSvc:
      if alg.isFinalized():
        continue
      if alg.finalize().isFailure():
        logger.error( f'The tool {alg.name} return status code different of SUCCESS')


    logger.info( 'Finalizing StoreGate service...')
    if self._writeStoregate:
      logger.info( f"writting root data into {self._ofile}")
      self._storegateSvc.write()
    del self._storegateSvc

    logger.debug( "Finalizing file...")
    self._f.Close()
    del self._f
    del self._event
    del self._t
    logger.debug( "Everything was finished... tchau!")
    return StatusCode.SUCCESS


  #
  # Run
  #
  def run( self, nov: int = -1 ) -> None:
    self._nov = nov
    self.initialize()
    self.execute()
    self.finalize()



  def getEntries(self) -> int:
    return self._entries

  #
  # User method
  #
  def getEntry( self, entry: int ) -> None:
    self._t.GetEntry( entry )


  def getContext(self) -> EventContext:
    return self._context


  # get the storegate pointer
  def getStoreGateSvc(self) -> StoreGate:
    return self._storegateSvc


  # set the storegate from another external source
  def setStoreGateSvc(self, store: StoreGate) -> None:
    self._storegateSvc = store


  # number of event
  def get_nov(self) -> int:
    return self.getEntries() if self._nov < 0 or self._nov > self.getEntries() else self._nov




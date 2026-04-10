
__all__ = ['ElectronLoop']


from trig_egamma_frame.kernel import StatusCode, StatusTool, TEventLoop
from trig_egamma_frame.enumerators import DataframeSchemma
from loguru import logger

#
# Electron loop
#
class ElectronLoop( TEventLoop ):

  def __init__(self, name : str , **kw):
    # Retrieve all information needed
    TEventLoop.__init__(self, name, **kw)


  #
  # Initialize all services
  #
  def initialize( self ) -> StatusCode:

    logger.info( 'Initializing Event...')
    if super(ElectronLoop,self).initialize().isFailure():
      logger.error( "Impossible to initialize the TEventLoop services.")

    if self._dataframe is DataframeSchemma.Run2:
      from trig_egamma_frame.dataframe.c_struct.Electron_v1 import Electron_v1
      self._event = Electron_v1()
      from trig_egamma_frame.dataframe import Electron_v1      as Electron
      from trig_egamma_frame.dataframe import TrigEMCluster_v1 as TrigEMCluster
      from trig_egamma_frame.dataframe import TrigElectron_v1  as TrigElectron
      from trig_egamma_frame.dataframe import CaloCluster_v1   as CaloCluster
      from trig_egamma_frame.dataframe import TrackParticle_v1 as TrackParticle
      from trig_egamma_frame.dataframe import EmTauRoI_v1      as EmTauRoI
      from trig_egamma_frame.dataframe import EventInfo_v1     as EventInfo
      from trig_egamma_frame.dataframe import MonteCarlo_v1    as MonteCarlo
      #from trig_egamma_frame.dataframe import Menu_v1          as Menu

    elif self._dataframe is DataframeSchemma.Run3:
      
      from trig_egamma_frame.dataframe.c_struct.Electron_v2 import Electron_v2
      self._event = Electron_v2()
      from trig_egamma_frame.dataframe import Electron_v2      as Electron
      from trig_egamma_frame.dataframe import TrigEMCluster_v1 as TrigEMCluster
      from trig_egamma_frame.dataframe import TrigElectron_v2  as TrigElectron
      from trig_egamma_frame.dataframe import CaloCluster_v2   as CaloCluster
      from trig_egamma_frame.dataframe import TrackParticle_v2 as TrackParticle
      from trig_egamma_frame.dataframe import EmTauRoI_v2      as EmTauRoI
      from trig_egamma_frame.dataframe import EventInfo_v2     as EventInfo
      from trig_egamma_frame.dataframe import MonteCarlo_v2    as MonteCarlo
      #from trig_egamma_frame.dataframe import Menu_v1          as Menu

    else:
      return StatusCode.FATAL


    logger.info( "Creating containers...")
    # Allocating containers


    # Initialize the base of this container.
    # Do not change this key names!
    self._containersSvc  = {
                            # event dataframe containers
                            'EventInfoContainer'         : EventInfo(),
                            'MonteCarloContainer'        : MonteCarlo(),
                            'CaloClusterContainer'       : CaloCluster(),
                            #'MenuContainer'              : Menu(),
                           }

    self._containersSvc.update({
                            'HLT__TrigEMClusterContainer': TrigEMCluster(),
                            'HLT__CaloClusterContainer'  : CaloCluster(),
                            'HLT__EmTauRoIContainer'     : EmTauRoI(),
                            })

    self._containersSvc.update({  
                            'ElectronContainer'          : Electron(),
                            'TrackParticleContainer'     : TrackParticle(),
                            'HLT__TrigElectronContainer' : TrigElectron(),
                            'HLT__ElectronContainer'     : Electron(),
                            'HLT__TrackParticleContainer': TrackParticle(),
                            })
  

    # append TDT container
    #if self._dataframe is DataframeSchemma.Run2:
    #  from egamma.dataframe import TDT_v1 as TDT
    #  self._containersSvc.update({
    #                        # metadata containers
    #                        'HLT__TDT'                   : TDT(),
    #                        })


    # configure all EDMs needed
    for key, edm  in self._containersSvc.items():
      self.getContext().setHandler(key,edm)
      # add properties
      edm.dataframe = self._dataframe
      edm.tree  = self._t
      #edm.level = self._level
      edm.event = self._event
      edm.setContext(self.getContext())

      # enable hlt property by the container key name
      if 'HLT' in key:
        edm._is_hlt = True
          
      # set basepath into the root file
      if edm.useMetadataParams():
        edm.setMetadataParams( {'basepath':self._metadataInputFile[1].rsplit('/',1)[0],
                                 'file':self._metadataInputFile[0]} ) # remove the last name after '/' (tree name)
      # If initializations is failed, we must remove this from the container
      # service
      logger.info( f"Initialize the dataframe with name: {key}" )
      if(edm.initialize().isFailure()):
        logger.warning( f"Impossible to create the EDM: {key}")

    self.getContext().initialize()

    logger.info( 'Initializing all tools...')
    from trig_egamma_frame.kernel import ToolSvc as toolSvc
    for alg in toolSvc:
      if alg.status is StatusTool.DISABLE:
        continue
      # Retrieve all services
      #alg.level = self._level
      alg.setContext( self.getContext() )
      alg.setStoreGateSvc( self.getStoreGateSvc() )
      alg.dataframe = self._dataframe
      if alg.isInitialized():
        continue
      if alg.initialize().isFailure():
        logger.error( "Impossible to initialize the tool name: %s",alg.name)

    return StatusCode.SUCCESS




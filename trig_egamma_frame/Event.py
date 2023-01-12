
__all__ = ['ElectronLoop', 'PhotonLoop']


from trig_egamma_frame.core.macros      import *
from trig_egamma_frame.core             import StatusCode, StatusTool
from trig_egamma_frame.core             import TEventLoop
from trig_egamma_frame.enumerators      import Dataframe as DataframeEnum

#
# Electron loop
#
class ElectronLoop( TEventLoop ):

  def __init__(self, name , **kw):
    # Retrieve all information needed
    TEventLoop.__init__(self, name, **kw)


  #
  # Initialize all services
  #
  def initialize( self ):

    MSG_INFO( self, 'Initializing Event...')
    if super(ElectronLoop,self).initialize().isFailure():
      MSG_FATAL( self, "Impossible to initialize the TEventLoop services.")

    if self._dataframe is DataframeEnum.Run2:
      from trig_egamma_frame.c_struct import Electron_v1
      self._event = Electron_v1()
      from trig_egamma_frame.dataframe import Electron_v1      as Electron
      from trig_egamma_frame.dataframe import TrigEMCluster_v1 as TrigEMCluster
      from trig_egamma_frame.dataframe import TrigElectron_v1  as TrigElectron
      from trig_egamma_frame.dataframe import CaloCluster_v1   as CaloCluster
      from trig_egamma_frame.dataframe import TrackParticle_v1 as TrackParticle
      from trig_egamma_frame.dataframe import EmTauRoI_v1      as EmTauRoI
      from trig_egamma_frame.dataframe import EventInfo_v1     as EventInfo
      from trig_egamma_frame.dataframe import MonteCarlo_v1    as MonteCarlo
      from trig_egamma_frame.dataframe import Menu_v1          as Menu

    elif self._dataframe is DataframeEnum.Run3:
      
      from trig_egamma_frame.c_struct import Electron_v2
      self._event = Electron_v2()
      from trig_egamma_frame.dataframe import Electron_v2      as Electron
      from trig_egamma_frame.dataframe import TrigEMCluster_v1 as TrigEMCluster
      from trig_egamma_frame.dataframe import TrigElectron_v2  as TrigElectron
      from trig_egamma_frame.dataframe import CaloCluster_v2   as CaloCluster
      from trig_egamma_frame.dataframe import TrackParticle_v2 as TrackParticle
      from trig_egamma_frame.dataframe import EmTauRoI_v2      as EmTauRoI
      from trig_egamma_frame.dataframe import EventInfo_v2     as EventInfo
      from trig_egamma_frame.dataframe import MonteCarlo_v2    as MonteCarlo
      from trig_egamma_frame.dataframe import Menu_v1          as Menu

    else:
      return StatusCode.FATAL


    MSG_INFO( self, "Creating containers...")
    # Allocating containers


    # Initialize the base of this container.
    # Do not change this key names!
    self._containersSvc  = {
                            # event dataframe containers
                            'EventInfoContainer'         : EventInfo(),
                            'MonteCarloContainer'        : MonteCarlo(),
                            'CaloClusterContainer'       : CaloCluster(),
                            'MenuContainer'              : Menu(),
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
    if self._dataframe is DataframeEnum.Run2:
      from trig_egamma_frame.dataframe import TDT_v1 as TDT
      self._containersSvc.update({
                            # metadata containers
                            'HLT__TDT'                   : TDT(),
                            })


    # configure all EDMs needed
    for key, edm  in self._containersSvc.items():
      self.getContext().setHandler(key,edm)
      # add properties
      edm.dataframe = self._dataframe
      edm.tree  = self._t
      edm.level = self._level
      edm.event = self._event
      edm.setContext(self.getContext())

      # enable hlt property by the container key name
      if 'HLT' in key:
        edm.is_hlt = True

      # set basepath into the root file
      if edm.useMetadataParams():
        edm.setMetadataParams( {'basepath':self._metadataInputFile[1].rsplit('/',1)[0],
                                 'file':self._metadataInputFile[0]} ) # remove the last name after '/' (tree name)
      # If initializations is failed, we must remove this from the container
      # service
      MSG_INFO( self, "Initialize the dataframe with name: %s" , key )
      if(edm.initialize().isFailure()):
        MSG_WARNING( self, 'Impossible to create the EDM: %s',key)

    self.getContext().initialize()

    MSG_INFO( self, 'Initializing all tools...')
    from Gaugi import ToolSvc as toolSvc
    self._alg_tools = toolSvc.getTools()
    for alg in self._alg_tools:
      if alg.status is StatusTool.DISABLE:
        continue
      # Retrieve all services
      alg.level = self._level
      alg.setContext( self.getContext() )
      alg.setStoreGateSvc( self.getStoreGateSvc() )
      alg.dataframe = self._dataframe
      if alg.isInitialized():
        continue
      if alg.initialize().isFailure():
        MSG_FATAL( self, "Impossible to initialize the tool name: %s",alg.name)

    return StatusCode.SUCCESS




class PhotonLoop( TEventLoop ):

  def __init__(self, name , **kw):
    # Retrieve all information needed
    TEventLoop.__init__(self, name, **kw)


  #
  # Initialize all services
  #
  def initialize( self ):

    MSG_INFO( self, 'Initializing Event...')
    if super(Event,self).initialize().isFailure():
      MSG_FATAL( self, "Impossible to initialize the TEventLoop services.")

    if self._dataframe is DataframeEnum.Photon_v1:
      from trig_egamma_frame.dataframe import Photon_v1
      self._event = Photon_v1()
    else:
      return StatusCode.FATAL


    MSG_INFO( self, "Creating containers...")
    # Allocating containers
    from trig_egamma_frame.dataframe import Photon
    from trig_egamma_frame.dataframe import TrigEMCluster
    from trig_egamma_frame.dataframe import CaloCluster
    from trig_egamma_frame.dataframe import EmTauRoI
    from trig_egamma_frame.dataframe import EventInfo
    from trig_egamma_frame.dataframe import MonteCarlo
    from trig_egamma_frame.dataframe import TDT
    from ringer.kepler.trig_egamma_frame.dataframe import Menu_v1


    # Initialize the base of this container.
    # Do not change this key names!
    self._containersSvc  = {
                            # event dataframe containers
                            'EventInfoContainer'         : EventInfo(),
                            'MonteCarloContainer'        : MonteCarlo(),
                            'CaloClusterContainer'       : CaloCluster(),
                            'MenuContainer'              : Menu_v1(),
                           }

    self._containersSvc.update({
                            'HLT__TrigEMClusterContainer': TrigEMCluster(),
                            'HLT__CaloClusterContainer'  : CaloCluster(),
                            'HLT__EmTauRoIContainer'     : EmTauRoI(),
                            })

    self._containersSvc.update({  
                                  'PhotonContainer'      : Photon(),
                                  'HLT__PhotonContainer' : Photon(),
                                })

    # append TDT container
    if self._dataframe is DataframeEnum.Photon_v1:
      self._containersSvc.update({
                            # metadata containers
                            'HLT__TDT'                   : TDT(),
                            })


    # force the event id number for this event looper
    #self._containersSvc['EventInfoContainer'].setId( self.id() )
    # Add decoration for  event information
    self._containersSvc['EventInfoContainer'].setDecor( "is_fakes", True if 'fakes' in self._treePath else False)



    # configure all EDMs needed
    for key, edm  in self._containersSvc.items():
      self.getContext().setHandler(key,edm)
      # add properties
      edm.dataframe = self._dataframe
      edm.tree  = self._t
      edm.level = self._level
      edm.event = self._event
      edm.setContext(self.getContext())

      # enable hlt property by the container key name
      if 'HLT' in key:
        edm.hlt = True

      # set basepath into the root file
      if edm.useMetadataParams():
        edm.setMetadataParams( {'basepath':self._metadataInputFile[1].rsplit('/',1)[0],
                                 'file':self._metadataInputFile[0]} ) # remove the last name after '/' (tree name)
      # If initializations is failed, we must remove this from the container
      # service
      MSG_INFO( self, "Initialize the dataframe with name: %s" , key )
      if(edm.initialize().isFailure()):
        MSG_WARNING( self, 'Impossible to create the EDM: %s',key)

    self.getContext().initialize()

    MSG_INFO( self, 'Initializing all tools...')
    from Gaugi import ToolSvc as toolSvc
    self._alg_tools = toolSvc.getTools()
    for alg in self._alg_tools:
      if alg.status is StatusTool.DISABLE:
        continue
      # Retrieve all services
      alg.level = self._level
      alg.setContext( self.getContext() )
      alg.setStoreGateSvc( self.getStoreGateSvc() )
      alg.dataframe = self._dataframe
      if alg.isInitialized():
        continue
      if alg.initialize().isFailure():
        MSG_FATAL( self, "Impossible to initialize the tool name: %s",alg.name)

    return StatusCode.SUCCESS




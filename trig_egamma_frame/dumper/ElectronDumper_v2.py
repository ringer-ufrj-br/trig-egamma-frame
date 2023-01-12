
__all__ = ["ElectronDumper_v2"]


from trig_egamma_frame.dataframe import EgammaParameters

from trig_egamma_frame.core import Algorithm
from trig_egamma_frame.core import StatusCode
from trig_egamma_frame.core import save, load, declareProperty
from trig_egamma_frame.core.macros import *
from trig_egamma_frame.core.constants import GeV

import pandas as pd
import numpy as np
import collections
import math
import gc

from pprint import pprint
from prettytable import PrettyTable



#
# Electron
#
class ElectronDumper_v2( Algorithm ):


  #
  # constructor
  #
  def __init__(self, output, etbins, etabins, **kw ):
    
    Algorithm.__init__(self, "ElectronDumper")

    self.__etbins  = etbins
    self.__etabins = etabins
    self.output    = output
    self.features  = []
    self.__decorators = collections.OrderedDict({})
    self.__extra_features = list()
    self.__dataframe = None


 
  def __add__( self, key ):
    if type(key) is str:
      key = [key]
    self.__extra_features.extend( key )
    return self


  def decorate( self, key , f):
    self.__decorators[key] = f


  #
  # Initialize dumper
  #
  def initialize(self):

    Algorithm.initialize(self)

    self.features.extend(['et_bin', 'eta_bin'])

    #
    # Event info
    #
    self.features.extend( ['avgmu'] )

    #
    # Fast calo
    #
    self.features.extend( [
                                'trig_L2_cl_et',
                                'trig_L2_cl_eta',
                                'trig_L2_cl_phi',
                                'trig_L2_cl_reta',
                                'trig_L2_cl_ehad1', 
                                'trig_L2_cl_eratio',
                                'trig_L2_cl_f1', 
                                'trig_L2_cl_f3', 
                                'trig_L2_cl_weta2', 
                                'trig_L2_cl_wstot', 
                                'trig_L2_cl_e2tsts1'
                                ] )

    # Add fast calo ringsE
    self.features.extend( [ 'trig_L2_cl_ring_%d'%r for r in range(100) ] )


    #
    # Fast electron
    #
    self.features.extend( [
                                'trig_L2_el_hastrack',
                                'trig_L2_el_trkClusDeta',
                                'trig_L2_el_trkClusDphi',
                                'trig_L2_el_etOverPt',
                                'trig_L2_el_d0',
                                ] )

    #
    # Offline variables
    #
    self.features.extend( [
                                'el_lhtight',
                                'el_lhmedium',
                                'el_lhloose',
                                'el_lhvloose',
                                ] )


    self.features.extend( self.__decorators.keys() )
    self.features.extend( self.__extra_features )

    return StatusCode.SUCCESS


  #
  # fill current event
  #
  def fill( self, row ):
    dataframe = {}
    if self.__dataframe is None:
      self.__dataframe = collections.OrderedDict({})
      for idx, col in enumerate(self.features):
        self.__dataframe[col] = [row[idx]]
    else:
      for idx, col in enumerate(self.features):
        self.__dataframe[col].append(row[idx])


  #
  # execute 
  #
  def execute(self, context):

    event_row = list()

    #
    # event info
    #
    eventInfo = context.getHandler( "EventInfoContainer" )

    #
    # Fast Calo features
    #
    fc = context.getHandler( "HLT__TrigEMClusterContainer" )

    etBinIdx, etaBinIdx = self.__get_bin( fc.et()/GeV, abs(fc.eta()) )
    if etBinIdx < 0 or etaBinIdx < 0:
      return StatusCode.SUCCESS

      

    event_row.append( etBinIdx )
    event_row.append( etaBinIdx )
    event_row.append( eventInfo.avgmu() )
    event_row.append( fc.et()       )
    event_row.append( fc.eta()      )
    event_row.append( fc.phi()      )
    event_row.append( fc.reta()     )
    event_row.append( fc.ehad1()    )
    event_row.append( fc.eratio()   )
    event_row.append( fc.f1()       )
    event_row.append( fc.f3()       )
    event_row.append( fc.weta2()    )
    event_row.append( fc.wstot()    )
    event_row.append( fc.e2tsts1()  )
    event_row.extend( fc.ringsE()   )
   
    #
    # Fast electron features
    #
    # Save only the closest fast track object cluster-trk
    fcElCont = context.getHandler("HLT__TrigElectronContainer" )

    hasFcTrack = True if fcElCont.size()>0 else False
    if hasFcTrack:
      fcElCont.setToBeClosestThanCluster()
      event_row.append( True )
      event_row.append( fcElCont.trkClusDeta() )  
      event_row.append( fcElCont.trkClusDphi() )
      event_row.append( fcElCont.etOverPt() )
      event_row.append( fcElCont.d0() )
    else:
      event_row.extend( [False, -1.0, -1.0, -1.0, -1.0] )



    #
    # Offline variables
    #
    elCont = context.getHandler( "ElectronContainer" )

    # Adding Offline PID LH decisions
    event_row.append( elCont.accept( "el_lhtight"  ) )
    event_row.append( elCont.accept( "el_lhmedium" ) )
    event_row.append( elCont.accept( "el_lhloose"  ) )
    event_row.append( elCont.accept( "el_lhvloose" ) )
 
    #
    # Decorate from external funcions by the client. Can be any type
    #
    for feature, func, in self.__decorators.items():
      event_row.append( func(context) )

    #
    # Decorate with other decisions from emulator service
    #
    dec = context.getHandler("MenuContainer")
    for feature in self.__extra_features:
      passed = dec.accept(feature).getCutResult('Pass')
      event_row.append( passed )

    if len(event_row) != len( self.features ):
      MSG_FATAL( "This event missing some column. We have some problem into the dumper code! please, verify it!")


    self.fill(event_row)
    return StatusCode.SUCCESS



  #
  # Finalize method
  #
  def finalize( self ):
    if self.__dataframe:
      MSG_INFO(self, "Save dataframe into %s", self.output)
      df = pd.DataFrame(self.__dataframe)
      df.to_pickle(self.output)
    return StatusCode.SUCCESS




  def __get_bin(self,et,eta):
    # Fix eta value if > 2.5
    if eta > self.__etabins[-1]:  eta = self.__etabins[-1]
    if et > self.__etbins[-1]:  et = self.__etbins[-1]
    ### Loop over binnings
    for etBinIdx in range(len(self.__etbins)-1):
      if et >= self.__etbins[etBinIdx] and  et < self.__etbins[etBinIdx+1]:
        for etaBinIdx in range(len(self.__etabins)-1):
          if eta >= self.__etabins[etaBinIdx] and eta < self.__etabins[etaBinIdx+1]:
            return etBinIdx, etaBinIdx
    return -1, -1#
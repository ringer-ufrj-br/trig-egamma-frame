
__all__ = ['L2Electron']


from egamma.core import Messenger
from egamma.core.macros  import *
from egamma.core import declareProperty, StatusCode
from egamma import GeV

import numpy as np
import math


#
# Hypo self.hypo
#
class L2Electron(Messenger):


  #
  # Constructor
  #
  def __init__(self, name, **kw):

    Messenger.__init__(self, name)
    self.name = name
    declareProperty( self, kw, "EtCut"               ,   0      )
    declareProperty( self, kw, "TrackPt"             ,   0      )
    declareProperty( self, kw, "CaloTrackdETA"       ,   0.2    )
    declareProperty( self, kw, "CaloTrackdPHI"       ,   0.3    )
    declareProperty( self, kw, "CaloTrackdEoverPLow" ,   0      )
    declareProperty( self, kw, "CaloTrackdEoverPHigh",   999    )
    declareProperty( self, kw, "TRTRatio"            ,   -999   )
    declareProperty( self, kw, "d0Cut"               ,   -999   )
    declareProperty( self, kw, "DoLRT"               , False    )

  #
  # Initialize method
  #
  def initialize(self):
    return StatusCode.SUCCESS


  #
  # Finalize method
  #
  def finalize(self):
    return StatusCode.SUCCESS


  #
  # Accept method
  #
  def accept( self, context ):

    elCont = context.getHandler( "HLT__TrigElectronContainer" )
    current = elCont.getPos()

    bitAccept = [False for _ in range(elCont.size())]

    for el in elCont:
      # Retrieve all quantities
      dPhiCalo    = el.trkClusDphi()
      dEtaCalo    = el.trkClusDeta()
      pTcalo      = el.pt()
      eTOverPt    = el.etOverPt()
      NTRHits     = el.numberOfTRTHits()
      NStrawHits  = el.numberOfTRTHiThresholdHits()
      TRTHitRatio = 1e10 if NStrawHits==0 else NTRHits/float(NStrawHits)
      d0          = el.d0()
      # apply cuts

      passed = False

      if (pTcalo > self.TrackPt):
        if (dEtaCalo < self.CaloTrackdETA):
          if (dPhiCalo < self.CaloTrackdPHI):
            if(eTOverPt >  self.CaloTrackdEoverPLow ):
              if ( eTOverPt < self.CaloTrackdEoverPHigh ):
                if (TRTHitRatio > self.TRTRatio):
                  if self.DoLRT and d0 > self.d0Cut:
                    passed = True
                    MSG_DEBUG( self,  "Event LRT accepted !" )
                  else:
                    # TrigElectron passed all cuts: set flags
                    passed = True
                    MSG_DEBUG( self,  "Event accepted !" )
                #TRTHitRatio
              #etOverPt
            #dphi
          #deta
        #pt
      #apply cuts

      bitAccept[el.getPos()] = passed

    # Loop over electrons

    elCont.setPos( current )
    # got this far => passed!
    passed = any( bitAccept )
    return Accept( self.name, [("Pass", passed)] )





#
# For electrons
#
class L2ElectronConfiguration(Messenger):

  __operation_points  = [  'tight'    , 
                           'medium'   , 
                           'loose'    , 
                           'vloose'   , 
                           'lhtight'  , 
                           'lhmedium' , 
                           'lhloose'  , 
                           'lhvloose' ,
                           'mergedtight',
                           'dnntight' ,  
                           'dnnmedium',
                           'dnnloose' ,
                           'dnnvloose',
                           ]

  __trigElectronLrtd0Cut = { 'lrtloose' :2.0,
                             'lrtmedium':3.0,
                             'lrttight' :5.0
                           }

  def __init__(self, name, cpart):

    Messenger.__init__(self)

    self.__threshold  = cpart['threshold']
    self.__sel        = cpart['addInfo'][0] if cpart['addInfo'] else cpart['IDinfo']
    self.__idperfInfo = cpart['idperfInfo']
    self.__lrtInfo    = cpart['lrtInfo']
    self.hypo         = L2Electron(name)
    self.hypo.AcceptAll            = False
    self.hypo.TrackPt              = 0.0
    self.hypo.CaloTrackdETA        = 0.2
    self.hypo.CaloTrackdPHI        = 990.
    self.hypo.CaloTrackdEoverPLow  = 0.0
    self.hypo.CaloTrackdEoverPHigh = 999.0
    self.hypo.TRTRatio             = -999.
    
    MSG_INFO(self, 'Threshold :%s', self.__threshold )
    MSG_INFO(self, 'Pidname   :%s', self.__sel )


  def etthr(self):
    return self.__threshold

  def lrtInfo(self):
    return self.__lrtInfo
  
  def idperfInfo(self):
    return self.__idperfInfo

  def nocut(self):
    self.hypo.AcceptAll = True


  def nominal(self):
    if self.etthr() < 15:
      self.hypo.TrackPt = 1.0 * GeV 
    elif self.etthr() >= 15 and self.etthr() < 20:
      self.hypo.TrackPt = 2.0 * GeV 
    elif self.etthr() >= 20 and self.etthr() < 50:
      self.hypo.TrackPt =  3.0 * GeV 
    elif self.etthr() >= 50:
      self.hypo.TrackPt =  5.0 * GeV 
      self.hypo.CaloTrackdETA =  999. 
      self.hypo.CaloTrackdPHI =  999.


  def addLRTCut(self):
    self.hypo.DoLRT = True
    self.hypo.d0Cut=self.__trigElectronLrtd0Cut[self.lrtInfo()]


  #
  # Compile the chain
  #
  def compile(self):
    if 'idperf' in self.idperfInfo():
      MSG_INFO(self, "Configure nocut...")
      self.nocut()
    else:
      MSG_INFO(self, "Configure nominal...")
      self.nominal()
    # secondary extra cut
    if self.lrtInfo() in self.__trigElectronLrtd0Cut.keys():
      MSG_INFO(self, "Adding LRT cuts...")
      self.addLRTCut()



def configure(name, chainPart):
  config = L2ElectronConfiguration(name, chainPart)
  config.compile()
  return config.hypo

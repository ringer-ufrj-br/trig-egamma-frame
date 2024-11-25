

__all__ = []


from egamma.core import Messenger
from egamma.core.macros  import *
from egamma.core import declareProperty, StatusCode
from egamma.emulator import Accept
from egamma.emulator.run3.electron import L2CaloCutMaps
from egamma.emulator.run3.ringer import RingerSelector
from egamma.emulator.run3.menu import electronFlags, treat_pidname
from egamma import GeV
from ROOT import TEnv

import os
import numpy as np
import math

def same(value):
    return [value]*9

    
#
# L2Calo hypo self.hypo
#
class L2Calo(Messenger):

  #
  # Constructor
  #
  def __init__(self, name, **kw):

    Messenger.__init__(self)
    self.name = name

    declareProperty( self, kw, "AcceptAll"      , False                               )
    declareProperty( self, kw, "UseRinger"      , False                               )
    declareProperty( self, kw, "EtaBins"        , [0.0, 0.6, 0.8, 1.15, 1.37, 1.52, 1.81, 2.01, 2.37, 2.47] )
    declareProperty( self, kw, "ETthr"          , same(0)                             )
    declareProperty( self, kw, "dETACLUSTERthr" , 0.1                                 )
    declareProperty( self, kw, "dPHICLUSTERthr" , 0.1                                 )
    declareProperty( self, kw, "F1thr"          , same(0.005)                         )
    declareProperty( self, kw, "ET2thr"         , same(90.0*GeV)                      )
    declareProperty( self, kw, "HADET2thr"      , same(999.0)                         )
    declareProperty( self, kw, "HADETthr"       , same(999.0)                         )
    declareProperty( self, kw, "WETA2thr"       , same(99999.)                        )
    declareProperty( self, kw, "WSTOTthr"       , same(99999.)                        )
    declareProperty( self, kw, "F3thr"          , same(99999.)                        )
    declareProperty( self, kw, "CARCOREthr"     , same(999.0)                         )
    declareProperty( self, kw, "CAERATIOthr"    , same(999.0)                         )
    declareProperty( self, kw, "ConfigPath"     , None                                )
    declareProperty( self, kw, "EtCut"          , -999                                )



  #
  # Initialize method
  #
  def initialize(self): 

    if self.UseRinger:
      MSG_INFO(self, f"Loading ringer models from {self.ConfigPath}")
      self.ringer = RingerSelector(ConfigPath=self.ConfigPath)
      if self.ringer.initialize().isFailure():
        MSG_FATAL(self, "Its not possible to initialize the ringer selector.")

    return StatusCode.SUCCESS



  #
  # Finalize method
  #
  def finalize(self):
    return StatusCode.SUCCESS


  #
  # Accept method
  #
  def accept(self, context):

    if self.UseRinger:
      passed = self.emulate_ringer(context)
    else:
      passed = self.emulate(context)

    return Accept( self.name, [ ("Pass", passed)] )



  #
  # Emulation method
  #
  def emulate(self, context):



    pClus = context.getHandler( "HLT__TrigEMClusterContainer" )
    # get the equivalent L1 EmTauRoi object in athena
    emTauRoi = pClus.emTauRoI()
    PassedCuts=0

    # fill local variables for RoI reference position
    phiRef = emTauRoi.phi()
    etaRef = emTauRoi.eta()

    if abs(etaRef) > 2.6:
      MSG_DEBUG(self, 'The cluster had eta coordinates beyond the EM fiducial volume.')
      return False

    if self.AcceptAll:
      MSG_DEBUG(self, "Accept all.")
      return True

    # correct phi the to right range (probably not needed anymore)
    if  math.fabs(phiRef) > np.pi: phiRef -= 2*np.pi; # correct phi if outside range

    absEta = math.fabs( pClus.eta() )
    etaBin = -1
    if absEta > self.EtaBins[-1]:
      absEta=self.EtaBins[-1]
    # get the corrct eta bin range
    for idx, value in enumerate(self.EtaBins):
      if ( absEta > self.EtaBins[idx] and absEta < self.EtaBins[idx+1] ):
        etaBin = idx

    # Is in crack region?
    inCrack = True if (absEta > 2.37 or (absEta > 1.37 and absEta < 1.52)) else False

    # Deal with angle diferences greater than Pi
    dPhi =  math.fabs(pClus.phi() - phiRef)
    dPhi = dPhi if (dPhi < np.pi) else  (2*np.pi - dPhi)

    # calculate cluster quantities // definition taken from TrigElectron constructor
    if ( pClus.emaxs1() + pClus.e2tsts1() ) > 0 :
      energyRatio = ( pClus.emaxs1() - pClus.e2tsts1() ) / float( pClus.emaxs1() + pClus.e2tsts1() )

    # (VD) here the definition is a bit different to account for the cut of e277 @ EF
    if ( pClus.e277()!= 0.):
      rCore = pClus.e237() / float(pClus.e277())

    # fraction of energy deposited in 1st sampling
    #if ( math.fabs(pClus.energy()) > 0.00001) :
    #  F1 = (pClus.energy(CaloSampling.EMB1)+pClus.energy(CaloSampling.EME1))/float(pClus.energy())
    F1 = pClus.f1()

    eT_T2Calo  = float(pClus.et())

    if ( eT_T2Calo!=0 and pClus.eta()!=0 ):
      hadET_T2Calo = pClus.ehad1()/math.cosh(math.fabs(pClus.eta()))/eT_T2Calo

    # extract Weta2 varable
    Weta2 = pClus.weta2()
    # extract Wstot varable
    Wstot = pClus.wstot()

    # extract F3 (backenergy i EM calorimeter
    #e0 = pClus.energy(CaloSampling.PreSamplerB) + pClus.energy(CaloSampling.PreSamplerE)
    #e1 = pClus.energy(CaloSampling.EMB1) + pClus.energy(CaloSampling.EME1)
    #e2 = pClus.energy(CaloSampling.EMB2) + pClus.energy(CaloSampling.EME2)
    #e3 = pClus.energy(CaloSampling.EMB3) + pClus.energy(CaloSampling.EME3)
    #eallsamples = float(e0+e1+e2+e3)
    #F3 = e3/eallsamples if math.fabs(eallsamples)>0. else 0.
    F3 = pClus.f3()
    # apply cuts: DeltaEta(clus-ROI)
    if ( math.fabs(pClus.eta() - etaRef) > self.dETACLUSTERthr ):
      return False

    PassedCuts+=1  #Deta

    # DeltaPhi(clus-ROI)
    if ( dPhi > self.dPHICLUSTERthr ):
      MSG_DEBUG(self, 'dphi > dphicluster')
      return False

    PassedCuts+=1 #DPhi

    # eta range
    if ( etaBin==-1 ):  # VD
      MSG_DEBUG(self, "Cluster eta: %1.3f  outside eta range ",absEta )
      return False
    else:
      MSG_DEBUG(self, "eta bin used for cuts ")

    PassedCuts+=1 # passed eta cut

    # Rcore
    if ( rCore < self.CARCOREthr[etaBin] ):  return False
    PassedCuts+=1 # Rcore

    # Eratio
    if ( inCrack or F1<self.F1thr[etaBin] ):
      MSG_DEBUG(self, "TrigEMCluster: InCrack= %d F1=%1.3f",inCrack,F1 )
    else:
      if ( energyRatio < self.CAERATIOthr[etaBin] ): return False

    PassedCuts+=1 # Eratio
    if(inCrack): energyRatio = -1; # Set default value in crack for monitoring.

    # ET_em
    if ( eT_T2Calo < self.ETthr[etaBin]): return False

    PassedCuts+=1 # ET_em

    hadET_cut = 0.0
    # find which ET_had to apply : this depends on the ET_em and the eta bin
    if ( eT_T2Calo >  self.ET2thr[etaBin] ):
      hadET_cut = self.HADET2thr[etaBin]
    else:
      hadET_cut = self.HADETthr[etaBin]

    # ET_had
    if ( hadET_T2Calo > hadET_cut ): return False
    PassedCuts+=1 #ET_had
    # F1
    # if ( F1 < m_F1thr[0]) return true;  //(VD) not cutting on this variable, only used to select whether to cut or not on eRatio
    PassedCuts+=1 # F1
    # Weta2
    if ( Weta2 > self.WETA2thr[etaBin]): return False
    PassedCuts+=1 # Weta2
    # Wstot
    if ( Wstot >= self.WSTOTthr[etaBin]): return False
    PassedCuts+=1 # Wstot
    # F3
    if ( F3 > self.F3thr[etaBin]): return False
    PassedCuts+=1 # F3
    # got this far => passed!
    MSG_DEBUG(self, 'T2Calo emulation approved...')
    return True



  #
  # Emulate ringer decision
  #
  def emulate_ringer(self, context):

    fc = context.getHandler("HLT__TrigEMClusterContainer")
    et = fc.et() # in GeV

    if self.AcceptAll:
      MSG_DEBUG(self, "Accept all")
      return True

    if et < self.EtCut:
      return False

    return self.ringer.emulate(context)






#
# For electron and photons auto configuration
#




class L2CaloConfiguration(Messenger):

  __operation_points  = [  'tight'    , 
                           'medium'   , 
                           'loose'    , 
                           'vloose'   , 
                           'lhtight'  , 
                           'lhmedium' , 
                           'lhloose'  , 
                           'lhvloose' ,
                           'dnntight' ,
                           'dnnmedium',
                           'dnnloose' ,
                           'dnnvloose',
                           ]


  def __init__(self, name, cpart):
    Messenger.__init__(self)

    self.__cand          = cpart['trigType']
    self.__threshold     = cpart['threshold']
    self.__sel           = 'ion' if 'ion' in cpart['extra'] else (cpart['addInfo'][0] if cpart['addInfo'] else cpart['IDinfo'])
    self.__gsfinfo       = cpart['gsfInfo'] if cpart['trigType']=='e' and cpart['gsfInfo'] else ''
    self.__idperfinfo    = cpart['idperfInfo'] if cpart['trigType']=='e' and cpart['idperfInfo'] else ''
    self.__noringerinfo  = cpart['L2IDAlg']
    self.__ringerVersion = cpart['rVersion'] if 'rVersion' in cpart.keys() else None

    self.hypo = L2Calo(name)
    self.hypo.AcceptAll      = False
    self.hypo.UseRinger      = False
    self.hypo.EtaBins        = [0.0, 0.6, 0.8, 1.15, 1.37, 1.52, 1.81, 2.01, 2.37, 2.47]
    self.hypo.ETthr          = same( self.__threshold*GeV )
    self.hypo.dETACLUSTERthr = 0.1
    self.hypo.dPHICLUSTERthr = 0.1
    self.hypo.F1thr          = same( 0.005    )
    self.hypo.ET2thr         = same( 90.0*GeV )
    self.hypo.HADET2thr      = same( 999.0    )
    self.hypo.HADETthr       = same( 0.058    )
    self.hypo.WETA2thr       = same( 99999.   )
    self.hypo.WSTOTthr       = same( 99999.   )
    self.hypo.F3thr          = same( 99999.   )
    self.hypo.CARCOREthr     = same( -9999.   )
    self.hypo.CAERATIOthr    = same( -9999.   )

    MSG_INFO(self, 'Signature :%s'   , self.__cand )
    MSG_INFO(self, 'Threshold :%s'   , self.__threshold )
    MSG_INFO(self, 'Pidname   :%s'   , self.__sel )
    MSG_INFO(self, 'noringerinfo :%s', self.__noringerinfo )


  def pidname( self ):
    return self.__sel

  def etthr(self):
    return self.__threshold

  def isElectron(self):
    return 'e' in self.__cand

  def isPhoton(self):
    return 'g' in self.__cand

  def noringerinfo(self):
    return self.__noringerinfo

  def gsfinfo(self):
    return self.__gsfinfo

  def idperfinfo(self):
    return self.__idperfinfo


  def nocut(self):
    
    MSG_INFO(self, 'Configure nocut' )
    self.hypo.AcceptAll      = True
    self.hypo.UseRinger      = False
    self.hypo.ETthr          = same( self.etthr()*GeV )
    self.hypo.dETACLUSTERthr = 9999.
    self.hypo.dPHICLUSTERthr = 9999.
    self.hypo.F1thr          = same( 0.0    )
    self.hypo.HADETthr       = same( 9999.  )
    self.hypo.CARCOREthr     = same( -9999. )
    self.hypo.CAERATIOthr    = same( -9999. )


  def etcut(self):

    MSG_INFO(self, 'Configure etcut or nopid' )
    self.hypo.UseRinger      = False
    self.hypo.ETthr          = same( ( self.etthr()  -  3 )*GeV )
    self.hypo.dETACLUSTERthr = 9999.
    self.hypo.dPHICLUSTERthr = 9999.
    self.hypo.F1thr          = same( 0.0    )
    self.hypo.HADETthr       = same( 9999.  )
    self.hypo.CARCOREthr     = same( -9999. )
    self.hypo.CAERATIOthr    = same( -9999. )


  def noringer(self):

    MSG_INFO(self, 'Configure noringer' )
    self.hypo.UseRinger   = False
    self.hypo.ETthr       = same( ( self.etthr()  - 3 )*GeV )
    self.hypo.HADETthr    = L2CaloCutMaps( self.etthr() ).MapsHADETthr[self.pidname()]
    self.hypo.CARCOREthr  = L2CaloCutMaps( self.etthr() ).MapsCARCOREthr[self.pidname()]
    self.hypo.CAERATIOthr = L2CaloCutMaps( self.etthr() ).MapsCAERATIOthr[self.pidname()]


  def nominal(self):

    MSG_INFO(self, 'Configure ringer' )
    self.hypo.UseRinger = True
    self.hypo.EtCut     = (self.etthr()-3.)*GeV  
    if not self.pidname() in self.__operation_points:
      MSG_FATAL(self, f"Bad selection name: {self.pidname()}")
    
    opnames = {
      'tight' : 'Tight',
      'medium': 'Medium',
      'loose' : 'Loose',
      'vloose': 'VeryLoose',
    }

    # setup the electron ringer abspath
    path = os.path.join(
      electronFlags.ringerVersion[self.__ringerVersion],
      'ElectronRinger{op}TriggerConfig.conf'.format(op=opnames[treat_pidname(self.pidname())])
    )
    # Configure ringer here
    self.hypo.ConfigPath = path



  #
  # compile the chain
  #
  def compile(self):

    if self.pidname() in ('etcut', 'ion', 'nopid'):
      self.etcut()

    elif self.pidname() in self.__operation_points and 'noringer' in self.noringerinfo() and self.isElectron():
      self.noringer()

    elif self.pidname() in self.__operation_points and 'noringer' not in self.noringerinfo() and self.isElectron():
      self.nominal()

    elif self.pidname() in self.__operation_points and self.isPhoton() and  'ringer'!=self.noringerinfo():
      self.etcut()
    elif self.pidname() in self.__operation_points and self.isPhoton() and  'ringer'==self.noringerinfo():
      self.nominal()
   
    elif self.etthr()==0:
      self.nocut()





#
# Configure the hypo from trigger name
#
def configure( name, chainPart):

  config = L2CaloConfiguration(name, chainPart)
  config.compile()
  return config.hypo


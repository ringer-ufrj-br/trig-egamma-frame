
__all__ = ['TrigEgammaPrecisionElectronHypoTool']

from egamma.core import Messenger
from egamma.core.macros  import *
from egamma.core import declareProperty, StatusCode
from egamma.emulator import Accept
from egamma import GeV

import numpy as np
import math

def same( val , tool):
  return [val]*( len( tool.EtaBins ) - 1 )



#
# Hypo tool
#
class PrecisionElectron( Messenger ):


  #
  # Constructor
  #
  def __init__(self, name, **kw):

    Messenger.__init__(self)
    self.name = name
    declareProperty( self, kw, "RelPtConeCut"         , -1       )
    declareProperty( self, kw, "AcceptAll"            , False    )
    declareProperty( self, kw, "ETthr"                ,   0      )
    declareProperty( self, kw, "dPHICLUSTERthr"       ,   0      )
    declareProperty( self, kw, "dETACLUSTERthr"       ,   0.2    )
    declareProperty( self, kw, "PidName"              , ""       )
    declareProperty( self, kw, "d0Cut"                , -1       )
    declareProperty( self, kw, "DoNoPid"              , False    )



  #
  # Initialize method
  #
  def initialize(self):
    return StatusCode.SUCCESS


  #
  # Accept method
  # 
  def accept(self, context):

    elCont = context.getHandler("HLT__ElectronContainer")
    pClus = context.getHandler( "HLT__TrigEMClusterContainer" )

    current = elCont.getPos()
    bitAccept = [False for _ in range(elCont.size())]

    # get the equivalent L1 EmTauRoi object in athena
    emTauRoI = pClus.emTauRoI()

    for el in elCont:
      passed = self.emulate(el, emTauRoI)
      bitAccept[el.getPos()] = passed
    # Loop over all electrons

    elCont.setPos( current )
    # got this far => passed!
    passed = any( bitAccept )

    return Accept( self.name, [ ("Pass", passed) ] )


  def emulate(self, el, roi):

    passed = False

    # fill local variables for RoI reference position
    phiRef = roi.phi()
    etaRef = roi.eta()

    # correct phi the to right range (probably not needed anymore)
    if  math.fabs(phiRef) > np.pi: phiRef -= 2*np.pi # correct phi if outside range

    if self.AcceptAll:
      return True


    if abs(etaRef) > 2.6:
      MSG_DEBUG(self, 'The cluster had eta coordinates beyond the EM fiducial volume.')
      return False

    # calo cluster
    cl = el.caloCluster()
    trk = el.trackParticle()

    deta = abs(etaRef - cl.eta())
    dphi = abs(phiRef - cl.phi())

    if math.fabs(dphi) > np.pi: dphi -= 2*np.pi

    if deta > self.dETACLUSTERthr:
      return False
      
    if dphi > self.dPHICLUSTERthr:   
      return False

    if cl.et() < self.ETthr:
      return False

    if self.DoNoPid:
      return True

    # LRT cut
    if self.d0Cut > 0.0:
      d0 = trk.d0()
      if d0 < self.d0Cut:
        return False

    # Pid cut
    if not el.accept('trig_EF_el_'+self.PidName):
      return False

    ptvarcone20 = el.ptvarcone20()
    relptvarcone20 = ptvarcone20/el.pt()

    if self.RelPtConeCut < -100:
      MSG_DEBUG(self, "not applying isolation. Returning NOW")
      return True


    if relptvarcone20 > self.RelPtConeCut:
      return False

    # Pass all cuts
    return True


  #
  # Finalize method
  #
  def finalize(self):
    return StatusCode.SUCCESS




class PrecisionElectronConfiguration(Messenger):


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
                           'mergedtight',
                           'nopid',
                           ]

  __operation_points_lhInfo = [
        'nopix'
        ]

  __operation_points_gsfInfo = [
        'nogsf'
        ]

  # isolation cuts:w
  __isolationCut = {
        None: None,
        'ivarloose': 0.1,
        'ivarmedium': 0.065,
        'ivartight': 0.05
        }

  # LRT d0 cuts
  __lrtD0Cut = {
      '': -1.,
      None: None,
      'lrtloose':2.0,
      'lrtmedium':3.0,
      'lrttight':5.
      }


  def __init__(self, name, cpart):

    Messenger.__init__(self)
    self.__threshold  = cpart['threshold']
    self.__sel        = cpart['addInfo'][0] if cpart['addInfo'] else cpart['IDinfo']
    self.__iso        = cpart['isoInfo']
    self.__d0         = cpart['lrtInfo']
    self.__gsfInfo    = cpart['gsfInfo']
    self.__lhInfo     = cpart['lhInfo']
    

    self.hypo = PrecisionElectron(name)
    self.hypo.ETthr          = self.__threshold*GeV
    self.hypo.dETACLUSTERthr = 0.1
    self.hypo.dPHICLUSTERthr = 0.1
    self.hypo.RelPtConeCut   = -999
    self.hypo.PidName        = ""
    self.hypo.d0Cut          = -1
    self.hypo.AcceptAll      = False
    self.hypo.DoNoPid        = False

    MSG_INFO(self, f'Electron_Threshold :{self.__threshold}' )
    MSG_INFO(self, f'Electron_Pidname   :{self.pidname()}' )
    MSG_INFO(self, f'Electron_iso       :{self.__iso}' )
    MSG_INFO(self, f'Electron_d0        :{self.__d0}' )


  #
  # Get the pidname
  #
  def pidname( self ):
    # if LLH, we should append the LH extra information if exist
    return self.__sel

  def etthr(self):
    return self.__threshold

  def isoInfo(self):
    return self.__iso

  def d0Info(self):
    return self.__d0

  def gsfInfo(self):
    return self.__gsfInfo

  def nocut(self):

    MSG_INFO(self, 'Configure nocut' )
    self.hypo.ETthr          = self.etthr()*GeV
    self.hypo.dETACLUSTERthr = 9999.
    self.hypo.dPHICLUSTERthr = 9999.

  def noPid(self):
    
    MSG_INFO(self, 'Configure noPid' )
    self.hypo.DoNoPid        = True
    self.hypo.ETthr          = self.etthr()*GeV
    # No other cuts applied
    self.hypo.dETACLUSTERthr = 9999.
    self.hypo.dPHICLUSTERthr = 9999.

  #
  # LRT extra cut
  #
  def addLRTCut(self):
    if not self.d0Info() in self.__lrtD0Cut:
      MSG_FATAL(self, f"Bad LRT selection name: {self.d0Info()}")
    self.__tool.d0Cut = self.__lrtD0Cut[self.d0Info()]

  def acceptAll(self):
     self.hypo.AcceptAll = True
  #
  # Isolation extra cut
  #
  def addIsoCut(self):
    if not self.isoInfo() in self.__isolationCut:
      MSG_FATAL(self, f"Bad Iso selection name: {self.isoInfo()}")
    self.hypo.RelPtConeCut = self.__isolationCut[self.isoInfo()]

  def nominal(self):
    if not self.pidname() in self.__operation_points:
      MSG_FATAL(self, "Bad selection name: %s" % self.pidname())
    self.hypo.PidName = self.pidname()

  
  #
  # Compile the chain
  #
  def compile(self):

    if 'nocut' == self.pidname():
      MSG_INFO(self, "Configure nocut...")
      self.nocut()
    elif 'nopid' == self.pidname():
      MSG_INFO(self, "Configure nopid...")
      self.noPid()
    else: # nominal chain using pid selection
      MSG_INFO(self, "Configure nominal...")
      self.nominal()


    # secundary cut configurations
    if self.isoInfo() and self.isoInfo()!="":
      MSG_INFO(self, "Adding IsoCut...")
      self.addIsoCut()
    if self.d0Info() and self.d0Info()!="":
      MSG_INFO(self, "Adding LRTCut...")
      self.addLRTCut()
    

def configure(name, chainPart):
  config = PrecisionElectronConfiguration(name, chainPart)
  config.compile()
  return config.hypo


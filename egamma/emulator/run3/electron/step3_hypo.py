__all__ = []

from egamma.core import Messenger
from egamma.core.macros  import *
from egamma.core import declareProperty, StatusCode
from egamma.emulator import Accept
from egamma import GeV


import numpy as np
import math


#
# Hypo tool
#
class PrecisionCalo( Messenger):


  #
  # Constructor
  #
  def __init__(self, name, **kw):

    Messenger.__init__(self, name)
    self.name = name

    declareProperty( self, kw, "AcceptAll"            , False    )
    declareProperty( self, kw, "ETthr"                ,   0      )
    #declareProperty( self, kw, "ET2thr"               ,   0      )
    declareProperty( self, kw, "dPHICLUSTERthr"       ,   0      )
    declareProperty( self, kw, "dETACLUSTERthr"       ,   0.2    )


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

    clCont = context.getHandler( "HLT__CaloClusterContainer" )
    current = clCont.getPos()

    pClus = context.getHandler( "HLT__TrigEMClusterContainer" )
    # get the equivalent L1 EmTauRoi object in athena
    emTauRoi = pClus.emTauRoI()
    
    # fill local variables for RoI reference position
    phiRef = emTauRoi.phi()
    etaRef = emTauRoi.eta()

    if abs(etaRef) > 2.6:
      MSG_DEBUG(self, 'The cluster had eta coordinates beyond the EM fiducial volume.')
      return False
    
    # correct phi the to right range (probably not needed anymore)
    if  math.fabs(phiRef) > np.pi: phiRef -= 2*np.pi # correct phi if outside range


    bitAccept = [False for _ in range(clCont.size())]

    for cl in clCont:

      passed = False
      deta = abs(etaRef - cl.eta())
      dphi = abs(phiRef - cl.phi())
      if math.fabs(dphi) > np.pi: dphi -= 2*np.pi

      if deta < self.dETACLUSTERthr:
        if dphi < self.dPHICLUSTERthr:        
          if cl.et() > self.ETthr:
            passed=True

      bitAccept[cl.getPos()] = passed
    # Loop over cluster

    clCont.setPos( current )
    # got this far => passed!
    passed = any( bitAccept )
    return Accept( self.name, [("Pass", passed)] )





def configure(name, cpart):

    threshold = cpart['threshold']
    sel = 'ion' if 'ion' in cpart['extra'] else (cpart['addInfo'][0] if cpart['addInfo'] else cpart['IDinfo'])
    
    hypo = PrecisionCalo(name)
    hypo.EtaBins = [0.0, 0.6, 0.8, 1.15, 1.37, 1.52, 1.81, 2.01, 2.37, 2.47]
    def same( val ):
        return [val]*( len( hypo.EtaBins ) - 1 )

    hypo.ETthr          = threshold*GeV
    hypo.dETACLUSTERthr = 0.1
    hypo.dPHICLUSTERthr = 0.1
    #hypo.ET2thr         = same( 90.0*GeV )

    if sel == 'nocut':
        #hypo.AcceptAll = True
        hypo.ETthr          = threshold*GeV
        hypo.dETACLUSTERthr = 9999.
        hypo.dPHICLUSTERthr = 9999.

    if sel == 'etcut' or sel == 'nopid' or sel == 'ion':
        hypo.ETthr          = threshold*GeV
        hypo.dETACLUSTERthr = 9999.
        hypo.dPHICLUSTERthr = 9999.

    return hypo

 




#
# Hypo tool
#
class TrigEgammaFastElectronHypoTool( Messenger):


  #
  # Constructor
  #
  def __init__(self, name, **kw):

    Messenger.__init__(self, name)
    self.name = name

    declareProperty( self, kw, "EtCut"                ,   0      )
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

    for cl in clCont

      passed = False
      deta = abs(etaRef - cl.eta())
      dphi = abs(phiRef - cl.phi())
      dphi = if  math.fabs(dphi) > np.pi: dphi -= 2*np.pi

      if deta < self.dETACLUSTERthr:
        if dphi < self.dPHICLUSTERthr:        
          if cl.et() > self.EtCut*GeV:
            passed=True

      bitAccept[el.getPos()] = passed
    # Loop over cluster

    clCont.setPos( current )
    # got this far => passed!
    passed = any( bitAccept )
    return Accept( self.name, [("Pass", passed)] )




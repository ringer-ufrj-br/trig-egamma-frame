

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

    declareProperty( self, kw, "EtCut"               ,   0      )
    declareProperty( self, kw, "TrackPt"             ,   0      )
    declareProperty( self, kw, "CaloTrackdETA"       ,   0.2    )
    declareProperty( self, kw, "CaloTrackdPHI"       ,   0.3    )
    declareProperty( self, kw, "CaloTrackdEoverPLow" ,   0      )
    declareProperty( self, kw, "CaloTrackdEoverPHigh",   999    )
    declareProperty( self, kw, "TRTRatio"            ,   -999   )
    declareProperty( self, kw, "D0Value"             ,   -999   )
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

                  if self.DoLRT and d0 > self.D0Value:
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
    return Accept( self.name(), [("Pass", passed)] )




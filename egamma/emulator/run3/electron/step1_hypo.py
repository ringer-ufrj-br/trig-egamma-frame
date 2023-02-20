

__all__ = ['L2Calo']


from egamma.core import Messenger
from egamma.core.macros  import *
from egamma.core import declareProperty, ToolSvc, StatusCode
from egamma import GeV
from ROOT import TEnv
from tensorflow import keras

import numpy as np
import math

def same(value):
    return [value]*9

    
#
# L2Calo hypo tool
#
class L2Calo(Messenger):

  #
  # Constructor
  #
  def __init__(self, name, **kw):

    Messenger.__init__(self)

    declareProperty( self, kw, "EtaBins"        , [0.0, 0.6, 0.8, 1.15, 1.37, 1.52, 1.81, 2.01, 2.37, 2.47] )
    declareProperty( self, kw, "F1thr"          , same(0.005)                         )
    declareProperty( self, kw, "ETthr"          , same(0)                             )
    declareProperty( self, kw, "ET2thr"         , same(90.0*GeV)                      )
    declareProperty( self, kw, "HADET2thr"      , same(999.0)                         )
    declareProperty( self, kw, "HADETthr"       , same(999.0)                         )
    declareProperty( self, kw, "CARCOREthr"     , same(999.0)                         )
    declareProperty( self, kw, "CAERATIOthr"    , same(999.0)                         )
    declareProperty( self, kw, "dETACLUSTERthr" , 0.1                                 )
    declareProperty( self, kw, "dPHICLUSTERthr" , 0.1                                 )
    declareProperty( self, kw, "WETA2thr"       , same(99999.)                        )
    declareProperty( self, kw, "WSTOTthr"       , same(99999.)                        )
    declareProperty( self, kw, "F3thr"          , same(99999.)                        )
    declareProperty( self, kw, "DoRinger"       , True                                )
    declareProperty( self, kw, "ConfigPath"     , None                                )


  #
  # Initialize method
  #
  def initialize(self): 

    if self.DoRinger:
      MSG_INFO(self, f"Loading ringer models from {self.ConfigPath}")
      self.load(self.ConfigPath)

    return StatusCode.SUCCESS


  #
  # Accept method
  #
  def accept(self, context):

    if self.DoRinger:
      passed = self.emulate_ringer(context)
    else:
      passed = self.emulate(context)

    return Accept( self.name(), [ ("Pass", passed)] )



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
    if ( eT_T2Calo*1e-3 < self.ETthr[etaBin]): return False
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
  def emulate_ringer(self, context)


    fc = context.getHandler("HLT__TrigEMClusterContainer")
    eventInfo = context.getHandler( "EventInfoContainer" )

    avgmu = eventInfo.avgmu()
    absEta = abs(fc.eta())

    if eta>2.5: eta=2.5
    et = fc.et() # in GeV

    if et < self.EtCut*GeV:
      return False


    discriminant = None

    for model in self.models:
      if model.etmin() < et/GeV <= model.etmax():
        if model.etamin() < absEta <= model.etamax():
          discriminant = model.predict(context)

    if not discriminant:
      return False



    cutter=None
    for obj in self.cuts:
      if obj.etmin() < et/GeV <= obj.etmax():
        if obj.etamin() < absEta <= obj.etamax():
          cutter=obj

    if not cutter:
      return False

    return cut.accept(discriminant, avgmu)


  #
  # Load all ringer models from athena format
  #
  def load( configPath ):
    
    basepath = '/'.join(configPath.split('/')[:-1])

    # Load configuration file
    env = TEnv( configPath )
    version = env.GetValue("__version__", '')

    def treat_float( env, key ):
      return [float(value) for value in  env.GetValue(key, '').split('; ')]

    def treat_string( env, key ):
      return [str(value) for value in  env.GetValue(key, '').split('; ')]

    #
    # Reading all models
    #
    nmodels     = env.GetValue("Model__size", 0)
    etmin_list  = treat_float( env, 'Model__etmin' )
    etmax_list  = treat_float( env, 'Model__etmax' )
    etamin_list = treat_float( env, 'Model__etamin' )
    etamax_list = treat_float( env, 'Model__etamax' )
    paths       = treat_string(env, 'Model__path' )
    
    class Model:
      def __init__(self, model, etmin, etamax, etmin, etmax):
        self.model=model
        self.etmin=etmin; self.etmax=etmax
        self.etamin=etamin; self.etamax=etamax

    self.models = []
    for idx, path in enumerate(paths):
      model = keras.models.load_model(basepath+'/'+path.replace('.onnx','h5'))
      self.models.append(Model( model,
                                etmin_list[idx],
                                etmax_list[idx],
                                etamin_list[idx],
                                etamax_list[idx],
                                ))

    #
    # Reading all thresholds
    #  
   
    nhresholds  = env.GetValue("Threshold__size", 0)
    max_avgmu   = treat_float( env, "Threshold__MaxAverageMu" )
    min_avgmu   = treat_float( env, "Threshold__MinAverageMu" )
    etmin_list  = treat_float( env, 'Threshold__etmin' )
    etmax_list  = treat_float( env, 'Threshold__etmax' )
    etamin_list = treat_float( env, 'Threshold__etamin' )
    etamax_list = treat_float( env, 'Threshold__etamax' )
    slopes      = treat_float( env, 'Threshold__slope' )
    offsets     = treat_float( env, 'Threshold__offset' )

    class Threshold:
      def __init__(self, slope, offset, avgmumin, avgmumax, etmin, etmax, etamin, etamax):
        self.slope=slope; self.offset=offset
        self.etmin=etmin; self.etmax=etmax
        self.etamin=etamin; self.etamax=etamax
        self.avgmumin=avgmumin; self.avgmumax=avgmumax

      # Is passed?
      def accept(self, discr, avgmu):
        if avgmu < self.avgmumin:
          avgmu=0
        if avgmu > self.avgmumax:
          avgmu=self.avgmumax
        return True if discr > avgmu*self.slope + self.offset else False 


    for idx in range(nhresholds):
      self.cuts.append( Threshold( 
                                    slopes[idx],
                                    offsets[idx],
                                    min_avgmu[idx],
                                    max_avgmu[idx],
                                    etmin_list[idx],
                                    etmax_list[idx],
                                    etamin_list[idx],
                                    etamax_list[idx],
                                  ))



  #
  # Finalize method
  #
  def finalize(self):
    return StatusCode.SUCCESS





def configure_from_trigger( trigger ):

  d = treat_trigger_dict_type( trigger )
  etthr = d['etthr']
  pidname = d['pidname']
  name = 'Hypo__FastCalo__' + trigger

  emulator = ToolSvc.retrieve("Emulator")
  if not emulator.isValid(name):
    hypo = configure(name, etthr, pidname)
    emulator+=hypo

  return name



#
# Configure the hypo from trigger name
#
def configure( name, etthr, pidname ):

  
  from trig_egamma_frame.emulator.run2 import L2CaloCutMaps, TrigEgammaFastCaloHypoTool
  cuts = L2CaloCutMaps(etthr)
  hypo  = L2Calo(name,
                 dETACLUSTERthr = 0.1,
                 dPHICLUSTERthr = 0.1,
                 EtaBins        = [0.0, 0.6, 0.8, 1.15, 1.37, 1.52, 1.81, 2.01, 2.37, 2.47],
                 F1thr          = same(0.005),
                 ETthr          = same(0),
                 ET2thr         = same(90.0*GeV),
                 HADET2thr      = same(999.0),
                 WETA2thr       = same(99999.),
                 WSTOTthr       = same(99999.),
                 F3thr          = same(99999.),
                 HADETthr       = cuts.MapsHADETthr[pidname],
                 CARCOREthr     = cuts.MapsCARCOREthr[pidname],
                 CAERATIOthr    = cuts.MapsCAERATIOthr[pidname],
                 DoRinger       = True,
                 EtCut          = etcut, 
                 )

  return hypo


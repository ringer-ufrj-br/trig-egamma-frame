
__all__ = ["RingerSelector"]

from egamma.core import Messenger
from egamma.core.macros  import *
from egamma.core import declareProperty, StatusCode
from egamma import GeV
from ROOT import TEnv
from egamma.emulator.run3.ringer import Model, Threshold, half_rings_indexs
from tensorflow import keras
import numpy as np


def treat_float( env, key ):
  return [float(value) for value in  env.GetValue(key, '').split('; ')]

def treat_string( env, key ):
  return [str(value) for value in  env.GetValue(key, '').split('; ')]



class RingerSelector(Messenger):


  def __init__(self, **kw):
    
    Messenger.__init__(self)
    declareProperty( self, kw, "ConfigPath"     , "" )

  

  #
  # Load all ringer models from athena format
  #
  def initialize(self):
    
    MSG_INFO(self, f"Loading models from {self.ConfigPath}")

    basepath = '/'.join(self.ConfigPath.split('/')[:-1])

    # Load configuration file
    env = TEnv( self.ConfigPath )
    version = env.GetValue("__version__", '')
    self.cuts = []
    self.models = []
    
    # Reading all models
    nmodels     = env.GetValue("Model__size", 0)
    barcode_list= treat_float( env, 'Model__barcode' )
    etmin_list  = treat_float( env, 'Model__etmin' )
    etmax_list  = treat_float( env, 'Model__etmax' )
    etamin_list = treat_float( env, 'Model__etamin' )
    etamax_list = treat_float( env, 'Model__etamax' )
    paths       = treat_string(env, 'Model__path' )

    self.models = []
    for idx, path in enumerate(paths):
      model = keras.models.load_model(basepath+'/'+path.replace('.onnx','.h5'))
      self.models.append(Model( model,
                                etmin_list[idx],
                                etmax_list[idx],
                                etamin_list[idx],
                                etamax_list[idx],
                                barcode_list[idx],
                                ))

    # Reading all thresholds
    nhresholds  = env.GetValue("Threshold__size", 0)
    max_avgmu   = treat_float( env, "Threshold__MaxAverageMu" )
    min_avgmu   = treat_float( env, "Threshold__MinAverageMu" )
    etmin_list  = treat_float( env, 'Threshold__etmin' )
    etmax_list  = treat_float( env, 'Threshold__etmax' )
    etamin_list = treat_float( env, 'Threshold__etamin' )
    etamax_list = treat_float( env, 'Threshold__etamax' )
    slopes      = treat_float( env, 'Threshold__slope' )
    offsets     = treat_float( env, 'Threshold__offset' )

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

    return StatusCode.SUCCESS


  def predict(self, context):

    cl = context.getHandler("HLT__TrigEMClusterContainer")

    for model in self.models:
      if model.etmin < cl.et()/GeV <= model.etmax:
        if model.etamin < abs(cl.eta()) <= model.etamax:
          # prepare inputs given barcode configuration
          inputs = self.prepare_inputs(context, model.barcode)
          return model.predict(inputs)
        # is in eta range?
      # is in et range?
    # Loop over all modes
    return None # dummy output
    

  def accept(self, context, discriminant):

    cl = context.getHandler("HLT__TrigEMClusterContainer")
    evtInfo = context.getHandler( "EventInfoContainer")
    avgmu = evtInfo.avgmu()
    for cut in self.cuts:
      if cut.etmin < cl.et()/GeV <= cut.etmax:
        if cut.etamin < abs(cl.eta()) <= cut.etamax:
          # prepare inputs given barcode configuration
          return cut.accept(discriminant, avgmu)
        # is in eta range?
      # is in et range?
    # Loop over all cuts
    return False


  def prepare_inputs(self, context, barcode):

    cl = context.getHandler("HLT__TrigEMClusterContainer")
    inputs = []
    if barcode == 0:
      rings = cl.ringsE() / abs(sum(cl.ringsE()))
      inputs.append(rings)
    elif barcode == 1:
      rings = cl.ringsE() 
      ref_rings = [rings[iring] for iring in half_rings_indexs]
      ref_rings = ref_rings / abs(sum(ref_rings))
      inputs.append(ref_rings)

    return np.array(inputs)



  def emulate(self, context):

    discriminant = self.predict(context)
    if not discriminant:
      return False

    return self.accept(context, discriminant)
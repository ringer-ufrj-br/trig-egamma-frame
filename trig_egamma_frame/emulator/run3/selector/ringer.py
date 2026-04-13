
__all__ = ["RingerSelector"]

from trig_egamma_frame.kernel import StatusCode
from trig_egamma_frame import GeV
from ROOT import TEnv, kEnvUser
from tensorflow import keras
from trig_egamma_frame import logger
import tensorflow as tf
import numpy as np


tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

def treat_float( env, key ):
  return [float(value) for value in  env.GetValue(key, '').split('; ')]

def treat_string( env, key ):
  return [str(value) for value in  env.GetValue(key, '').split('; ')]


NUMBER_OF_RINGS = 100


class Model:
  def __init__(self, model, etmin, etmax, etamin, etamax, barcode,path):
    self.model=model
    self.etmin=etmin; self.etmax=etmax
    self.etamin=etamin; self.etamax=etamax
    self.barcode=barcode
    self.path = path

  #
  # Predict discriminant output
  #
  def predict(self, inputs):
    return self.model(inputs)[0][0]


class Threshold:
  def __init__(self, slope, offset, avgmumin, avgmumax, etmin, etmax, etamin, etamax):
    self.slope=slope; self.offset=offset
    self.etmin=etmin; self.etmax=etmax
    self.etamin=etamin; self.etamax=etamax
    self.avgmumin=avgmumin; self.avgmumax=avgmumax

  #
  # Is passed?
  #
  def accept(self, discr, avgmu):
    #if avgmu < self.avgmumin:
    #  avgmu=0
    if avgmu > self.avgmumax:
      avgmu=self.avgmumax
    return True if discr > avgmu*self.slope + self.offset else False 


# for new training, we selected 1/2 of rings in each layer
half_rings_indexs = [0, 1, 2, 3, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 72, 73, 74, 75, 80, 81, 82, 83, 88, 89, 92, 93, 96, 97]



class RingerSelector:


  def __init__(self, ConfigPath: str):
    
    self.ConfigPath = ConfigPath

  

  #
  # Load all ringer models from athena format
  #
  def initialize(self) -> StatusCode:
    
    #MSG_INFO(self, f"Loading models from {self.ConfigPath}")

    basepath = '/'.join(self.ConfigPath.split('/')[:-1])

    # Load configuration file
    env = TEnv( '' )
    env.ReadFile( self.ConfigPath, kEnvUser )
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
                                basepath+'/'+path.replace('.onnx','.h5'),
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

    if max_avgmu < min_avgmu:
      logger.debug( 'Fixing avgmu boundaries... ')
      #print('Fixing avgmu boundaries... ')
      a = max_avgmu; b = min_avgmu
      max_avgmu = b; min_avgmu = a
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
      rings = cl.ringsE()
      energy = sum(rings)
      if energy > 0:
        rings = rings / energy
      inputs.append(rings)
    elif barcode == 1:
      rings = cl.ringsE() 
      ref_rings = [rings[iring] for iring in half_rings_indexs]
      energy = sum(ref_rings)
      if energy > 0:
        ref_rings = ref_rings / energy
      inputs.append(ref_rings)

    return np.array(inputs)



  def emulate(self, context):

    discriminant = self.predict(context)
    if not discriminant:
      return False

    return self.accept(context, discriminant)


  def get_model(self, et, eta):
    for model in self.models:
        if model.etmin*GeV < et <= model.etmax*GeV:
            if model.etamin < abs(eta) <= model.etamax:
                return model
    return None

  def get_cut(self, et, eta):
    for config in self.cuts:
        if config.etmin*GeV < et <= config.etmax*GeV:
            if config.etamin < abs(eta) <= config.etamax:
                return config
    return None
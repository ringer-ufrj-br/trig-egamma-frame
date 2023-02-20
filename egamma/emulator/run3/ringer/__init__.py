

__all__ = ["Model", "Threshold"]


class Model:
  def __init__(self, model, etmin, etmax, etamin, etamax, input_generator):
    self.model=model
    self.etmin=etmin; self.etmax=etmax
    self.etamin=etamin; self.etamax=etamax
    self.input_generator = input_generator

  #
  # Predict discriminant output
  #
  def predict(self, context):
    return self.model.predict(inputs)[0][0].numpy()


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
    if avgmu < self.avgmumin:
      avgmu=0
    if avgmu > self.avgmumax:
      avgmu=self.avgmumax
    return True if discr > avgmu*self.slope + self.offset else False 


from . import RingerSelector
__all__.extend(RingerSelector.__all__)
from .RingerSelector import *
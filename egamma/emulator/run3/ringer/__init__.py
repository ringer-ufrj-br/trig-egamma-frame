

__all__ = ["Model", "Threshold", "half_rings_indexs"]


class Model:
  def __init__(self, model, etmin, etmax, etamin, etamax, barcode):
    self.model=model
    self.etmin=etmin; self.etmax=etmax
    self.etamin=etamin; self.etamax=etamax
    self.barcode=barcode

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
    if avgmu < self.avgmumin:
      avgmu=0
    if avgmu > self.avgmumax:
      avgmu=self.avgmumax
    return True if discr > avgmu*self.slope + self.offset else False 


# for new training, we selected 1/2 of rings in each layer
half_rings_indexs = [0, 1, 2, 3, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 72, 73, 74, 75, 80, 81, 82, 83, 88, 89, 92, 93, 96, 97]


from . import RingerSelector
__all__.extend(RingerSelector.__all__)
from .RingerSelector import *
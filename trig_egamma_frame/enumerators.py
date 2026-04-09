__all__ = ['DataframeSchemma', 'DataframeType']

from enum import Enum


class DataframeSchemma(Enum):
  Run2 = 0
  Run3 = 1


class DataframeType(Enum):
  Electron = 0
  Photon = 1

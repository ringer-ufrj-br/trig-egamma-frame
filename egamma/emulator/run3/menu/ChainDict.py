
__all__ = ["get_chain_dict", "treat_pidname"]

from egamma.core import Messenger
from egamma.core.macros  import *
from pprint import pprint
from copy import copy



# Take from: https://gitlab.cern.ch/atlas/athena/-/blob/master/Trigger/TriggerCommon/TriggerMenuMT/python/HLT/Menu/SignatureDicts.py
#==========================================================
# Electron Chains
#==========================================================
AllowedTopos_e = ['Jpsiee','Zeg','Zee','Heg','bBeeM6000']
# ---- Electron Dictionary of all allowed Values ----
ElectronChainParts = {
    'signature'      : ['Electron'],
    'alignmentGroup' : ['Electron','Egamma'],
    'chainPartName'  : '',
    'L1threshold'    : '',
    'tnpInfo'        : ['probe'],
    'extra'          : ['ion'],
    'multiplicity'   : '',
    'trigType'       : ['e'],
    'threshold'      : '',
    'etaRange'       : [],
    'IDinfo'         : ['dnnloose','dnnmedium','dnntight','lhvloose','lhloose','lhmedium','lhtight','vloose','loose','medium','tight', 'mergedtight'],
    'isoInfo'        : ['ivarloose','ivarmedium','ivartight'],
    'idperfInfo'     : ['idperf'],
    'gsfInfo'        : ['nogsf'],
    'lrtInfo'        : ['lrtloose','lrtmedium','lrttight'],
    'caloInfo'       : [],
    'lhInfo'         : ['nod0', 'nopix'],
    'L2IDAlg'        : ['noringer'],
    'rVersion'       : ['run2-v8', 'run3-v0', 'run3-v1'],
    'addInfo'        : [ 'etcut', 'etcut1step',"fwd",'nopid'],
    'sigFolder'     : ['Egamma'],
    'subSigs'       : ['Electron'],
    'topo'          : AllowedTopos_e,
    #'chainPartIndex': list(range(0,10))
}

# ---- Egamma Dictionary of default Values ----
ElectronChainParts_Default = {
    'signature'      : ['Electron'],
    'alignmentGroup' : ['Electron'],
    'multiplicity'   : '',
    'L1threshold'         : '',
    'trigType'       : '',
    'threshold'      : '',
    'etaRange'       : '0eta250',
    'tnpInfo'        : '',
    'extra'          : '',
    'IDinfoType'     : '',
    'IDinfo'         : '',
    'isoInfo'        : '',
    'reccalibInfo'   : '',
    'idperfInfo'     : '',
    'gsfInfo'        : '',
    'lrtInfo'        : '',
    'caloInfo'       : '',
    'lhInfo'         : '',
    'L2IDAlg'        : '',
    'hypoInfo'       : '',
    'recoAlg'        : '',
    'FSinfo'         : '',
    'addInfo'        : [],
    'sigFolder'     : ['Egamma'],
    'subSigs'       : ['Electron'],
    'topo'          : [],
    #'chainPartIndex': 0
}

# Take from: https://gitlab.cern.ch/atlas/athena/-/blob/master/Trigger/TriggerCommon/TriggerMenuMT/python/HLT/Menu/SignatureDicts.py
#==========================================================
# Photon chains
#==========================================================
# ---- Photon Dictionary of all allowed Values ----
AllowedTopos_g = ['dPhi25', 'm80']
PhotonChainParts = {
    'L1threshold'    : '',
    'signature'      : ['Photon'],
    'alignmentGroup' : ['Photon','Egamma'],
    'chainPartName'  : '',
    'multiplicity'   : '',
    'trigType'       : ['g'],
    'threshold'      : '',
    'extra'          : ['hiptrt', 'ion'],
    'IDinfo'         : ['etcut','loose','medium','tight'],
    'isoInfo'        : ['noiso', 'icaloloose','icalomedium','icalotight'],
    'reccalibInfo'   : [],
    'trkInfo'        : [],
    'caloInfo'       : [],
    'L2IDAlg'        : ['ringer'],
    'hypoInfo'       : '',
    'recoAlg'        : [],
    'FSinfo'         : [],
    'addInfo'        : ['etcut',],
    'sigFolder'     : ['Egamma'],
    'subSigs'       : ['Photon'],
    'topo'          : AllowedTopos_g,
    #'chainPartIndex': list(range(0,10)),
    }


def treat_pidname(pidname):
  if 'tight' in pidname:
    return 'tight'
  elif 'medium' in pidname:
    return 'medium'
  # this should be before loose to works
  elif 'vloose' in pidname:
    return 'vloose'
  else:
    return 'loose'


class ChainDict(Messenger):

    def __init__(self, trigName):
        Messenger.__init__(self)
        self.trigName = trigName
        self.args = {}



    #
    # Get chain dict
    #
    def configure(self):

        d = copy(ElectronChainParts_Default)

        # Format: HLT_e(G)XX_*_L1EM*
        trigger = self.trigName
        trigger = trigger.replace('HLT_', '')

        trigParts = trigger.split('_')
        trigType  = trigParts[0][0]

        d['trigName']    = self.trigName
        d['threshold']   = float(trigParts[0][1::])
        d['L1Threshold'] = trigParts[-1]

        def check(trig, d, key, chainParts):
            for part in chainParts[key]:
                if '_'+part+'_' in trig:
                    d[key] = part
                    return

        if trigType == 'e':

            d['signature'] = 'Electron'
            d['trigType']  = 'e'
            for key in ElectronChainParts.keys():
                check(trigger, d, key, ElectronChainParts)
            
        elif trigType == 'g':
            d['signature'] = 'Photon'
            d['trigType']  = 'g'
            for key in PhotonChainParts.keys():
                check(trigger, d, key, PhotonChainParts)

        else:
            MSG_FATAL(self, "Signature not supported.")


        self.args = d


def get_chain_dict( trigger ):

    chain = ChainDict(trigger)
    chain.configure()
    return chain.args




    
if __name__ == "__main__":


    trigger_list = [
                    #'HLT_e26_lhtight_ivarloose_L1EM22VHI',
                    #'HLT_e28_lhtight_ivarloose_noringer_nogsg_lrtmedium_L1EM22VHI',
                    #'HLT_e60_lhmedium_run2-v8_L1EM26M',
                    'HLT_e26_lhtight_ivarloose_run3-v0_L1EM22VHI',
                    'HLT_e26_lhtight_ivarloose_run3-v1_L1EM22VHI',
                    'HLT_e26_lhtight_ivarloose_noringer_L1EM22VHI'
                    ]

    for trigger in trigger_list:

        chain = ChainDict(trigger)
        chain.configure()   
        pprint(chain.args)
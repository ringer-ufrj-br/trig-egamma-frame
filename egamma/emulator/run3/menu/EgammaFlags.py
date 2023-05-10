
__all__ = ["electronFlags"]

import os

class ElectronFlags:
    def __init__(self):
        '''
        This flags is used to configure the Ringer Version to be used. 
        Attention to the paths used as default here. Any new versions must be correctly defined.
        When define a chain remenber to put the key version on it like: 'HLT_e26_lhtight_ivarloose_run2-v8_L1EM22VHI'
        '''
        
        self.ringerVersion = {
            'run2_v8' : "/cern_data/tunings/releases/Run2_20230227_v8/",
            'run3_v0' : "/cern_data/tunings/releases/Run3_20230316_v0/",
            'run3_v1' : "/cern_data/tunings/releases/Run3_20230316_v1/"
            }
        

electronFlags = ElectronFlags()
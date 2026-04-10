
__all__ = ["electronFlags"]

import os
from trig_egamma_frame.emulator.run3.menu import ringer_versions

class ElectronFlags:
    def __init__(self):
        '''
        This flags is used to configure the Ringer Version to be used. 
        Attention to the paths used as default here. Any new versions must be correctly defined.
        When define a chain remenber to put the key version on it like: 'HLT_e26_lhtight_ivarloose_run2-v8_L1EM22VHI'
        '''
        basepath = os.environ['CERN_DATA']
        self.ringerVersion = {
            'run2_v8' : os.path.join(basepath, "joao.pinto/tunings/releases/Run2_20230227_v8/"),
            'run3_v0' : os.path.join(basepath, "joao.pinto/tunings/releases/Run3_20230316_v0/"),
            'run3_v1' : os.path.join(basepath, "joao.pinto/tunings/releases/Run3_20230316_v1/")
            }
        self.L1Legacy = True
    
    def register_ringer_version(self, version: str, path: str):
        """
        registers a new ringer version with its path

        Parameters
        ----------
        version : str
            Ringer version
        path : str
            Directory path to the version files
        """
        ringer_versions.append(version)
        self.ringerVersion[version] = path
    

electronFlags = ElectronFlags()

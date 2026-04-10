"""
Implements the ElectronDumper class and its utilities to dump Electron data
"""

__all__ = ["ElectronDumper_v2"]

import os 
import ROOT 

import numpy as np

from itertools import product
from numbers import Number
from collections import OrderedDict
from typing import List, Dict, Tuple, Callable, Any, Sequence

from loguru import logger

from trig_egamma_frame.kernel import Algorithm, StatusCode, EventContext, EDM
from trig_egamma_frame import GeV


from trig_egamma_frame.emulator import attach
from trig_egamma_frame.emulator import electronFlags
from trig_egamma_frame.emulator.run3 import ElectronChain as Chain
from trig_egamma_frame.emulator.run3 import RingerSelector
from trig_egamma_frame.emulator.run3.electron import ELECTRON_STEPS
from trig_egamma_frame.emulator.run3.selector.ringer import NUMBER_OF_RINGS
from trig_egamma_frame.emulator.run3.menu.ChainDict import get_chain_dict

class ElectronDumper_v2( Algorithm ):
    """
    Dumps Electron data into a root file into a tree named tree.
    Can dump chain decisions and custom branches by using decorators.
    """

    def __init__(self, output: str,
                 etbins: Sequence[Number],
                 etabins: Sequence[Number],
                 only_decorators: bool=False,
                 decorate_rings: bool=False,
                 decorate_ringerVersion: bool=False,
                 **kw):
        """
        Constructor

        Parameters
        ----------
        output : str
            Output directory path
        etbins : Sequence[Number]
            Sequence with the etbins edges
        etabins : Sequence[Number]
            Sequence with the etabins edges
        only_decorators : bool, optional
            If True computes only the decorators, by default False
        """
        
        Algorithm.__init__(self, "ElectronDumper")
        
        self.__models = None
        self.__buffer = {}
        self.__etbins  = etbins
        self.__etabins = etabins
        self.output    = output
        self.features  = []
        self.__decorators = OrderedDict()
        self.__only_decorators = only_decorators
        self.__decorate_rings = decorate_rings
        self.chains = OrderedDict()
        self.__decorate_ringerVersions = decorate_ringerVersion
        

    def decorate(self, key: str , f: Callable[[EventContext], Number]) -> None:
        """
        Decorates the root file with another variable

        Parameters
        ----------
        key : str
            Variable name for the given decorator
        f : Callable[[EventContext], Number]
            Callable that receives an event context and returns
            a value for the variable
        """
        self.__decorators[key] = f

    def decorate_chain(self, chain_name: str) -> None:
        """
        Decorates the dumper with a chain simulation.
        As an example:
        Given the following chain: e140_lhloose_L1EM22VHI, adds the
        following branches:
        - L1Calo_e140_lhloose_L1EM22VHI
        - FastCalo_e140_lhloose_L1EM22VHI
        - FastElectron_e140_lhloose_L1EM22VHI
        - PrecisionCalo_e140_lhloose_L1EM22VHI
        - PrecisionElectron_e140_lhloose_L1EM22VHI

        Parameters
        ----------
        chain_name : str
            The chain to decorate
        """
        self.chains[chain_name] = get_chain_dict(chain_name)
        attach(Chain(chain_name))
    
    def get_decorators(self) -> Dict[str, Callable[[EventContext], Number]]:
        """
        Returns an OrderedDict instance with the key, f pairs passed to
        decorate.

        Returns
        -------
        Dict[str, Callable[[EventContext], Number]]
        """
        return self.__decorators
    
    def __make_models_dict(self) -> Dict[str, RingerSelector]:
        """
        Builds the models_dict inside each of self.buffer entries

        Returns
        -------
        Dict[str, RingerSelector]
        """
        ringer_models_dict = {}
        name_dict = {'Tight'     : 'tight',
                     'Medium'    : 'medium',
                     'Loose'     : 'loose',
                     'VeryLoose' : 'vloose'}
        
        for iversion, ipath in electronFlags.ringerVersion.items():
            for jop, jname in name_dict.items():
                m = RingerSelector(ConfigPath=ipath+f'ElectronRinger{jop}TriggerConfig.conf')
                m.initialize()
                ringer_models_dict.update({f'{iversion}_{jname}'  : m})
        return ringer_models_dict
    
    def __make_buffer_dict(self) -> Dict[str, list]:
        """
        Builds the buffer_dict inside each of self.buffer entries

        Returns
        -------
        Dict[str, list]
        """
        buffer_dict = {
            'et_bin': [],
            'eta_bin': [],
            'avgmu': []
        }
        buffer_dict.update({decorator_name: [] for decorator_name in self.__decorators.keys()})
        buffer_dict.update({
            'el_lhtight': [],
            'el_lhmedium': [],
            'el_lhloose': [],
            'el_lhvloose': []
        })
        if self.__decorate_ringerVersions:
            for iversion in electronFlags.ringerVersion.keys():
                buffer_dict.update({f'{iversion}_output' : [],
                                    f'{iversion}_tight'  : [],
                                    f'{iversion}_medium' : [],
                                    f'{iversion}_loose'  : [],
                                    f'{iversion}_vloose' : []})
        if self.__only_decorators:
            if self.__decorate_rings:
                buffer_dict.update({f'trig_L2_cl_ring_{iring}': [] for iring in range(NUMBER_OF_RINGS)})
            return buffer_dict

        buffer_dict.update({
            'trig_L2_cl_et': [],
            'trig_L2_cl_eta': [],
            'trig_L2_cl_phi': [],
            'trig_L2_cl_reta': [],
            'trig_L2_cl_ehad1': [],
            'trig_L2_cl_eratio': [],
            'trig_L2_cl_f1': [],
            'trig_L2_cl_f3': [],
            'trig_L2_cl_weta2': [],
            'trig_L2_cl_wstot': [],
            'trig_L2_cl_e2tsts1': [],    
        })
        buffer_dict.update({f'trig_L2_cl_ring_{iring}': [] for iring in range(NUMBER_OF_RINGS)})
        buffer_dict.update({
            'trig_L2_el_hastrack': [],
            'trig_L2_el_trkClusDeta': [],
            'trig_L2_el_trkClusDphi': [],
            'trig_L2_el_etOverPt': [],
            'trig_L2_el_d0': [],
        })
        buffer_dict.update({
            f"{step_name}_{chain_name}": []
            for chain_name, step_name in product(self.chains.keys(), ELECTRON_STEPS)
        })

        return buffer_dict

    def initialize(self) -> StatusCode:

        super().initialize()

        store = self.getStoreGateSvc()
        store.mkdir('sample')
        store.addHistogram(ROOT.TH1F('et','E_{T} distribution;E_{T};Count', 100, 0, 150 ))
        store.addHistogram(ROOT.TH1F('eta','#eta distribution;#eta;Count', 50, -2.5, 2.5))
        
        self.__buffer = self.__make_buffer_dict()#np.empty((len(etbins)-1, len(etabins)-1), dtype=object)
        #n, m = self.__buffer.shape
        #for etBinIdx, etaBinIdx in product(range(n), range(m)):
        #    self.__buffer[etBinIdx, etaBinIdx] = self.__make_buffer_dict()
        if self.__decorate_ringerVersions:
            logger.debug("Decorate Ringer Versions is True. Starting to load the models...")
            self.__models = self.__make_models_dict()

        return StatusCode.SUCCESS

    def __add_offline_decision(self, buffer_dict: Dict[str, List[Number]],
                             context: EventContext) -> None:
        """
        Appends the event's offline decision to buffer_dict.
        Executed when only_decorators=True

        Parameters
        ----------
        buffer_dict : Dict[str, List[Number]]
            buffer_dict to append
        context : EventContext
            Current EventContext instance
        """
        
        elCont: EDM = context.getHandler("ElectronContainer")
        buffer_dict["el_lhtight"].append(np.int32(elCont.accept("el_lhtight")))
        buffer_dict["el_lhmedium"].append(np.int32(elCont.accept("el_lhmedium")))
        buffer_dict["el_lhloose"].append(np.int32(elCont.accept("el_lhloose")))
        buffer_dict["el_lhvloose"].append(np.int32(elCont.accept("el_lhvloose")))
    
    def __add_ringer_decision(self, buffer_dict: Dict[str, List[Number]], 
                               models_dict: Dict[str, RingerSelector],
                               context: EventContext) -> None:
        """
        Appends the event's ringer decision to buffer_dict.
        Executed when decorate_ringerVersion=True

        Parameters
        ----------
        buffer_dict : Dict[str, List[Number]]
            buffer_dict to append
        models_dict : Dict[str, RingerSelector]
            models_dict to be used for predict and get accept
        context : EventContext
            Current EventContext instance
        """
        for iversion in electronFlags.ringerVersion.keys():
            buffer_dict[f'{iversion}_output'].append(models_dict[f'{iversion}_tight'].predict(context).numpy())
            for iop in ['tight', 'medium', 'loose', 'vloose']:
                buffer_dict[f'{iversion}_{iop}'].append(np.int32(models_dict[f'{iversion}_{iop}'].emulate(context)))
            
        
    def __apply_decorators(self, buffer_dict: Dict[str, List[Number]],
                         context: EventContext) -> None:
        """
        Computes and appends the decorators results to buffer_dict.
        Executed when only_decorators=True

        Parameters
        ----------
        buffer_dict : Dict[str, List[Number]]
            buffer_dict to append
        context : EventContext
            Current EventContext instance
        """
        for feature, func, in self.__decorators.items():
            buffer_dict[feature].append(func(context))

    def __apply_chain_decorators(self, buffer_dict: Dict[str, List[Number]],
                               context: EventContext) -> None:
        """
        Computes and appends all the chains decisions to buffer_dict.
        Executed when only_decorators=True

        Parameters
        ----------
        buffer_dict : Dict[str, List[Number]]
            buffer_dict to append
        context : EventContext
            Current EventContext instance
        """
        
        for chain_name in self.chains.keys():
            trig_menu: EDM = context.getHandler("MenuContainer")
            chain_results = trig_menu.accept(chain_name)
            for step_name in ELECTRON_STEPS:
                step_chain_name = f"{step_name}_{chain_name}"
                # Casting to int32 to be RDataFrame.MakeNumpyDataFrame compatible
                # default bool neither numpy.bool_ work
                buffer_dict[step_chain_name].append(np.int32(chain_results.getCutResult(step_name)))
    

    def __add_fc_rings(self, buffer_dict: Dict[str, List[Number]],
                       context: EventContext) -> None:
        """
        Appends the rings information from FastCalo

        Parameters
        ----------
        buffer_dict : Dict[str, List[Number]]
            buffer_dict to append
        context : EventContext
            Current EventContext instance
        """           
        fast_calo: EDM = context.getHandler( "HLT__TrigEMClusterContainer" )
        ring_array = fast_calo.ringsE()
        for iring in range(NUMBER_OF_RINGS):
            buffer_dict[f'trig_L2_cl_ring_{iring}'].append(ring_array[iring])

    def __add_fast_calo_info(self, buffer_dict: Dict[str, List[Number]],
                           context: EventContext) -> None:
        """
        Appends fast calo infos to buffer_dict.
        Executed when only_decorators=False

        Parameters
        ----------
        buffer_dict : Dict[str, List[Number]]
            buffer_dict to append
        context : EventContext
            Current EventContext instance
        """
        
        fast_calo: EDM = context.getHandler( "HLT__TrigEMClusterContainer" )
        buffer_dict['trig_L2_cl_et'].append(fast_calo.et())
        buffer_dict['trig_L2_cl_eta'].append(fast_calo.eta())
        buffer_dict['trig_L2_cl_phi'].append(fast_calo.phi())
        buffer_dict['trig_L2_cl_reta'].append(fast_calo.reta())
        buffer_dict['trig_L2_cl_ehad1'].append(fast_calo.ehad1())
        buffer_dict['trig_L2_cl_eratio'].append(fast_calo.eratio())
        buffer_dict['trig_L2_cl_f1'].append(fast_calo.f1())
        buffer_dict['trig_L2_cl_f3'].append(fast_calo.f3())
        buffer_dict['trig_L2_cl_weta2'].append(fast_calo.weta2())
        buffer_dict['trig_L2_cl_wstot'].append(fast_calo.wstot())
        buffer_dict['trig_L2_cl_e2tsts1'].append(fast_calo.e2tsts1())

        ring_array = fast_calo.ringsE()
        for iring in range(NUMBER_OF_RINGS):
            buffer_dict[f'trig_L2_cl_ring_{iring}'].append(ring_array[iring])
    
    def __add_tracking_info(self, buffer_dict: Dict[str, List[Number]],
                          context: EventContext) -> None:
        """
        Appends tracking variables from fast electron to buffer_dict.
        Executed when only_decorators=False

        Parameters
        ----------
        buffer_dict : Dict[str, List[Number]]
            buffer_dict to append
        context : EventContext
            Current EventContext instance

        Parameters
        ----------
        buffer_dict : Dict[str, List[Number]]
            _description_
        context : EventContext
            _description_
        """
        fcElCont = context.getHandler("HLT__TrigElectronContainer" )

        hasFcTrack = True if fcElCont.size()>0 else False
        if hasFcTrack:
            fcElCont.setToBeClosestThanCluster()
            buffer_dict['trig_L2_el_hastrack'].append(np.int32(True))
            buffer_dict['trig_L2_el_trkClusDeta'].append(fcElCont.trkClusDeta())  
            buffer_dict['trig_L2_el_trkClusDphi'].append(fcElCont.trkClusDphi())
            buffer_dict['trig_L2_el_etOverPt'].append(fcElCont.etOverPt())
            buffer_dict['trig_L2_el_d0'].append(fcElCont.d0())
        else:
            buffer_dict['trig_L2_el_hastrack'].append(np.int32(False))
            buffer_dict['trig_L2_el_trkClusDeta'].append(-1.0)  
            buffer_dict['trig_L2_el_trkClusDphi'].append(-1.0)
            buffer_dict['trig_L2_el_etOverPt'].append(-1.0)
            buffer_dict['trig_L2_el_d0'].append(-1.0)

    def execute(self, context: EventContext) -> StatusCode:

        fast_calo: EDM = context.getHandler( "HLT__TrigEMClusterContainer" )
        
        etBinIdx, etaBinIdx = self.__get_bin( fast_calo.et()/GeV, abs(fast_calo.eta()) )
        if etBinIdx < 0 or etaBinIdx < 0:
            return StatusCode.SUCCESS
        buffer_dict = self.__buffer

        buffer_dict["et_bin"].append(np.int32(etBinIdx))
        buffer_dict["eta_bin"].append(np.int32(etaBinIdx))
        eventInfo: EDM = context.getHandler( "EventInfoContainer" )
        buffer_dict["avgmu"].append(eventInfo.avgmu())
        
        self.__add_offline_decision(buffer_dict, context)
        self.__apply_decorators(buffer_dict, context)        
        self.__apply_chain_decorators(buffer_dict, context)
        if self.__decorate_ringerVersions:
            MSG_DEBUG(self, "Decorate Ringer Versions is True. Adding information to buffer_dict")
            models_dict = self.__models
            self.__add_ringer_decision(buffer_dict, models_dict, context)
            
        store = self.getStoreGateSvc()
        store.histogram("sample/et").Fill(fast_calo.et()/GeV)
        store.histogram("sample/eta").Fill(fast_calo.eta())

        if self.__only_decorators:
            if self.__decorate_rings:
                logger.debug("Decorate Rings is True. Adding Rings information to buffer_dict")
                self.__add_fc_rings(buffer_dict, context)
            return StatusCode.SUCCESS

        self.__add_fast_calo_info(buffer_dict, context)
        self.__add_tracking_info(buffer_dict, context)

        return StatusCode.SUCCESS

    def finalize( self ) -> StatusCode:
        
        #if not os.path.exists(self.output):
        #    os.makedirs(self.output)
        #_, output_dirname = os.path.split(self.output)
        
        buffer_dict = self.__buffer
        df_shape, to_df_buffer = self.__validate_buffer_dict(buffer_dict)
            
        #rdf = ROOT.RDF.MakeNumpyDataFrame(to_df_buffer)
        rdf = ROOT.RDF.FromNumpy(to_df_buffer)
        output_filepath = f"{self.output}.root"
        MSG_INFO(self, "Save RDataFrame into %s with shape (%d,%d)", output_filepath, df_shape[0], df_shape[1])

        rdf_columns = rdf.GetColumnNames()
        options = ROOT.RDF.RSnapshotOptions()
        options.fCompressionLevel = 9
        rdf.Snapshot("tree", 
                     output_filepath,
                     rdf_columns,
                     options
                         )
        
        return StatusCode.SUCCESS

    def __validate_buffer_dict(self, buffer_dict) -> Tuple[Tuple[int, int], Dict[str, np.ndarray]]:
        # It is faster to append a list and convert to array than append to an array
        # https://stackoverflow.com/questions/29839350/numpy-append-vs-python-append
        validated_buffer = dict()
        buffer_len = None
        for key, value in buffer_dict.items():
            value = np.array(value)
            if buffer_len is not None and buffer_len != len(value):
                logger.fatal(f"Buffer has distinct col sizes. Size so far {buffer_len} size found at {key} {len(value)}")
            elif str(value.dtype) == "object":
                logger.fatal(f"{key} raised unsupported type {value.dtype}")
            else:
                logger.debug(f"{key} size {len(value)} dtype {value.dtype}")
                validated_buffer[key] = value
                buffer_len = len(value)
        
        buffer_shape = (buffer_len, len(validated_buffer.keys()))

        return buffer_shape, validated_buffer


    def __get_bin(self, et: Number, eta: Number) -> Tuple[int, int]:
        """
        Returns an etBinIdx and etaBinIdx pair given certain et and eta values.

        Uses numpy.digitize for efficient bin lookup.

        Parameters
        ----------
        et : Number
            Transverse energy value
        eta : Number
            Pseudorapidity value

        Returns
        -------
        Tuple[int, int]
            etBinIdx, etaBinIdx values. Returns (-1, -1) if outside ranges.
        """
        et_idx = np.digitize(et, self.__etbins) - 1
        eta_idx = np.digitize(eta, self.__etabins) - 1

        # Check if indices are within the valid bin range [0, N-1]
        if not (0 <= et_idx < len(self.__etbins) - 1):
            et_idx = -1
        if not (0 <= eta_idx < len(self.__etabins) - 1):
            eta_idx = -1

        if et_idx == -1 or eta_idx == -1:
            return -1, -1

        return int(et_idx), int(eta_idx)

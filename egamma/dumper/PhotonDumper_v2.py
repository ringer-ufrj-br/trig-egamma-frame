"""
Implements the PhotonDumper class and its utilities to dump Photon data
"""

__all__ = ["PhotonDumper_v2"]

from egamma.core import Algorithm, StatusCode, EventContext, EDM
from egamma.core.macros import *
from egamma.core.constants import GeV
from egamma.emulator.run3 import PhotonChain as Chain
from egamma.emulator import attach
from egamma.emulator.run3.menu.ChainDict import get_chain_dict
from egamma.emulator.run3.photon import PHOTON_STEPS
from egamma.emulator.run3.ringer import NUMBER_OF_RINGS
from numbers import Number
from typing import List, Dict, Tuple, Callable, Any, Sequence
from itertools import product

import numpy as np
from collections import OrderedDict
import os
import ROOT

class PhotonDumper_v2( Algorithm ):
    """
    Dumps Photon data into a root file into a tree named tree.
    Can dump chain decisions and custom branches by using decorators.
    """

    def __init__(self, output: str,
                 etbins: Sequence[Number],
                 etabins: Sequence[Number],
                 only_decorators: bool=False,
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
        
        Algorithm.__init__(self, "PhotonDumper")
        
        self.__buffer = np.empty((len(etbins)-1, len(etabins)-1), dtype=object)

        self.__etbins  = etbins
        self.__etabins = etabins
        self.output    = output
        self.features  = []
        self.__decorators = OrderedDict()
        self.__only_decorators= only_decorators
        self.chains = OrderedDict()

    def decorate(self, key: str , f: Callable[[EventContext], Number]):
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

    def decorate_chain(self, chain_name: str):
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
        if self.__only_decorators:
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
            'trig_L2_ph_hastrack': [],
            'trig_L2_ph_trkClusDeta': [],
            'trig_L2_ph_trkClusDphi': [],
            'trig_L2_ph_etOverPt': [],
            'trig_L2_ph_d0': [],
            'ph_lhtight': [],
            'ph_lhmedium': [],
            'ph_lhloose': [],
            'ph_lhvloose': []
        })
        buffer_dict.update({
            f"{step_name}_{chain_name}": []
            for chain_name, step_name in product(self.chains.keys(), PHOTON_STEPS)
        })

        return buffer_dict

    def initialize(self):

        super().initialize()

        store = self.getStoreGateSvc()
        store.mkdir('sample')
        store.addHistogram(ROOT.TH1F('et','E_{T} distribution;E_{T};Count', 100, 0, 150 ))
        store.addHistogram(ROOT.TH1F('eta','#eta distribution;#eta;Count', 50, -2.5, 2.5))
        
        n, m = self.__buffer.shape
        for etBinIdx, etaBinIdx in product(range(n), range(m)):
            self.__buffer[etBinIdx, etaBinIdx] = self.__make_buffer_dict()

        return StatusCode.SUCCESS

    def __add_offline_decision(self, buffer_dict: Dict[str, List[Number]],
                             context: EventContext):
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
        phCont: EDM = context.getHandler("PhotonnContainer")
        buffer_dict["ph_lhtight"].append(np.int32(phCont.accept("ph_lhtight")))
        buffer_dict["ph_lhmedium"].append(np.int32(phCont.accept("ph_lhmedium")))
        buffer_dict["ph_lhloose"].append(np.int32(phCont.accept("ph_lhloose")))
        buffer_dict["ph_lhvloose"].append(np.int32(phCont.accept("ph_lhvloose")))
    
    def __apply_decorators(self, buffer_dict: Dict[str, List[Number]],
                         context: EventContext):
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
                               context: EventContext):
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
            for step_name in PHOTON_STEPS:
                step_chain_name = f"{step_name}_{chain_name}"
                # Casting to int32 to be RDataFrame.MakeNumpyDataFrame compatible
                # default bool neither numpy.bool_ work
                buffer_dict[step_chain_name].append(np.int32(chain_results.getCutResult(step_name)))
    
    def __add_fast_calo_info(self, buffer_dict: Dict[str, List[Number]],
                           context: EventContext):
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
                          context: EventContext):
        """
        Appends tracking variables from fast photon to buffer_dict.
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
        fcElCont = context.getHandler("HLT__TrigPhotonContainer" )

        hasFcTrack = True if fcElCont.size()>0 else False
        if hasFcTrack:
            fcElCont.setToBeClosestThanCluster()
            buffer_dict['trig_L2_ph_hastrack'].append(np.int32(True))
            buffer_dict['trig_L2_ph_trkClusDeta'].append(fcElCont.trkClusDeta())  
            buffer_dict['trig_L2_ph_trkClusDphi'].append(fcElCont.trkClusDphi())
            buffer_dict['trig_L2_ph_etOverPt'].append(fcElCont.etOverPt())
            buffer_dict['trig_L2_ph_d0'].append(fcElCont.d0())
        else:
            buffer_dict['trig_L2_ph_hastrack'].append(np.int32(False))
            buffer_dict['trig_L2_ph_trkClusDeta'].append(-1.0)  
            buffer_dict['trig_L2_ph_trkClusDphi'].append(-1.0)
            buffer_dict['trig_L2_ph_etOverPt'].append(-1.0)
            buffer_dict['trig_L2_ph_d0'].append(-1.0)

    def execute(self, context: EventContext):

        fast_calo: EDM = context.getHandler( "HLT__TrigEMClusterContainer" )
        
        etBinIdx, etaBinIdx = self.__get_bin( fast_calo.et()/GeV, abs(fast_calo.eta()) )
        if etBinIdx < 0 or etaBinIdx < 0:
            return StatusCode.SUCCESS
        buffer_dict = self.__buffer[etBinIdx, etaBinIdx]

        buffer_dict["et_bin"].append(np.int32(etBinIdx))
        buffer_dict["eta_bin"].append(np.int32(etaBinIdx))
        eventInfo: EDM = context.getHandler( "EventInfoContainer" )
        buffer_dict["avgmu"].append(eventInfo.avgmu())

        self.__add_offline_decision(buffer_dict, context)
        self.__apply_decorators(buffer_dict, context)        
        self.__apply_chain_decorators(buffer_dict, context)

        store = self.getStoreGateSvc()
        store.histogram("sample/et").Fill(fast_calo.et()/GeV)
        store.histogram("sample/eta").Fill(fast_calo.eta())

        if self.__only_decorators:
            return StatusCode.SUCCESS

        self.__add_fast_calo_info(buffer_dict, context)
        self.__add_tracking_info(buffer_dict, context)

        return StatusCode.SUCCESS

    def finalize( self ):
        
        n, m = self.__buffer.shape
        if not os.path.exists(self.output):
            os.makedirs(self.output)
        _, output_dirname = os.path.split(self.output)
        for etBinIdx, etaBinIdx in product(range(n), range(m)):
            buffer_dict = self.__buffer[etBinIdx,etaBinIdx]
            df_shape, to_df_buffer = self.__validate_buffer_dict(buffer_dict)
            if df_shape[0] < 1:
                MSG_INFO(self, "RDataFrame (etBinIdx, etaBinIdx) (%d, %d) into with (%d,%d) was empty",
                         etBinIdx, etaBinIdx, df_shape[0], df_shape[1])
                continue
            rdf = ROOT.RDF.MakeNumpyDataFrame(to_df_buffer)
            output_filepath = os.path.join(self.output, f"{output_dirname}_et{etBinIdx}_eta{etaBinIdx}.root")
            MSG_INFO(self, "Save RDataFrame (etBinIdx, etaBinIdx) (%d, %d) into %s with shape (%d,%d)",
                     etBinIdx, etaBinIdx, output_filepath, df_shape[0], df_shape[1])
            rdf.Snapshot("tree", output_filepath)
        
        return StatusCode.SUCCESS

    def __validate_buffer_dict(self, buffer_dict):
        # It is faster to append a list and convert to array than append to an array
        # https://stackoverflow.com/questions/29839350/numpy-append-vs-python-append
        validated_buffer = dict()
        buffer_len = None
        for key, value in buffer_dict.items():
            value = np.array(value)
            if buffer_len is not None and buffer_len != len(value):
                MSG_FATAL(self, f"Buffer has distinct col sizes. Size so far {buffer_len} size found at {key} {len(value)}")
            elif str(value.dtype) == "object":
                MSG_FATAL(self, f"{key} raised unsupported type {value.dtype}")
            else:
                MSG_DEBUG(self, f"{key} size {len(value)} dtype {value.dtype}")
                validated_buffer[key] = value
                buffer_len = len(value)
        
        buffer_shape = (buffer_len, len(validated_buffer.keys()))

        return buffer_shape, validated_buffer


    def __get_bin(self, et: Number, eta: Number) -> Tuple[int, int]:
        """
        Retunrs an etBinIdx and etaBinIdx pair given
        certain et and eta values.

        Parameters
        ----------
        et : Number
            Transverse energy value
        eta : Number
            Pseudorapidity value

        Returns
        -------
        Tuple[int, int]
            etBinIdx, etaBinIdx values
        """
        # Fix eta value if > 2.5
        if eta > self.__etabins[-1]:  eta = self.__etabins[-1]
        if et > self.__etbins[-1]:  et = self.__etbins[-1]
        ### Loop over binnings
        for etBinIdx in range(len(self.__etbins)-1):
            if et >= self.__etbins[etBinIdx] and  et < self.__etbins[etBinIdx+1]:
                for etaBinIdx in range(len(self.__etabins)-1):
                    if eta >= self.__etabins[etaBinIdx] and eta < self.__etabins[etaBinIdx+1]:
                        return etBinIdx, etaBinIdx
        return -1, -1

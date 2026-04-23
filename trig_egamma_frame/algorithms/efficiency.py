
__all__ = ["Efficiency"]




import array
import numpy as np
from tqdm import tqdm
from typing import List, Dict, Optional, Sequence, Any, Union
from ROOT import TH1F, TH2F, TProfile, TProfile2D, TFile
from expand_folders import expand_folders
from copy import deepcopy
from prettytable import PrettyTable

from trig_egamma_frame.kernel import Algorithm, StatusCode, EventContext
from trig_egamma_frame import logger, GeV
from trig_egamma_frame.emulator.run3.menu.ChainDict import get_chain_dict
from trig_egamma_frame.constants import eta_bins_default, zee_et_bins, mu_bins
from trig_egamma_frame.emulator.run3.menu.ChainDict import get_chain_dict
from trig_egamma_frame.emulator import attach
from trig_egamma_frame.emulator.run3 import ElectronChain as Chain


class Efficiency(Algorithm):
    """
    Algorithm to monitor and calculate trigger efficiencies at different levels (L1, Fast, Precision).
    """

    def __init__(self, 
                 name: str, 
                 basepath: str = "trigger",
                 triggers: List[str] = [],
                 etbins: Sequence[float] = zee_et_bins,
                 etabins: Sequence[float] = eta_bins_default,
                 mubins: Sequence[float] = mu_bins,
                 pidname: Optional[str] = None):
        """
        Constructor for the Efficiency algorithm.

        Args:
            name (str): The name of the algorithm instance.
            basepath (str): The base path in StoreGate where histograms will be stored. Defaults to "Trigger".
            triggers (List[str]): List of trigger chain names to monitor.
            etbins (Sequence[float]): Bin edges for the transverse energy (Et) histograms.
            etabins (Sequence[float]): Bin edges for the pseudorapidity (eta) histograms.
            mubins (Sequence[float]): Bin edges for the mu (pileup) or nvtx histograms.
            pidname (Optional[str]): Override for the PID selection name. If None, it uses the trigger's info.
        """
        super().__init__(name)

        self.basepath = basepath
        self.__trigger_names = triggers
        self.triggers = [get_chain_dict(trigName) for trigName in triggers]
        self.etbins = array.array('d', etbins) if not isinstance(etbins, array.array) else etbins
        self.etabins = array.array('d', etabins) if not isinstance(etabins, array.array) else etabins
        self.mubins = array.array('d', mubins) if not isinstance(mubins, array.array) else mubins
        self.pidname = pidname


    def __add__(self, trigName: str) -> 'Efficiency':
        """
        Operator to add a trigger chain to the monitored list.

        Args:
            trigName (str): Name of the trigger chain to add.

        Returns:
            Efficiency: The algorithm instance itself.
        """
        chainPart = get_chain_dict(trigName)
        attach(Chain(trigName))
        self.triggers.append(chainPart)
        return self


    def initialize(self) -> StatusCode:
        """
        Initialize the algorithm, creating the necessary histogram directories and booking histograms.

        Returns:
            StatusCode: StatusCode.SUCCESS if initialization is successful.
        """
        logger.info(f"Initializing {self.name()}...")

        sg = self.getStoreGateSvc()
        
        for chainPart in self.triggers:

            signature = chainPart['signature']
            trigName  = chainPart['trigName']
            if signature == "Electron":
                triggerLevels = ['L1Calo', 'FastCalo', 'FastElectron', 'PrecisionCalo', 'PrecisionElectron']
            elif signature == "Photon":
                triggerLevels = ['L1Calo', 'FastCalo', 'FastPhoton', 'PrecisionCalo', 'PrecisionPhoton']
            else:
                logger.warning(f"Signature '{signature}' not supported for trigger {trigName}")
                continue

            for dirname in triggerLevels:
                path = f"{self.basepath}/{trigName}/Efficiency/{dirname}"
                sg.mkdir(path)
                sg.addHistogram(TH1F('et', 'E_{T} distribution;E_{T};Count', len(self.etbins)-1, np.array(self.etbins)))
                sg.addHistogram(TH1F('highet', 'E_{T} distribution;E_{T};Count', 40, 0, 500))
                sg.addHistogram(TH1F('eta', '#eta distribution;#eta;Count', len(self.etabins)-1, np.array(self.etabins)))
                sg.addHistogram(TH1F("phi", "#phi distribution; #phi ; Count", 20, -3.2, 3.2))
                sg.addHistogram(TH1F('mu', '<#mu> distribution;<#mu>;Count', 20, 0, 100))
                sg.addHistogram(TH1F('nvtx', 'N_{vtx} distribution;N_{vtx};Count', len(self.mubins)-1, np.array(self.mubins)))
                sg.addHistogram(TH1F('match_et', 'E_{T} matched distribution;E_{T};Count', len(self.etbins)-1, np.array(self.etbins)))
                sg.addHistogram(TH1F('match_highet', 'E_{T} distribution;E_{T};Count', 40, 0, 500))
                sg.addHistogram(TH1F('match_eta', '#eta matched distribution;#eta;Count', len(self.etabins)-1, np.array(self.etabins)))
                sg.addHistogram(TH1F("match_phi", "#phi matched distribution; #phi ; Count", 20, -3.2, 3.2))
                sg.addHistogram(TH1F('match_mu', '<#mu> matched distribution;<#mu>;Count', 20, 0, 100))
                sg.addHistogram(TH1F('match_nvtx', 'N_{vtx} matched distribution;N_{vtx};Count', len(self.mubins)-1, np.array(self.mubins)))
                sg.addHistogram(TProfile("eff_et", "#epsilon(E_{T}); E_{T} ; Efficiency", len(self.etbins)-1, np.array(self.etbins)))
                sg.addHistogram(TProfile("eff_highet", "#epsilon(E_{T}); E_{T} ; Efficiency", 40, 0, 500))
                sg.addHistogram(TProfile("eff_eta", "#epsilon(#eta); #eta ; Efficiency", len(self.etabins)-1, np.array(self.etabins)))
                sg.addHistogram(TProfile("eff_phi", "#epsilon(#phi); #phi ; Efficiency", 20, -3.2, 3.2))
                sg.addHistogram(TProfile("eff_mu", "#epsilon(<#mu>); <#mu> ; Efficiency", 20, 0, 100))
                sg.addHistogram(TProfile("eff_nvtx", "#epsilon(N_{vtx}); N_{vtx} ; Efficiency", len(self.mubins)-1, np.array(self.mubins)))
                sg.addHistogram(TH2F('match_etVsEta', "Passed;E_{T};#eta;Count", len(self.etbins)-1, np.array(self.etbins), len(self.etabins)-1, np.array(self.etabins)))
                sg.addHistogram(TH2F('etVsEta', "Total;E_{T};#eta;Count", len(self.etbins)-1, np.array(self.etbins), len(self.etabins)-1, np.array(self.etabins)))
                sg.addHistogram(TProfile2D('eff_etVsEta', "Total;E_{T};#eta;Count", len(self.etbins)-1, np.array(self.etbins), len(self.etabins)-1, np.array(self.etabins)))

        self.init_lock()
        return StatusCode.SUCCESS 


    def fillEfficiency(self, dirname: str, el: Any, etthr: float, pidword: str, isPassed: bool) -> None:
        """
        Utility method to fill the histograms for a specific trigger level.

        Args:
            dirname (str): The full directory path in StoreGate for the histograms.
            el (Any): The electron or photon object being monitored.
            etthr (float): The energy threshold of the trigger chain.
            pidword (str): The PID selection name used to filter the objects.
            isPassed (bool): Whether the trigger level bit was passed.
        """
        sg = self.getStoreGateSvc()
        pid = not el.accept(pidword.replace('!', '')) if '!' in pidword else el.accept(pidword)
        eta = el.caloCluster().etaBE2()
        et = el.et() / GeV
        phi = el.phi()
        evt = self.getContext().getHandler("EventInfoContainer")
        avgmu = evt.avgmu()
        nvtx = evt.nvtx()
        pw = 1

        if pid: 
            sg.histogram(f"{dirname}/et").Fill(et, pw)
            sg.histogram(f"{dirname}/highet").Fill(et, pw)

            if et > etthr + 1.0:
                sg.histogram(f"{dirname}/eta").Fill(eta, pw)
                sg.histogram(f"{dirname}/phi").Fill(phi, pw)
                sg.histogram(f"{dirname}/mu").Fill(avgmu, pw)
                sg.histogram(f"{dirname}/nvtx").Fill(nvtx, pw)
                sg.histogram(f"{dirname}/etVsEta").Fill(et, eta, pw)

            if isPassed:
                sg.histogram(f"{dirname}/match_et").Fill(et, pw)
                sg.histogram(f"{dirname}/match_highet").Fill(et, pw)
                sg.histogram(f"{dirname}/eff_et").Fill(et, 1, pw)
                sg.histogram(f"{dirname}/eff_highet").Fill(et, 1, pw)
                
                if et > etthr + 1.0:
                    sg.histogram(f"{dirname}/match_eta").Fill(eta, pw)
                    sg.histogram(f"{dirname}/match_phi").Fill(phi, pw)
                    sg.histogram(f"{dirname}/match_mu").Fill(avgmu, pw)
                    sg.histogram(f"{dirname}/match_nvtx").Fill(nvtx, pw)
                    sg.histogram(f"{dirname}/match_etVsEta").Fill(et, eta, pw)
                    sg.histogram(f"{dirname}/eff_eta").Fill(eta, 1, pw)
                    sg.histogram(f"{dirname}/eff_phi").Fill(phi, 1, pw)
                    sg.histogram(f"{dirname}/eff_mu").Fill(avgmu, 1, pw)
                    sg.histogram(f"{dirname}/eff_nvtx").Fill(nvtx, 1, pw)
                    sg.histogram(f"{dirname}/eff_etVsEta").Fill(et, eta, 1, pw)
            else:
                sg.histogram(f"{dirname}/eff_et").Fill(et, 0)
                sg.histogram(f"{dirname}/eff_highet").Fill(et, 0)

                if et > etthr + 1.0:
                    sg.histogram(f"{dirname}/eff_eta").Fill(eta, 0, pw)
                    sg.histogram(f"{dirname}/eff_phi").Fill(phi, 0, pw)
                    sg.histogram(f"{dirname}/eff_mu").Fill(avgmu, 0, pw)
                    sg.histogram(f"{dirname}/eff_nvtx").Fill(nvtx, 0, pw)
                    sg.histogram(f"{dirname}/eff_etVsEta").Fill(et, eta, 0, pw)


    def execute(self, context: EventContext) -> StatusCode:
        """
        Main execution loop of the algorithm. Called once per event.

        Args:
            context (EventContext): The context for the current event.

        Returns:
            StatusCode: StatusCode.SUCCESS.
        """
        super().execute(context)
        dec = context.getHandler("MenuContainer")

        for chainPart in self.triggers:

            signature = chainPart['signature']
            trigName  = chainPart['trigName']

            pidname   = self.pidname if self.pidname else chainPart['IDinfo']
            etthr     = chainPart['threshold']

            if signature == "Electron":
                triggerLevels = ['L1Calo', 'FastCalo', 'FastElectron', 'PrecisionCalo', 'PrecisionElectron']
                egCont = context.getHandler("ElectronContainer")
                pidname = f'el_{pidname}'
            elif signature == "Photon":
                triggerLevels = ['L1Calo', 'FastCalo', 'FastPhoton', 'PrecisionCalo', 'PrecisionPhoton']
                egCont = context.getHandler("PhotonContainer")
                pidname = f'ph_{pidname}'
            else:
                logger.warning(f"Signature '{signature}' not supported for trigger {trigName}")
                continue

            for eg in egCont:
                if eg.et() < (etthr - 5) * GeV:
                    continue 
                if abs(eg.eta()) > 2.47:
                    continue
                dirname = f"{self.basepath}/{trigName}/Efficiency"
                accept = dec.accept(trigName)
                  
                for trigLevel in triggerLevels:
                    self.fillEfficiency(f"{dirname}/{trigLevel}", eg, etthr, pidname, accept.getCutResult(trigLevel))
               
        return StatusCode.SUCCESS 


    def finalize(self) -> StatusCode:
        """
        Finalize the algorithm, printing a summary table of the calculated efficiencies.

        Returns:
            StatusCode: StatusCode.SUCCESS.
        """
        sg = self.getStoreGateSvc()
        for chainPart in self.triggers:
            
            signature = chainPart['signature']
            trigName  = chainPart['trigName']
            if signature == "Electron":
                triggerLevels = ['L1Calo', 'FastCalo', 'FastElectron', 'PrecisionCalo', 'PrecisionElectron']
            elif signature == "Photon":
                triggerLevels = ['L1Calo', 'FastCalo', 'FastPhoton', 'PrecisionCalo', 'PrecisionPhoton']
            else:
                continue

            logger.info(f"{trigName:-^78}")

            for trigLevel in triggerLevels:
                dirname = f"{self.basepath}/{trigName}/Efficiency/{trigLevel}"
                total  = sg.histogram(f"{dirname}/eta").GetEntries()
                passed = sg.histogram(f"{dirname}/match_eta").GetEntries()
                eff = (passed / float(total) * 100.) if total > 0 else 0
                
                stroutput = f'| {trigLevel:<30} | {eff:<8.2f} ({int(passed):<5}, {int(total):<5}) |'
                logger.info(stroutput)
          
            logger.info(f"{'-':-^78}")
        
        self.fina_lock()
        return StatusCode.SUCCESS 



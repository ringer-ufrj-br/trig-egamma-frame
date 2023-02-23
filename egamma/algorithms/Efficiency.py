

__all__ = ["Efficiency"]


from egamma import Algorithm
from egamma import StatusCode
from egamma import declareProperty
from egamma.core.macros import *
from egamma.emulator.run3.menu.ChainDict import get_chain_dict
from egamma.algorithms.constants import etabins, zee_etbins, mubins
from egamma import GeV

from ROOT import TH1F,TH2F,TProfile, TProfile2D

import numpy as np
import array

class Efficiency(Algorithm):

  def __init__(self, name,  **kw):
    Algorithm.__init__(self, name)


    declareProperty(self, kw, "basepath"      , "Efficiency")
    declareProperty(self, kw, "triggers"      , []          )
    declareProperty(self, kw, "etbins"        , zee_etbins  )
    declareProperty(self, kw, "etabins"       , etabins     )
    declareProperty(self, kw, "mubins"        , mubins      )
    declareProperty(self, kw, "applyOffline"  , True        )

    self.triggers   = [get_chain_dict(trigName) for trigName in self.triggers]
    self.etbins     = array.array('d',self.etbins) if not type(self.etbins) is array.array else self.etbins
    self.etabins    = array.array('d',self.etabins) if not type(self.etabins) is array.array else self.etabins
    self.mubins     = array.array('d',self.mubins) if not type(self.mubins) is array.array else self.mubins
    #self.deltaRbins = array.array('d',deltaRbins) if not type(deltaRbins) is array.array else deltaRbins


  def __add__(self, trigName):
    chainPart = get_chain_dict(trigName)
    self.triggers.append(chainPart)
    return self

  #
  # Initialize method
  #
  def initialize(self):
    
    MSG_INFO(self, f"Initalizing {self.name()}...")

    sg = self.getStoreGateSvc()
    
    for chainPart in self.triggers:

      signature = chainPart['signature']
      trigName  = chainPart['trigName']
      if signature == "Electron":
        triggerLevels = ['L1Calo','FastCalo','FastElectron','PrecisionCalo','PrecisionElectron']
      elif signature == "Photon":
        triggerLevels = ['L1Calo','FastCalo','FastPhoton','PrecisionCalo','PrecisionPhoton']
      else:
        MSG_WARNING(self, 'Signature not supported')
        continue

      for dirname in triggerLevels:

        sg.mkdir( self.basepath +'/'+trigName+'/Efficiency/'+dirname )
        sg.addHistogram(TH1F('et','E_{T} distribution;E_{T};Count', len(self.etbins)-1, np.array(self.etbins)))
        sg.addHistogram(TH1F('eta','#eta distribution;#eta;Count', len(self.etabins)-1, np.array(self.etabins)))
        sg.addHistogram(TH1F("phi", "#phi distribution; #phi ; Count", 20, -3.2, 3.2))
        sg.addHistogram(TH1F('mu' ,'<#mu> distribution;<#mu>;Count', 20, 0, 100))
        sg.addHistogram(TH1F('nvtx' ,'N_{vtx} distribution;N_{vtx};Count', len(self.mubins)-1, np.array(self.mubins)))
        sg.addHistogram(TH1F('match_et','E_{T} matched distribution;E_{T};Count', len(self.etbins)-1, np.array(self.etbins)))
        sg.addHistogram(TH1F('match_eta','#eta matched distribution;#eta;Count', len(self.etabins)-1, np.array(self.etabins)))
        sg.addHistogram(TH1F("match_phi", "#phi matched distribution; #phi ; Count", 20, -3.2, 3.2))
        sg.addHistogram(TH1F('match_mu' ,'<#mu> matched distribution;<#mu>;Count', 20, 0, 100))
        sg.addHistogram(TH1F('match_nvtx' ,'N_{vtx} matched distribution;N_{vtx};Count', len(self.mubins)-1, np.array(self.mubins)))
        sg.addHistogram(TProfile("eff_et", "#epsilon(E_{T}); E_{T} ; Efficiency" , len(self.etbins)-1, np.array(self.etbins)))
        sg.addHistogram(TProfile("eff_eta", "#epsilon(#eta); #eta ; Efficiency"  , len(self.etabins)-1,np.array(self.etabins)))
        sg.addHistogram(TProfile("eff_phi", "#epsilon(#phi); #phi ; Efficiency", 20, -3.2, 3.2))
        sg.addHistogram(TProfile("eff_mu", "#epsilon(<#mu>); <#mu> ; Efficiency", 20, 0, 100))
        sg.addHistogram(TProfile("eff_nvtx", "#epsilon(N_{vtx}); N_{vtx} ; Efficiency", len(self.mubins)-1, np.array(self.mubins)))
        sg.addHistogram( TH2F('match_etVsEta', "Passed;E_{T};#eta;Count", len(self.etbins)-1, np.array(self.etbins), len(self.etabins)-1, np.array(self.etabins)) )
        sg.addHistogram( TH2F('etVsEta' , "Total;E_{T};#eta;Count", len(self.etbins)-1,  np.array(self.etbins), len(self.etabins)-1, np.array(self.etabins)) )
        sg.addHistogram( TProfile2D('eff_etVsEta' , "Total;E_{T};#eta;Count", len(self.etbins)-1,  np.array(self.etbins), len(self.etabins)-1, np.array(self.etabins)) )

        # for boosted analysis
        #deltaR_bins = np.arange(0, 5, step=0.1)
        #sg.addHistogram(TH1F('deltaR','#\Delta R distribution;#\Delta R;Count', len(deltaR_bins)-1, deltaR_bins))
        #sg.addHistogram(TH1F('match_deltaR','#\Delta R matched distribution;#\Delta R;Count', len(deltaR_bins)-1, deltaR_bins))
        #sg.addHistogram(TProfile('eff_deltaR', "#\epsilon(#\Delta R); #\Delta R ; Efficiency" , len(deltaR_bins)-1, deltaR_bins))

    self.init_lock()
    return StatusCode.SUCCESS 




  #
  # Fill efficiency histograms
  #
  def fillEfficiency( self, dirname, el, etthr, pidword, isPassed ):
  
    sg = self.getStoreGateSvc()

    pid = el.accept(pidword) if pidword else True
    eta = el.caloCluster().etaBE2()
    et = el.et()/GeV
    phi = el.phi()
    evt = self.getContext().getHandler("EventInfoContainer")
    avgmu = evt.avgmu()
    nvtx = evt.nvtx()
    pw = 1


    #deltaR = el.deltaR()
    if pid: 
      sg.histogram( dirname+'/et' ).Fill(et, pw)
      if et > etthr+1.0:
        sg.histogram( dirname+'/eta' ).Fill(eta, pw)
        sg.histogram( dirname+'/phi' ).Fill(phi, pw)
        sg.histogram( dirname+'/mu' ).Fill(avgmu, pw)
        sg.histogram( dirname+'/nvtx' ).Fill(nvtx, pw)
        sg.histogram( dirname+'/etVsEta' ).Fill(et,eta, pw)
        #sg.histogram( dirname+'/deltaR' ).Fill(deltaR, pw)

      if isPassed:
        sg.histogram( dirname+'/match_et' ).Fill(et, pw)
        sg.histogram( dirname+'/eff_et' ).Fill(et,1, pw)
        
        if et > etthr+1.0:
          sg.histogram( dirname+'/match_eta' ).Fill(eta, pw)
          sg.histogram( dirname+'/match_phi' ).Fill(phi, pw)
          sg.histogram( dirname+'/match_mu' ).Fill(avgmu, pw)
          sg.histogram( dirname+'/match_nvtx' ).Fill(nvtx, pw)
          #sg.histogram( dirname+'/match_deltaR' ).Fill(deltaR, pw)
          
          sg.histogram( dirname+'/match_etVsEta' ).Fill(et,eta, pw)
          sg.histogram( dirname+'/eff_eta' ).Fill(eta,1, pw)
          sg.histogram( dirname+'/eff_phi' ).Fill(phi,1, pw)
          sg.histogram( dirname+'/eff_mu' ).Fill(avgmu,1, pw)
          sg.histogram( dirname+'/eff_nvtx' ).Fill(nvtx,1, pw)
          sg.histogram( dirname+'/eff_etVsEta' ).Fill(et,eta,1, pw)
          #sg.histogram( dirname+'/eff_deltaR' ).Fill(deltaR, 1, pw)

      else:
        sg.histogram( dirname+'/eff_et' ).Fill(et,0)
        if et > etthr+1.0:
          sg.histogram( dirname+'/eff_eta' ).Fill(eta,0, pw)
          sg.histogram( dirname+'/eff_phi' ).Fill(phi,0, pw)
          sg.histogram( dirname+'/eff_mu' ).Fill(avgmu,0, pw)
          sg.histogram( dirname+'/eff_nvtx' ).Fill(nvtx,0, pw)
          sg.histogram( dirname+'/eff_etVsEta' ).Fill(et,eta,0, pw)
          #sg.histogram( dirname+'/eff_deltaR' ).Fill(deltaR,0, pw)



  def execute(self, context):
  
    dec = context.getHandler("MenuContainer")

    for chainPart in self.triggers:

      signature = chainPart['signature']
      trigName  = chainPart['trigName']

      pidname   = chainPart['IDinfo']
      etthr     = chainPart['threshold']

      if signature == "Electron":
        triggerLevels = ['L1Calo','FastCalo','FastElectron','PrecisionCalo','PrecisionElectron']
        egCont = context.getHandler("ElectronContainer")
        pidname = 'el_'+pidname
      elif signature == "Photon":
        triggerLevels = ['L1Calo','FastCalo','FastPhoton','PrecisionCalo','PrecisionPhoton']
        egCont = context.getHandler("PhotonContainer")
        pidname = 'ph_'+pidname
      else:
        MSG_WARNING(self, 'Signature not supported')
        continue

      # overwrite pidname to disable the cut
      if not self.applyOffline:
        pidname = None

      for eg in egCont:
        if eg.et()  < (etthr- 5)*GeV:  continue 
        if abs(eg.eta())>2.47: continue
        dirname = self.basepath+'/'+trigName+'/Efficiency'
        accept = dec.accept( trigName )
          
        for trigLevel in triggerLevels:
          self.fillEfficiency(dirname+'/'+trigLevel, eg, etthr, pidname, accept.getCutResult(trigLevel) )
       
    return StatusCode.SUCCESS 



  #
  # Finalize method
  #
  def finalize(self):
    
    sg = self.getStoreGateSvc()
    for chainPart in self.triggers:
      
      signature = chainPart['signature']
      trigName  = chainPart['trigName']
      if signature == "Electron":
        triggerLevels = ['L1Calo','FastCalo','FastElectron','PrecisionCalo','PrecisionElectron']
      elif signature == "Photon":
        triggerLevels = ['L1Calo','FastCalo','FastPhoton','PrecisionCalo','PrecisionPhoton']
      else:
        MSG_WARNING(self, 'Signature not supported')
        continue

      MSG_INFO( self, '{:-^78}'.format((' %s ')%(trigName)))

      for trigLevel in triggerLevels:
        dirname = self.basepath+'/'+trigName+'/Efficiency/'+trigLevel
        total  = sg.histogram( dirname+'/eta' ).GetEntries()
        passed = sg.histogram( dirname+'/match_eta' ).GetEntries()
        eff = passed/float(total) * 100. if total>0 else 0
        eff=('%1.2f')%(eff); passed=('%d')%(passed); total=('%d')%(total)
        stroutput = '| {0:<30} | {1:<5} ({2:<5}, {3:<5}) |'.format(trigLevel,eff,passed,total)
        MSG_INFO( self, stroutput)
  
      MSG_INFO(self, '{:-^78}'.format((' %s ')%('-')))
    
    self.fina_lock()
    return StatusCode.SUCCESS 


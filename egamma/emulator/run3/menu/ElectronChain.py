
__all__ = ["ElectronChain"]


from egamma.core import Messenger
from egamma.core.macros  import *
from egamma.emulator.run3.menu.ChainDict import get_chain_dict
from pprint import pprint



class ElectronChain(Messenger):

  def __init__(self, trigName):
    
    Messenger.__init__(self)
    self.trigName = trigName
    self.chainPart = get_chain_dict(self.trigName)
    pprint(self.chainPart)
    self.sequences = self.prepareSequence()
    print(self.sequences)

    self.compile()


  # adapt from: https://gitlab.cern.ch/atlas/athena/-/blob/master/Trigger/TriggerCommon/TriggerMenuMT/python/HLT/Electron/ElectronChainConfiguration.py
  # ----------------------
  # Prepare the sequence
  # ----------------------
  def prepareSequence(self):
      # This function prepares the list of step names from which assembleChainImpl would make the chain assembly from.
      
      # --------------------
      # define here the names of the steps and obtain the chainStep configuration
      # --------------------
      stepNames = ["getL1Calo"] # This will contain the name of the steps we will want to configure
      # Step1
      # Put first fast Calo. Two possible variants now: 
      # getFastCalo 
      # getFastCalo_fwd
      # But first, we need to check whether this is a chain that will run smth at fast or precision. So if no L2IDAlg or IDinfo defined, just return this here
      if not self.chainPart['IDinfo'] and not self.chainPart['L2IDAlg'] and not self.chainPart['isoInfo'] and not self.chainPart['addInfo']:
          return stepNames
      if "fwd" in self.chainPart['addInfo']:
          stepNames += ['getFastCalo_fwd']
          
          # Actually, if its fwd and etcut we will stop here (for now)
          if "etcut" in self.chainPart['addInfo']:
              return stepNames
      else:
          stepNames += ['getFastCalo']
      # Step2
      # Now lets do Fast Electron. Possible Flavours:
      # getFastTracking
      # getFastTracking_lrt
      if self.chainPart['lrtInfo']:
          stepNames += ['getFastTracking_lrt']
      else:
          stepNames += ['getFastTracking'] 
      # Step3
      # Now lets do Fast Electron. Possible Flavours:
      # getFastElectron
      # getFastElectron_lrt
      if self.chainPart['lrtInfo']:
          stepNames += ['getFastElectron_lrt']
      else:
          stepNames += ['getFastElectron']
      # Step4
      # After Fast Electron we have to build PrecisionCalo for electorns. Current available variantas are:
      # getPrecisionCaloElectron
      # getPrecisionCaloElectron_lrt
      # Now, we will add this if there is any IDInfo (i.e. any of dnn* or lh* in the chain name). Otherwise we wont run precision steps
      
      if not self.chainPart['IDinfo'] and not self.chainPart['isoInfo'] and not self.chainPart['addInfo']: 
          MSG_DEBUG(self, "No IDInfo, no isoInfo and no addInfo. Returning here up to fastElectron")
          return stepNames
      if self.chainPart['lrtInfo']:
          stepNames += ['getPrecisionCaloElectron_lrt']
      else:
          stepNames += ['getPrecisionCaloElectron']
      # If its an etcut chain, we will not run precision Tracking Electron. Just precision Calo. So returning here if its an etcut chain unless its an etcut_idperf chaiin:
      
      if 'etcut' in self.chainPart['addInfo'] and 'idperf' not in self.chainPart['idperfInfo']:
          MSG_DEBUG(self, "This is an etcut chain. Returning here")
          return stepNames
      # Step5
      # After precisionCalo Electron we have to do precision tracking next. Current available variantas are:
      # getPrecisionTracking
      # getPrecisionTracking_lrt
      if self.chainPart['lrtInfo']:
          stepNames += ['getPrecisionTracking_lrt']
      else:
          stepNames += ['getPrecisionTracking']
      # Step6
      # Now if a chain is configured to do gsf refitting we need to add another tracking step for the GSF refitting:
      # getPrecisionTrack_GSFRefitted
      # getPrecisionTrack_GSFRefitted_lrt
      if "" in self.chainPart['gsfInfo'] and 'nogsf' not in self.chainPart['gsfInfo']:
          if self.chainPart['lrtInfo']:
              stepNames += ['getPrecisionTrack_GSFRefitted_lrt']
          else:
              stepNames += ['getPrecisionTrack_GSFRefitted']
      # if its nogsf, then we need to add an addtional empty step to keep aligned the gsf chains (with the additional refitting)     
      else:
          if 'idperf' not in self.chainPart['idperfInfo']:
              # Only add an empty refiting step if its not an idperf - nonGSF. Otherwise the last step will be an empty step and that doesnt work
              stepNames += ['getEmptyRefitStep']
         
          
      # If its an idperf chain, we will not run precision Electron. Just precision Calo and Precision Tracking so returning here if its an etcut chain
      if 'idperf' in self.chainPart['idperfInfo']:
          MSG_DEBUG(self, "This is an idperf chain. Returning here")
          return stepNames
      # Step7
      # and Finally! once we have precision tracking adn precision calo, we can build our electrons!. Current available variantas are:
      # getPrecisionElectron
      # getPrecisionGSFElectron
      # getPrecisionElectron_lrt
      if "nogsf" in self.chainPart['gsfInfo']:
          if self.chainPart['lrtInfo']:
              stepNames += ['getPrecisionElectron_lrt']
          else:
              stepNames += ['getPrecisionElectron']
      
      else:
          if self.chainPart['lrtInfo']:
              stepNames += ['getPrecisionGSFElectron_lrt']
          else:
              stepNames += ['getPrecisionGSFElectron']
      MSG_DEBUG(self, "Returning chain with all steps in the sequence")
      return stepNames


  def compile(self):
    hypos = []
    for name in self.sequences:
        hypo = getattr(self, name)()
        if hypo:
          hypos.append(hypo)

    print(hypos)
      

  #
  # Configure L1 trigger
  #
  def getL1Calo(self):
    from egamma.emulator.run3.electron.step0_hypo import configure

    name = "L1Calo__" + self.trigName
    hypo = configure( name , self.chainPart)
    return hypo


  def getFastCalo(self):
    from egamma.emulator.run3.electron.step1_hypo import configure
    name = "L2Calo__" + self.trigName
    hypo = configure( name , self.chainPart)
    return hypo

  def getFastElectron(self):
    from egamma.emulator.run3.electron.step2_hypo import configure
    name = "L2Electron__" + self.trigName
    hypo = configure( name , self.chainPart)
    return hypo

  def getFastTracking(self):
    return None

  def getPrecisionCaloElectron(self):
    from egamma.emulator.run3.electron.step3_hypo import configure
    name = "PrecisionCalo__" + self.trigName
    hypo = configure( name , self.chainPart)
    return hypo


    return None

  def getPrecisionTracking(self):
    return None

  def getPrecisionTrack_GSFRefitted(self):
    return None

  def getPrecisionGSFElectron(self):
    return None





#
# Local test
#
if __name__ == "__main__":


    trigger_list = [
                    'HLT_e26_lhtight_ivarloose_L1EM22VHI',
                    #'HLT_e28_lhtight_ivarloose_noringer_nogsg_lrtmedium_L1EM22VHI',
                    #'HLT_e60_etcut_L1EM26M',
                    #'HLT_e60_nopid_L1EM26M',
                    ]

    for trigger in trigger_list:


        chain = ElectronChain(trigger)






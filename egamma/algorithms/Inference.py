

__all__ = ["Inference"]


from egamma import Algorithm
from egamma import StatusCode
from egamma import declareProperty
from egamma.core.macros import *
from egamma.emulator.run3.menu.ChainDict import get_chain_dict
from egamma.algorithms.constants import etabins, zee_etbins, mubins
from egamma import GeV

from ROOT import TH1F, TH2F, TProfile, TProfile2D

import numpy as np
import array


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


class Inference(Algorithm):
    def __init__(self, name,  **kw):
        Algorithm.__init__(self, name)

        declareProperty(self, kw, "basepath", "Inference")
        declareProperty(self, kw, "hypos", [])
        declareProperty(self, kw, "etbins", [
                        2, 7, 10, 15, 20, 30, 40, 50, 1000000])
        declareProperty(self, kw, "etabins", [
                        0.0, 0.8, 1.37, 1.54, 2.37, 2.50])

        self.hypos = self.hypos
        self.etbins = array.array('d', self.etbins) if not type(
            self.etbins) is array.array else self.etbins
        self.etabins = array.array('d', self.etabins) if not type(
            self.etabins) is array.array else self.etabins

    def __add__(self, trigName):
        chainPart = get_chain_dict(trigName)
        self.triggers.append(chainPart)
        return self

    def RetrieveBinningIdx(self, et, eta):
        # Fix eta value if > 2.5
        if eta > self.etabins[-1]:
            eta = self.etabins[-1]
        if et > self.etbins[-1]:
            et = self.etbins[-1]
        # Loop over binnings
        for etBinIdx in range(len(self.etbins)-1):
            if et >= self.etbins[etBinIdx] and et < self.etbins[etBinIdx+1]:
                for etaBinIdx in range(len(self.etabins)-1):
                    if eta >= self.etabins[etaBinIdx] and eta < self.etabins[etaBinIdx+1]:
                        return etBinIdx, etaBinIdx
        return -1, -1

    #
    # Initialize method
    #
    def initialize(self):
        MSG_INFO(self, f"Initalizing {self.name()}...")

        sg = self.getStoreGateSvc()

        for etBinIdx in range(len(self.etbins)-1):
            # loop over etas...
            for etaBinIdx in range(len(self.etabins)-1):
                # loop over quadrants...
                binning_name = ('et%d_eta%d') % (etBinIdx, etaBinIdx)
                for model, model_name in self.hypos:
                    sg.mkdir(self.basepath + '/'+binning_name+'/'+model_name)
                    sg.addHistogram(
                        TH1F('out_lin', 'NN Linear distribution;NN Linear Output;Count', 100, -20, 10))
                    sg.addHistogram(
                        TH1F('out_sig', 'NN Sigmoid distribution;NN Sigmoid Output;Count', 100, 0, 1))
                    sg.addHistogram(
                        TH1F('dec', 'NN Decision distribution;NN Decision;Count', 2, 0, 1))

        for imodel, imodel_name in self.hypos:
            imodel.initialize()
        self.init_lock()
        return StatusCode.SUCCESS

    #
    # Fill histograms
    #

    def fillValidationHists(self, dirname, nn_linear_output, nn_sigmoid_output, nn_decision):
        
        MSG_INFO(self, 'Filling histograms!')
        sg = self.getStoreGateSvc()
        
        sg.histogram(dirname+'/out_lin').Fill(nn_linear_output, 1)
        sg.histogram(dirname+'/out_sig').Fill(nn_sigmoid_output, 1)
        sg.histogram(dirname+'/dec').Fill(nn_decision, 1)

    def execute(self, context):

        cl = context.getHandler("HLT__TrigEMClusterContainer")
        etBinIdx, etaBinIdx = self.RetrieveBinningIdx(
            cl.et()/GeV, abs(cl.eta()))
        if etBinIdx == -1 and etaBinIdx == -1:
            MSG_WARNING(self, 'Binning not found!')
            return StatusCode.SUCCESS

        binning_name = ('et%d_eta%d') % (etBinIdx, etaBinIdx)
        for model, model_name in self.hypos:
            out_lin = model.predict(context)
            out_sig = sigmoid(out_lin)
            dec = model.accept(context, out_lin)

            dirname = self.basepath + '/'+binning_name+'/'+model_name
            print('MICA AQUI %s | %1.5f | %1.5f | %1.2f' %
                  (dirname, out_lin, out_sig, dec))
            self.fillValidationHists(dirname, out_lin, out_sig, dec)

        return StatusCode.SUCCESS

    #
    # Finalize method
    #

    def finalize(self):
        self.fina_lock()
        return StatusCode.SUCCESS

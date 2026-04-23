
import os, glob, subprocess



#output_format = 'mc21_13p6TeV.801272.P8B_A14_CTEQ6L1_Jpsie.801278.Py8EG_A14NNPDF23LO_perf_JF17.40bins.et%d_eta%d.h5'
output_format = 'mc21_13p6TeV.601189.PhPy8EG_AZNLO_Zee.801278.Py8EG_A14NNPDF23LO_perf_JF17.40bins.et%d_eta%d.h5'

limit     = 2000000 # 2M events


files = glob.glob('data/*')


procs = []

for et_bin in range(3, 8):

    procs = []
    for eta_bin in range(5):
        inputs = ''
        output = output_format%(et_bin,eta_bin)
        for basepath in files:
            name = basepath.split('/')[-1]
            path = basepath+'/'+name+f'.et{et_bin}_eta{eta_bin}.pic'
            inputs+=path+' '
        command = 'merge_data.py -i %s -o %s -l %d'%(inputs,output,limit)
        command = command.replace('  ', ' ')
        proc = subprocess.Popen(command.split(' '))
        procs.append(proc)

    busy=True
    while busy:
        busy=False
        for proc in procs:
            if proc.poll() is None:
                busy=True

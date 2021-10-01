from __future__ import print_function
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets

import ipywidgets as widgets
import scipy.io as sio
import matplotlib.pyplot as plt
import numpy as np
from pylab import *

#######################################

TFE = sio.loadmat('TFpy.mat')
TF = np.array(TFE['TFE'])
mu = np.array(TFE['mu'])

TF = TF.ravel()
mu = mu.ravel()

z = np.polyfit(mu, TF, 20)
p = np.poly1d(z)

def trasfFunc(p,mu):
    mu = np.maximum(mu,-2000)
    pp = p(mu)
    pp = np.minimum(pp,140)
    pp = np.maximum(pp,0)
    return pp

#######################################

#Simulations Parameters

dt = 0.04#(s)
tauW = 0.1#(s)
TIME = 600

#load Inferred Parameters

InferredParameters = sio.loadmat('InferredParameters_py.mat')
K = np.transpose( np.array(InferredParameters['kLat']) )
b = np.array(InferredParameters['bs'])
Iext = np.transpose(np.array(InferredParameters['ExcDrive']))*.95

xPos = np.array(InferredParameters['x_pos_sel'])
yPos = np.array(InferredParameters['y_pos_sel'])

N = np.shape(Iext)[1]


nuE = np.zeros((TIME,N),dtype=float)
muE = np.zeros((TIME,N),dtype=float)
W = np.zeros((TIME,N),dtype=float)

times = np.arange(TIME)*dt

def run_and_plot(I0,b_0,b_amp,state):

    I_down,b_down = [.7,1.7]
    I_up,b_up = [1.4,.5]
    I_so,b_so = [1.0,.9]
    I_sp,b_sp = [.9,1.05]
    I_long_up,b_long_up = [1.27,0.77]
    I_HF,b_HF = [1.4,1.9]
    I_doublets,b_doublets,b_amp_doublets = [1.,1.29,0.31]
    I_SOMA,b_SOMA,b_amp_SOMA = [1.41,0.91,0.39]


    if state == 'HAS':
        I0 = I_up
        b_0 = b_up
        b_amp = 0.

    if state == 'LAS':
        I0 = I_down
        b_0 = b_down
        b_amp = 0.

    if state == 'Planar Slow Waves':
        I0 = I_so
        b_0 = b_so
        b_amp = 0.

    if state == 'Spiral Slow Waves':
        I0 = I_sp
        b_0 = b_sp
        b_amp = 0.

    if state == 'Long Up State':
        I0 = I_long_up
        b_0 = b_long_up
        b_amp = 0.

    if state == 'High Freq Waves':
        I0 = I_HF
        b_0 = b_HF
        b_amp = 0.

    if state == 'Doublets':
        I0 = I_doublets
        b_0 = b_doublets
        b_amp = b_amp_doublets

    if state == 'Waves MA':
        I0 = I_SOMA
        b_0 = b_SOMA
        b_amp = b_amp_SOMA


    for t in range(TIME-1):

        b_osc = b_amp*cos(t*.07)

        W[t+1,:] = W[t,:] + dt*( -W[t,:]/tauW + nuE[t,:] )

        muE[t,:] =   np.matmul(nuE[t,:],K)  + Iext*I0 - W[t,:]*(b_0+b_osc)*(b)

        TFE = trasfFunc(p,   muE[t,:] )  #
        nuE[t+1,:] =   np.maximum(TFE + np.random.randn(1,N)*1,0)

    ndx1 = int(floor(N/10))
    ndx2 = int(floor( N/5))
    ndx3 = int(floor(N/2))

    plt.figure(figsize=(14, 6), dpi=80)

    plt.subplot(221)

    plt.plot(times,nuE[:,ndx1])
    plt.plot(times,nuE[:,ndx2])
    plt.plot(times,nuE[:,ndx3])
    plt.ylim([0,100])
   # plt.xlabel('time (s)')
    plt.ylabel('f.r. (Hz)', fontsize=15)
    #plt.legend('123')

    plt.subplot(223)
    plt.imshow(nuE.T, aspect='auto',cmap= 'hot', extent=[0,25,0,N])
    plt.clim(0,60)
    plt.xlabel('time (s)', fontsize=15)
    plt.ylabel('population id.', fontsize=15)


    plt.subplot(122)
    plt.plot(I0,  b_0,'o',linewidth=2, markersize=12)
    plt.plot([I0, I0], [ b_0-b_amp, b_0+b_amp ],'r-')

    plt.xlim([0.6,1.5])
    plt.ylim([0.1,2])
    plt.xlabel('$I_{factor}$', fontsize=15)
    plt.ylabel('$b_{factor}$', fontsize=15)

    plt.plot( I_down,b_down,'rx',linewidth=2, markersize=5)
    plt.annotate('LAS', (I_down,b_down))

    plt.plot( I_up,b_up,'rx',linewidth=2, markersize=5)
    plt.annotate('HAS', (I_up,b_up))

    plt.plot( I_so,b_so,'rx',linewidth=2, markersize=5)
    plt.annotate('Planar Slow Waves', (I_so,b_so))

    plt.plot( I_sp,b_sp,'rx',linewidth=2, markersize=5)
    plt.annotate('Spiral Slow Waves', (I_sp,b_sp))

    plt.plot( I_long_up,b_long_up,'rx',linewidth=2, markersize=5)
    plt.annotate('Long Up States', (I_long_up,b_long_up))

    plt.plot( I_HF,b_HF,'rx',linewidth=2, markersize=5)
    plt.annotate('High Frequency Waves', (I_HF-.3,b_HF))

    plt.plot( I_doublets,b_doublets,'rx',linewidth=2, markersize=5)
    #plt.plot([I_doublets, I_doublets], [ b_doublets-b_amp_doublets, b_doublets+b_amp_doublets ],'g-',linewidth=2)
    plt.annotate('Waves Doublets', (I_doublets,b_doublets))

    plt.plot( I_SOMA,b_SOMA,'rx',linewidth=2, markersize=5)
    #plt.plot([I_doublets, I_doublets], [ b_doublets-b_amp_doublets, b_doublets+b_amp_doublets ],'g-',linewidth=2)
    plt.annotate('Waves MA', (I_SOMA,b_SOMA))

    #plt.savefig('fig1.eps')

    fig, axs = plt.subplots(2,6,figsize=(16, 5))

    t_0 = 100

    for n_plot in range(12):
        t_ndx = n_plot*2+t_0
        Grid = np.zeros((50,50),dtype=float)+60
        for k in range(N-1):
            Grid[xPos[0,k]-1,yPos[0,k]-1] = nuE[t_ndx,k]
        img = axs[int(floor(n_plot/6)),n_plot%6].imshow(Grid.T,cmap='hot')#,clim = (0.60))
        img.set_clim(0,60)
        #plt.axis('off')
        axs[int(floor(n_plot/6)),n_plot%6].set_yticklabels([])
        axs[int(floor(n_plot/6)),n_plot%6].set_xticklabels([])
        axs[int(floor(n_plot/6)),n_plot%6].set_title('t = ' + str((t_ndx-100)*0.04) + 's' )

    #plt.savefig('fig2.eps')

        #plt.colorbar()



    plt.show()

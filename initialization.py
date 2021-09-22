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

    if state == 'HAS':
        I0 = I_up
        b_0 = b_up
        bamp = 0.

    if state == 'LAS':
        I0 = I_down
        b_0 = b_down
        bamp = 0.

    if state == 'Slow Waves':
        I0 = I_so
        b_0 = b_so
        bamp = 0.

    if state == 'Spiral Waves':
        I0 = I_sp
        b_0 = b_sp
        bamp = 0.


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
    plt.ylabel('f.r. (Hz)')
    #plt.legend('123')

    plt.subplot(223)
    plt.imshow(nuE.T, aspect='auto',cmap= 'hot')
    plt.clim(0,60)
    plt.xlabel('time (s)')
    plt.ylabel('f.r. (Hz)')

    plt.subplot(122)
    plt.plot(I0,  b_0,'o',linewidth=2, markersize=12)

    plt.plot([I0, I0], [ b_0-b_amp, b_0+b_amp ],'r-')

    plt.xlim([0.6,1.5])
    plt.ylim([0.1,2])
    plt.xlabel('$I_0$')
    plt.ylabel('$b_0$')


    plt.plot( I_down,b_down,'rx',linewidth=2, markersize=5)
    plt.annotate('LAS', (I_down,b_down))


    plt.plot( I_up,b_up,'rx',linewidth=2, markersize=5)
    plt.annotate('HAS', (I_up,b_up))


    plt.plot( I_so,b_so,'rx',linewidth=2, markersize=5)
    plt.annotate('Slow Waves', (I_so,b_so))


    plt.plot( I_sp,b_sp,'rx',linewidth=2, markersize=5)
    plt.annotate('Spiral waves', (I_sp,b_sp))

    fig, axs = plt.subplots(2,6,figsize=(16, 5))

    for n_plot in range(12):
        t_ndx = n_plot*2+100
        Grid = np.zeros((50,50),dtype=float)+60
        for k in range(N-1):
            Grid[xPos[0,k]-1,yPos[0,k]-1] = nuE[t_ndx,k]
        img = axs[int(floor(n_plot/6)),n_plot%6].imshow(Grid.T,cmap='hot')#,clim = (0.60))
        img.set_clim(0,60)
        #plt.colorbar()

    plt.show()

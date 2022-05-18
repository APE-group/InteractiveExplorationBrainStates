import ipywidgets as widgets
import scipy.io as sio
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

class interactive_GUI:
    def __init__(self):
        
        # load simulation + inferred parameters
        self.TFE = sio.loadmat('TFpy.mat')
        self.TF = np.array(self.TFE['TFE']).ravel()
        self.mu = np.array(self.TFE['mu']).ravel()
        self.z = np.polyfit(self.mu, self.TF, 20)
        self.p = np.poly1d(self.z)
        self.dt = 0.04 #(s)
        self.tauW = 0.1 #(s)
        self.TIME = 600
        self.InferredParameters = sio.loadmat('InferredParameters_py.mat')
        self.K = np.transpose( np.array(self.InferredParameters['kLat']) )
        self.b = np.array(self.InferredParameters['bs'])
        self.Iext = np.transpose(np.array(self.InferredParameters['ExcDrive']))*.95
        self.xPos = np.array(self.InferredParameters['x_pos_sel'])
        self.yPos = np.array(self.InferredParameters['y_pos_sel'])
        self.N = np.shape(self.Iext)[1]
        self.times = np.arange(self.TIME)*self.dt
        
        # defined parameters for predefined states [order: I0, b_0, bamp]
        self.states = {'HAS': [1.4, 0.5, 0.], 
                      'LAS': [0.7, 1.7, 0.],
                      'Planar Slow Waves': [1.0, 0.9, 0.],
                      'Spiral Slow Waves': [0.9, 1.05, 0.],
                      'Long Up State': [1.27, 0.77, 0.],
                      'High Frequency Waves': [1.4, 1.9, 0.],
                      'Waves Doublets': [1., 1.29, 0.31],
                      'Waves MA': [1.41, .91, 0.39],                       
                      }
        
        # define widgets
        self.widgets = {}
        self.widgets['out'] = widgets.Output()
        self.widgets['I0'] = widgets.FloatSlider(min=.6, max=1.5, step=.01, value=1., description= 'I factor', continuous_update=False)
        self.widgets['b_0'] = widgets.FloatSlider(min=0.1, max=2., step=.01, value=1., description= 'b factor', continuous_update=False)
        self.widgets['b_amp'] =widgets.FloatSlider(min=0, max=1., step=.01, value=0, description= 'b amplitude', continuous_update=False)
        self.widgets['state'] = widgets.Dropdown(value='selected from slider', 
                                                 options=['selected from slider',
                                                          'Planar Slow Waves',
                                                          'Spiral Slow Waves',
                                                          'Long Up State',
                                                          'High Frequency Waves',
                                                          'HAS',
                                                          'LAS',
                                                          'Waves MA',
                                                          'Waves Doublets'])
        self.widgets['label'] = widgets.Label(value='Choose pre-defined state:')
        self.widgets['stimulation'] = widgets.Dropdown(value='Stim OFF',
                                                 options=['Stim OFF',
                                                          'Stim ON'])
        
        self.widgets['btn_execute'] = widgets.Button(description='Run')
        
        # GUI display
        display(
            widgets.HBox(
                [widgets.VBox([self.widgets['I0'], 
                             self.widgets['b_0'], 
                             self.widgets['b_amp']]),
                 widgets.VBox([self.widgets['label'], 
                               self.widgets['state'], 
                               self.widgets['stimulation'],
                               self.widgets['btn_execute']])
                             ]))
        display(self.widgets['out'])
        
        # action --> execute the run_simulation_and_plot function when the Run button is clicked.
        self.widgets['btn_execute'].on_click(self.run_simulation_and_plot)
        
        
        # action 2 --> if any of the sliders is changed, the state selected goes back to "selected from slider"
        
        self.widgets['I0'].observe(self.default_state)
        self.widgets['b_0'].observe(self.default_state)
        self.widgets['b_amp'].observe(self.default_state)
        
        
        # first execution (when the GUI is loaded, a first execution is made without the need of pressing Run and with the default values)
        #self.run_simulation_and_plot(self)
        
    def default_state(self, x):
        self.widgets['state'].value = "selected from slider"
                
    def trasfFunc(self, p, mu):
        mu = np.maximum(mu,-2000)
        pp = p(mu)
        pp = np.minimum(pp,140)
        pp = np.maximum(pp,0)
        return pp
    
    def run_simulation_and_plot(self, x):
        # set parameters and check if predefined state is selected
        state = self.widgets['state'].value 
        stimulation = self.widgets['stimulation'].value 
        if state == 'selected from slider':
            self.params = {'I0': self.widgets['I0'].value, 'b_0': self.widgets['b_0'].value, 'b_amp': self.widgets['b_amp'].value}
        else: 
            self.params = {'I0': self.states[state][0], 'b_0': self.states[state][1], 'b_amp': self.states[state][2]}
            self.widgets['I0'].value = self.params['I0']
            self.widgets['b_0'].value = self.params['b_0']
            self.widgets['b_amp'].value = self.params['b_amp']
            
        # avoid going back to selected from slider value in the state widget
        self.widgets['state'].value = state
            
        I_stim = 0
        
        stimulation_amplitude = 0
        stimulus_duration = 3
        stimulus_site = 1065

            
        if stimulation == 'Stim ON':
            
        
            stimulation_amplitude = 100000
        
        # run simulation 
        nuE = np.zeros((self.TIME, self.N), dtype=float)
        muE = np.zeros((self.TIME, self.N), dtype=float)
        W = np.zeros((self.TIME, self.N), dtype=float)
        for t in range(self.TIME-1):
            
            if t == 100:
                self.Iext[0,stimulus_site] = self.Iext[0,stimulus_site] + stimulation_amplitude
            
            if t == 100+stimulus_duration:
                self.Iext[0,stimulus_site] = self.Iext[0,stimulus_site] - stimulation_amplitude
        
            b_osc = self.params['b_amp']*np.cos(t*.07)
            W[t+1,:] = W[t,:] + self.dt*( -W[t,:]/self.tauW + nuE[t,:] )
            muE[t,:] = np.matmul(nuE[t,:],self.K)  + self.Iext*self.params['I0'] - W[t,:]*(self.params['b_0']+b_osc)*(self.b)
            self.TFE = self.trasfFunc(self.p, muE[t,:])  #
            nuE[t+1,:] = np.maximum(self.TFE + np.random.randn(1,self.N)*1,0)
        
        # plot
        ndx1 = int(np.floor(self.N/10))
        ndx2 = int(np.floor(self.N/5))
        ndx3 = int(np.floor(self.N/2))
        
        # VISUALIZATION
        with self.widgets['out']:
            # clear last figure before new execution
            self.widgets['out'].clear_output()

            # figure 
            fig = plt.figure(figsize=(10, 6), constrained_layout=True)
            Grid = gridspec.GridSpec(ncols=6, nrows=4, figure=fig)
            ax_fr = fig.add_subplot(Grid[0, :3])
            ax_pop = fig.add_subplot(Grid[1, :3])
            ax_map = fig.add_subplot(Grid[:2, 3:])
            axs_im = [fig.add_subplot(Grid[i, j]) for i in range(2,4) for j in range(0, 6)]
            
            # fr plot
            ax_fr.plot(self.times, nuE[:,ndx1])
            ax_fr.plot(self.times, nuE[:,ndx2])
            ax_fr.plot(self.times, nuE[:,ndx3])
            ax_fr.set_ylim([0, 100])
            ax_fr.set_ylabel('f.r. (Hz)', fontsize=15)

            # pop plot
            ax_pop.imshow(nuE.T, aspect='auto',cmap='hot', extent=[0,25, 0, self.N], vmin=0, vmax=60)
            ax_pop.set_xlabel('time (s)', fontsize=15)
            ax_pop.set_ylabel('population id.', fontsize=15)

            # map plot
            ax_map.plot(self.params['I0'], self.params['b_0'], 'o', linewidth=2, markersize=12)
            ax_map.plot([self.params['I0'], self.params['I0']], [self.params['b_0']-self.params['b_amp'], self.params['b_0']+self.params['b_amp'] ],'r-')
            ax_map.set_xlim([0.6,1.5])
            ax_map.set_ylim([0.1,2])
            ax_map.set_xlabel('$I_{factor}$', fontsize=15)
            ax_map.set_ylabel('$b_{factor}$', fontsize=15)
            for state in self.states.keys():
                ax_map.plot(self.states[state][0], self.states[state][1], 'rx', linewidth=2, markersize=5)
                ax_map.annotate(state, (self.states[state][0], self.states[state][1]), fontweight='bold')

            # brain images plot
            for n_plot in range(12):
                t_ndx = n_plot*2+100
                grid = np.zeros((50,50),dtype=float)+60
                for k in range(self.N-1):
                    grid[self.xPos[0, k]-1, self.yPos[0, k]-1] = nuE[t_ndx, k]
                img = axs_im[n_plot].imshow(grid.T,cmap='hot')#,clim = (0.60))
                img.set_clim(0,60)
                axs_im[n_plot].set_yticklabels([])
                axs_im[n_plot].set_yticks([])
                axs_im[n_plot].set_xticklabels([])
                axs_im[n_plot].set_xticks([])
                axs_im[n_plot].set_title('t = '+ str(self.times[n_plot*2]) + ' s') 
                
            plt.show()
                
            # plt.show() must be included, otherwise the figure is displayed in the terminal.  
            #plt.show()
            #print('hello')
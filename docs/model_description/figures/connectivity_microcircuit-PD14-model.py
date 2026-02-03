#!/usr/bin/env python3
## -*- coding: utf-8 -*-
##
## This file is part of https://github.com/INM-6/microcircuit-PD14-model
##
## SPDX-License-Identifier: CC-BY-NC-SA-4.0
##

"""
Created on Tue Oct 31 12:01:38 2023

@author: peraza
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

#Write down connectivity matrix

W = np.array([[0.101,0.169,0.044,0.083,0.032,0.0,0.008,0.0],
              [0.135,0.137,0.032,0.052,0.075,0.0,0.004,0.0],
              [0.008,0.006,0.050,0.135,0.007,0.0003,0.045,0.0],
              [0.069,0.003,0.079,0.160,0.003,0.0,0.106,0.0],
              [0.100,0.062,0.051,0.006,0.083,0.373,0.020,0.0],
              [0.055,0.027,0.026,0.002,0.060,0.316,0.009,0.0],
              [0.016,0.007,0.021,0.017,0.057,0.020,0.040,0.225],
              [0.036,0.001,0.003,0.001,0.028,0.008,0.066,0.144]],dtype=float)

print(W)

mpl.rcParams['font.size'] = 8
mpl.rcParams['text.usetex'] = True
mpl.rcParams['xtick.top'] = True
mpl.rcParams['xtick.bottom'] = False
mpl.rcParams['xtick.labeltop'] = True
mpl.rcParams['xtick.labelbottom'] = False
plt.figure(1,dpi=300,figsize=(2,1.7))
plt.imshow(W, cmap='cividis')
cb = plt.colorbar(fraction=0.045)
cb.set_label(r'$C_{yx}$',fontsize=10)
cb.set_ticks([])
plt.title(r'$x$')
plt.xticks([0,1,2,3,4,5,6,7],[r'$\mathcal{E}_{23}$',r'$\mathcal{I}_{23}$',r'$\mathcal{E}_{4}$',r'$\mathcal{I}_{4}$',r'$\mathcal{E}_{5}$',r'$\mathcal{I}_{5}$',r'$\mathcal{E}_{6}$',r'$\mathcal{I}_{6}$'])
plt.ylabel(r'$y$')
plt.yticks([0,1,2,3,4,5,6,7],[r'$\mathcal{E}_{23}$',r'$\mathcal{I}_{23}$',r'$\mathcal{E}_{4}$',r'$\mathcal{I}_{4}$',r'$\mathcal{E}_{5}$',r'$\mathcal{I}_{5}$',r'$\mathcal{E}_{6}$',r'$\mathcal{I}_{6}$'])
ax = plt.gca()
#ax.set_aspect('equal', 'box')
#plt.subplots_adjust(left=0.2, right=0.9, bottom=0.2, top=0.8)
plt.tight_layout(pad=0.5)
plt.savefig('connectivity_microcircuit-PD14-model.svg')
#plt.show()

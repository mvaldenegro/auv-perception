"""Demo of polar plot of arbitrary theta. This is a workaround for MPL's polar plot limitation
to a full 360 deg.

Based on http://matplotlib.org/mpl_toolkits/axes_grid/examples/demo_floating_axes.py
"""

from __future__ import division
from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.transforms import Affine2D
from matplotlib.projections import PolarAxes
from mpl_toolkits.axisartist import angle_helper
from mpl_toolkits.axisartist.grid_finder import MaxNLocator
from mpl_toolkits.axisartist.floating_axes import GridHelperCurveLinear, FloatingSubplot

import numpy as N
import matplotlib.pyplot as P

from matplotlib.projections import PolarAxes, register_projection
from matplotlib.transforms import Affine2D, Bbox, IdentityTransform

class NorthPolarAxes(PolarAxes):
    '''
    A variant of PolarAxes where theta starts pointing north and goes
    clockwise.
    '''
    name = 'northpolar'

    class NorthPolarTransform(PolarAxes.PolarTransform):
        def transform(self, tr):
            xy   = N.zeros(tr.shape, N.float_)
            t    = tr[:, 0:1]
            r    = tr[:, 1:2]
            x    = xy[:, 0:1]
            y    = xy[:, 1:2]
            x[:] = r * N.sin(t)
            y[:] = r * N.cos(t)
            return xy

        transform_non_affine = transform

        def inverted(self):
            return InvertedNorthPolarTransform()

    class InvertedNorthPolarTransform(PolarAxes.InvertedPolarTransform):
        def transform(self, xy):
            x = xy[:, 0:1]
            y = xy[:, 1:]
            r = N.sqrt(x*x + y*y)
            theta = N.arctan2(y, x)
            return N.concatenate((theta, r), 1)

        def inverted(self):
            return NorthPolarTransform()

    def _set_lim_and_transforms(self):
        PolarAxes._set_lim_and_transforms(self)
        self.transProjection = self.NorthPolarTransform()
        self.transData = (
            self.transScale +
            self.transProjection +
            (self.transProjectionAffine + self.transAxes))
        self._xaxis_transform = (
            self.transProjection +
            self.PolarAffine(IdentityTransform(), Bbox.unit()) +
            self.transAxes)
        self._xaxis_text1_transform = (
            self._theta_label1_position +
            self._xaxis_transform)
        self._yaxis_transform = (
            Affine2D().scale(N.pi * 2.0, 1.0) +
            self.transData)
        self._yaxis_text1_transform = (
            self._r_label1_position +
            Affine2D().scale(1.0 / 360.0, 1.0) +
            self._yaxis_transform)

register_projection(NorthPolarAxes)

def fractional_polar_axes(f, thlim=(0, 180), rlim=(0, 1), step=(30, 0.2),
                          thlabel='theta', rlabel='r', ticklabels=False):
    """Return polar axes that adhere to desired theta (in deg) and r limits. steps for theta
    and r are really just hints for the locators."""
    th0, th1 = thlim # deg
    r0, r1 = rlim
    thstep, rstep = step

    # scale degrees to radians:
    tr_scale = Affine2D().scale(np.pi/180., 1.)
    tr = tr_scale + NorthPolarAxes.NorthPolarTransform()
    theta_grid_locator = angle_helper.LocatorDMS((th1-th0)//thstep)
    r_grid_locator = MaxNLocator((r1-r0)//rstep)
    theta_tick_formatter = angle_helper.FormatterDMS()
    grid_helper = GridHelperCurveLinear(tr,
                                        extremes=(th0, th1, r0, r1),
                                        grid_locator1=theta_grid_locator,
                                        grid_locator2=r_grid_locator,
                                        tick_formatter1=theta_tick_formatter,
                                        tick_formatter2=None)

    a = FloatingSubplot(f, 111, grid_helper=grid_helper)
    f.add_subplot(a)

    # adjust x axis (theta):
    a.axis["bottom"].set_visible(False)
    a.axis["top"].set_axis_direction("bottom") # tick direction
    a.axis["top"].toggle(ticklabels=ticklabels, label=bool(thlabel))
    a.axis["top"].major_ticklabels.set_axis_direction("top")
    a.axis["top"].label.set_axis_direction("top")

    # adjust y axis (r):
    a.axis["left"].set_axis_direction("bottom") # tick direction
    a.axis["right"].set_axis_direction("top") # tick direction
    a.axis["left"].toggle(ticklabels=ticklabels, label=bool(rlabel))

    # add labels:
    #a.axis["top"].label.set_text(thlabel)
    #a.axis["left"].label.set_text(rlabel)

    #Remove axes, its a sonar image :)
    a.axis["top"].set_visible(False)
    a.axis["left"].set_visible(False)
    a.axis["right"].set_visible(False)

    # create a parasite axes whose transData is theta, r:
    auxa = a.get_aux_axes(tr)
    # make aux_ax to have a clip path as in a?:
    auxa.patch = a.patch
    # this has a side effect that the patch is drawn twice, and possibly over some other
    # artists. So, we decrease the zorder a bit to prevent this:
    a.patch.zorder = -2

    # add sector lines for both dimensions:
    thticks = grid_helper.grid_info['lon_info'][0]
    rticks = grid_helper.grid_info['lat_info'][0]
    #for th in thticks[1:-1]: # all but the first and last
    #    auxa.plot([th, th], [r0, r1], '--', c='grey', zorder=-1)
    #for ri, r in enumerate(rticks):
        # plot first r line as axes border in solid black only if it isn't at r=0
        #if ri == 0 and r != 0:
        #    ls, lw, color = 'solid', 0.01, 'black'
        #else:
        #    ls, lw, color = 'dashed', 0.01, 'grey'
        # From http://stackoverflow.com/a/19828753/2020363
        #auxa.add_artist(plt.Circle([0, 0], radius=r, ls=ls, lw=lw, color=color, fill=False,
        #                transform=auxa.transData._b, zorder=-1))

    auxa.set_axis_off()
    auxa.axis("tight")
    auxa.axis("image")
    auxa.get_xaxis().set_visible(False)
    auxa.get_yaxis().set_visible(False)
    return auxa


if __name__ == '__main__':
    f1 = plt.figure()
    a1 = fractional_polar_axes(f1)
    # example spiral plot:
    thstep = 10
    th = np.arange(0, 180+thstep, thstep) # deg
    rstep = 1/(len(th)-1)
    r = np.arange(0, 1+rstep, rstep)
    a1.plot(th, r, 'b')
    f1.show()

    f2 = plt.figure()
    a2 = fractional_polar_axes(f2, thlim=(36, 135), rlim=(2,7), step=(15, 1))
    # example spiral plot:
    thstep = 10
    th = np.arange(36, 135+thstep, thstep) # deg
    rstep = (7-2)/(len(th)-1)
    r = np.arange(2, 7+rstep, rstep)
    a2.plot(th, r, 'r')
    f2.show()

    f3 = plt.figure()
    a3 = fractional_polar_axes(f3, thlim=(36, 135), rlim=(2,7), step=(15, 1),
                               thlabel=None, rlabel=None, ticklabels=False)
    # example spiral plot:
    thstep = 10
    th = np.arange(36, 135+thstep, thstep) # deg
    rstep = (7-2)/(len(th)-1)
    r = np.arange(2, 7+rstep, rstep)
    a3.plot(th, r, 'r')
    f3.show()

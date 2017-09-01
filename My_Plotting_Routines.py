# common conversion point stacking

# import modules
import sys
from geographiclib.geodesic import Geodesic as geo
import numpy as np
# from matplotlib.mlab import griddata
import scipy
import scipy.ndimage
from scipy import interpolate
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import os
import os.path
import math
import msgpack
import msgpack_numpy as m
m.patch()
import shutil
from matplotlib.colors import LogNorm
import matplotlib.cm as cm
from obspy import read
from scipy import stats

import mpl_toolkits
root = '/raid3/sdat2/Parra/'


# definition of the half width of the fresnel zone
knotspacing = lambda r, vs: 1./2.*np.sqrt(((10./3.*vs)+r)**2.-r**2.) # in m for a 10s wave


def haversine(lat1, long1, lats2, longs2):
    """
    Calculate the distance between two points on earth in m
    """
    d = []

    for i in range(len(lats2)):
        lat2 = lats2[i]
        long2 = longs2[i]
        earth_radius = 6371.e3  # m
        dLat = math.radians(lat2 - lat1)
        dLong = math.radians(long2 - long1)

        a = (math.sin(dLat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLong / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d.append(earth_radius * c)
    return float(d[0])


def weight(distance, depth, vs, factor):
    '''
    Calculates the weight based on the distance and the fresnel zone width for a given depth
    '''
    delta = distance/(factor*knotspacing(depth*1.e3, vs)) # distance in m ~~~~~~ fresnel zone times factor~~~
    if delta > 2:
        weight = 0
    elif delta > 1:
        weight = .25*(2.-delta)**3.
    else:
        weight = .75*delta**3.-1.5*delta**2.+1.

    return weight

class VOL(dict):
    def __init__(self, *arg, **kw):
        super(VOL, self).__init__(*arg, **kw)
        self.__dict__ = self
    def __getattr__(self, name):
        return self[name]

class ccp_volume(object):
    """
       Handling large stacked volumes
    """
    def __init__(self, *arg, **kw):
        self.VOL = VOL(*arg, **kw)


#
# Load latest volume to dictionary
#
    def load_latest(self, name='Megavolume', filter='rff2', conversion='EU60', factor=1.):
        line = open(root+'CCP_Stack/Volumes/'+name+'_'+filter+'_'+conversion+'_'+str(factor)+'/filenames.dat', 'r').readlines()[-1]
        runnum = int(float(line.split()[0]))
        volumefile = line.split()[1]
        print('loading', name, runnum, volumefile)



        # get last stackfile name

        # Read in volumes

        self.VOL.update(msgpack.unpack(open(volumefile, 'rb'), use_list=False, object_hook=m.decode))
        # del self.VOL['trackRFs']


        return self


#
# Plot crossections
#

    def plot_crosssection(self, direction, lonorlat, amplify=1., name='Megavolume', filter='rff2', conversion='EU60', factor=2., zoom=False, mincoverage=10):
        # set volume lats and lons

        if direction == 'NS':
            lon = lonorlat
            n = np.argmin(np.abs(self.VOL.grid_lon-lon))
            crossec = self.VOL.volume[n,:,:].T.copy()
            vol_sig = self.VOL.volumesigma[n,:,:].T.copy()
            w = self.VOL.volumeweight[n,:,:].T

            xaxis = self.VOL.grid_lat
            xlabel = 'latitude (dg)'
            xends = [lon, lon]
            yends = [self.VOL.latmin, self.VOL.latmax]

        if direction == 'EW':
            lat = lonorlat
            n = np.argmin(np.abs(self.VOL.grid_lat-lat))
            crossec = self.VOL.volume[:, n,:].T.copy()
            vol_sig = self.VOL.volumesigma[:, n,:].T.copy()
            w = self.VOL.volumeweight[:, n,:].T
            xaxis = self.VOL.grid_lon
            xlabel = 'longitude (dg)'
            xends = [self.VOL.lonmin, self.VOL.lonmax]
            yends = [lat, lat]
        depths = self.VOL.grid_depth

        # normalize
        for i in range(np.shape(w)[0]):
            for j in range(np.shape(w)[1]):
                if w[i, j] > mincoverage:

                    crossec[i, j] = crossec[i, j]/w[i, j]
                    if crossec[i, j] > 0:
                        vol_sig[i, j] = crossec[i, j]-1.96*np.sqrt(vol_sig[i, j]/(w[i, j]*w[i, j]))
                        if vol_sig[i, j] < 0:
                            vol_sig[i, j] = 0.
                    if crossec[i, j] < 0:
                        vol_sig[i, j] = crossec[i, j]+1.96*np.sqrt(vol_sig[i, j]/(w[i, j]*w[i, j]))
                        if vol_sig[i, j] > 0:
                            vol_sig[i, j] = 0.

                else:
                    crossec[i, j] = 1000.
     

        plt.figure(figsize=(14, 8))

        plt.subplot(2, 2, 2)
        m = Basemap(projection='merc', llcrnrlat=self.VOL.latmin, urcrnrlat=self.VOL.latmax, llcrnrlon=self.VOL.lonmin, urcrnrlon=self.VOL.lonmax, lat_ts=20, resolution='i')
        m.drawparallels(np.arange(self.VOL.latmin, self.VOL.latmax, 5.), labels=[1, 0, 0, 1], labelstyle='+/-', fontsize=10)
        m.drawmeridians(np.arange(self.VOL.lonmin, self.VOL.lonmax, 5.), labels=[1, 0, 0, 1], labelstyle='+/-', fontsize=10)

        m.drawcoastlines()
        m.drawcountries()
        m.drawstates()

        m.drawmapboundary(fill_color=[1.0, 1.0, 1.0])

        x1, y1 = m(xends[0], yends[0])
        x2, y2 = m(xends[1], yends[1])
        m.plot([x1, x2], [y1, y2], color='r', linewidth=1, zorder=1)
        if direction == 'NS':
            x3, y3 = m(lon*np.ones(len(xaxis),), np.round(xaxis/10.)*10.)
            m.scatter(x3, y3, 80, xaxis, zorder=2)
        if direction == 'EW':
            x3, y3 = m(np.round(xaxis/10.)*10, lat*np.ones(len(xaxis),)  )
            m.scatter(x3, y3, 80, xaxis, zorder=2)



        norm = 0.2/amplify

        # plot

        plt.subplot(2, 2, 1)
        xx, yy = np.meshgrid(xaxis, depths)

        cs = plt.pcolor(xx, yy, crossec, vmin=-0.15, vmax=0.15, rasterized=True,cmap=cm.coolwarm)
        plt.colorbar()
        cs.cmap.set_over([0.8, 0.8, 0.8])
        if zoom:
            plt.ylim([300, 800])
        else:
            plt.ylim([min(depths), max(depths)])
        plt.gca().invert_yaxis()
        plt.xlim(xends)
        plt.subplot(2, 1, 2)
        for t in np.arange(0, len(xaxis), 1):

            lx = [x for x in range(100, len(depths)) if (np.abs(w[x, t]) > mincoverage)]# and np.abs(vol_sig[x,t])>std[x,t]/1.96)]
            RF = vol_sig[lx, t]/norm+xaxis[t]
            RFfull = crossec[lx, t]/norm+xaxis[t]

            plt.fill_betweenx(depths[lx], RFfull, xaxis[t], where=RFfull >= xaxis[t], facecolor='k', rasterized=True)
            plt.fill_betweenx(depths[lx], RFfull, xaxis[t], where=xaxis[t] >= RFfull, facecolor='k', rasterized=True)
            plt.fill_betweenx(depths[lx], RF, xaxis[t], where=RF >= xaxis[t], facecolor=[1.0, 0., 0.], rasterized=True)
            plt.fill_betweenx(depths[lx], RF, xaxis[t], where=xaxis[t] >= RF, facecolor=[0.0, 0.0, 1.], rasterized=True)
        plt.scatter(np.round(xaxis/10.)*10., 80.*np.ones(len(xaxis),), 80, xaxis, rasterized=True)
        plt.plot([-15, 140], [410, 410], '--k', linewidth=2)
        plt.plot([-15, 140], [660, 660], '--k', linewidth=2)
        plt.ylabel('Depth (km)')
        plt.xlabel(xlabel, fontsize=12)
        plt.xlim([min(xaxis), max(xaxis)])

        if zoom:
            plt.ylim([300, 800])
        else:
            plt.ylim([min(depths), max(depths)])
        plt.gca().invert_yaxis()


#
# Plot crossections
#

    def plot_crosssection_any(self, lon1,lon2,lat1,lat2,numpoints=200,amplify=1.,name='Megavolume',filter='rff2', conversion='EU60', factor=2.,zoom=False,mincoverage=10., color_scheme = 'spectral', reverse = False,degree_limit=10):
        # set volume lats and lons

        inv = geo.WGS84.Inverse(lat1, lon1, lat2, lon2)
        points = np.linspace(0, inv['s12'], numpoints)
        line = geo.WGS84.Line(lat1, lon1, inv['azi1'])

        lats = []
        lons = []
        for i in range(len(points)):
            lats.append(line.Position(points[i])['lat2'])
            lons.append(line.Position(points[i])['lon2'])

        lats = np.array(lats)
        lons = np.array(lons)

        crossec = []
        vol_sig = []
        w = []
 
        dist = []
        for i in range(len(lats)):
            dist.append(haversine(lats[0], lons[0], [lats[i]], [lons[i]])/111194.)

        # pixelize lon and lat
        row = (lons-np.min(self.VOL.grid_lon))/(self.VOL.grid_lon[1]-self.VOL.grid_lon[0])
        for i in range(len(row)):
            if row[i] < 0:
                row[i] = row[i]+len(self.lon)
        col = (lats-np.min(self.VOL.grid_lat))/(self.VOL.grid_lat[1]-self.VOL.grid_lat[0])

        for dp in range(len(self.VOL.grid_depth)):
            crossec.append(scipy.ndimage.map_coordinates(self.VOL.volume[:,:, dp], np.vstack((row, col))))
            vol_sig.append(scipy.ndimage.map_coordinates(self.VOL.volumesigma[:,:, dp], np.vstack((row, col))))
            w.append(scipy.ndimage.map_coordinates(self.VOL.volumeweight[:,:, dp], np.vstack((row, col))))


        crossec = np.array(crossec)
        vol_sig = np.array(vol_sig)
        w = np.array(w)

        xaxis = self.VOL.grid_lat
        xlabel = 'latitude (dg)'
        xends = [lon1, lon2]
        yends = [lat1, lat2]

        depths = self.VOL.grid_depth

        # normalize
        for i in range(np.shape(w)[0]):
            for j in range(np.shape(w)[1]):
                if w[i, j] > mincoverage:

                    crossec[i, j] = crossec[i, j]/w[i, j]
                    if crossec[i, j] > 0:
                        vol_sig[i, j] = crossec[i, j]-1.96*np.sqrt(vol_sig[i, j]/(w[i, j]*w[i, j]))
                        if vol_sig[i, j] < 0:
                            vol_sig[i, j] = 0.
                    if crossec[i, j] < 0:
                        vol_sig[i, j] = crossec[i, j]+1.96*np.sqrt(vol_sig[i, j]/(w[i, j]*w[i, j]))
                        if vol_sig[i, j] > 0:
                            vol_sig[i, j] = 0.

   
                else:
                    crossec[i, j] = 100.
                   

        plt.subplot(2, 2, 2)
        m = Basemap(projection='merc', llcrnrlat=self.VOL.latmin, urcrnrlat=self.VOL.latmax, llcrnrlon=self.VOL.lonmin, urcrnrlon=self.VOL.lonmax, lat_ts=20, resolution='i')
        m.drawparallels(np.arange(0, 70, 5.), labels=[1, 0, 0, 1], labelstyle='+/-', fontsize=10)
        #lon1,lon2,lat1,lat2
        m.drawparallels([lat1,lat2],labels=[0, 1, 1, 0], labelstyle='+/-', fontsize=10)
        m.drawmeridians([lon1,lon2],labels=[0, 1, 1, 0], labelstyle='+/-', fontsize=10)
        m.drawmeridians(np.arange(-130,100, 5.), labels=[1, 0, 0, 1], labelstyle='+/-', fontsize=10)
        m.drawstates()
        m.drawcoastlines()
        m.drawcountries()

        m.drawmapboundary(fill_color=[1.0, 1.0, 1.0])
        x1, y1 = m(xends[0], yends[0])
        x2, y2 = m(xends[1], yends[1])
        m.plot([x1, x2], [y1, y2], color='r', linewidth=1, zorder=1)
        

######################################################
        plt.subplot(2, 2, 1)
        xx, yy = np.meshgrid(dist, depths)
        #----------------------------------------------------
        if color_scheme == 'rainbow' and reverse == True: cmap = cm.rainbow_r
        if color_scheme == 'rainbow' and reverse == False: cmap = cm.rainbow
        if color_scheme == 'spectral' and reverse == True: cmap = cm.Spectral_r
        if color_scheme == 'spectral' and reverse == False: cmap = cm.Spectral
        cs = plt.pcolor(xx, yy, crossec, vmin=-0.1, vmax=0.1, rasterized=True,cmap=cmap)
        #----------------------------------------------------
        plt.colorbar()
        cs.cmap.set_over([0.8, 0.8, 0.8])
        if zoom:
            plt.ylim([300, 800])
            plt.xlim([0, degree_limit])#((lat2-lat1)**2+(lon2-lon1)**2)**0.5])
        else:
            plt.ylim([min(depths), max(depths)])
            plt.xlim([0, degree_limit])
        plt.gca().invert_yaxis()
  


        # corrected by 3D model
        # normalize

        norm = 0.2/amplify#np.max(np.max(np.abs(crossec_3D)))/amplify

        # plot
        plt.subplot(2,1,2)
        for t in np.arange(0, len(dist), 1):

            lx = [x for x in range(len(depths)) if (np.abs(w[x, t]) > mincoverage)]# and np.abs(vol_sig[x,t])>std[x,t]/1.96)]
            RF = vol_sig[lx, t]/norm+dist[t]
            RFfull = crossec[lx, t]/norm+dist[t]

            plt.fill_betweenx(depths[lx], RFfull, dist[t], where=RFfull >= dist[t], facecolor='k', rasterized=True)
            plt.fill_betweenx(depths[lx], RFfull, dist[t], where=dist[t] >= RFfull, facecolor='k', rasterized=True)
            plt.fill_betweenx(depths[lx], RF, dist[t], where=RF >= dist[t], facecolor=[1.0, 0., 0.], rasterized=True)
            plt.fill_betweenx(depths[lx], RF, dist[t], where=dist[t] >= RF, facecolor=[0.0, 0.0, 1.], rasterized=True)
            RF2 = crossec[lx, t]/norm
            l410 = [x for x in range(len(depths[lx])) if depths[lx[x]] > 366 and depths[lx[x]] < 454]
            l660 = [x for x in range(len(depths[lx])) if depths[lx[x]] > 616 and depths[lx[x]] < 704]
            if len(l410) > 20:
                max410 = np.argmax(RF2[l410])
                ind = lx[l410[max410]]
                plt.plot([dist[t]+0.1, 0.5*RF2[l410[max410]]+dist[t]], [depths[ind], depths[ind]], 'y', linewidth=2)
            if len(l660) > 20:
                max660 = np.argmax(RF2[l660])
                ind = lx[l660[max660]]
                plt.plot([dist[t]+0.1, 0.5*RF2[l660[max660]]+dist[t]], [depths[ind], depths[ind]], 'y', linewidth=2)

        plt.ylabel('Depth (km)')
        plt.xlabel('Distance (dg)', fontsize=12)
        plt.xlim([min(dist), max(dist)])
        plt.plot([-5, 40], [410, 410], '--k', linewidth=2)
        plt.plot([-5, 40], [660, 660], '--k', linewidth=2)
        if zoom:
            plt.ylim([300, 800])
            plt.xlim([0, degree_limit])#((lat2-lat1)**2+(lon2-lon1)**2)**0.5])
        else:
            plt.ylim([min(depths), max(depths)])
            plt.xlim([0, degree_limit])
        plt.gca().invert_yaxis()



#
# Plot data coverage map at predefined depth
#

    def plot_datacoverage(self,depth,name='Megavolume',filter='rff2', conversion='EU60', factor=2.):
 
        fig = plt.figure(figsize=(6,6))
        d = np.argmin(np.abs(self.VOL.grid_depth-depth))
        slice = self.VOL.volumeweight[:,:, d].copy()


        xx, yy = np.meshgrid(self.VOL.grid_lon, self.VOL.grid_lat)

        m = Basemap(projection='merc', llcrnrlat=np.min(self.VOL.grid_lat), urcrnrlat=np.max(self.VOL.grid_lat), llcrnrlon=np.min(self.VOL.grid_lon), urcrnrlon=np.max(self.VOL.grid_lon), lat_ts=20, resolution='i')
        m.drawparallels(np.arange(self.VOL.latmin, self.VOL.latmax, 2.), labels=[1, 0, 0, 1], linewidth=0.5, dashes=[4, 2], labelstyle='+/-', fontsize=10)
        m.drawmeridians(np.arange(self.VOL.lonmin, self.VOL.lonmax, 2.), labels=[1, 0, 0, 1], linewidth=0.5, dashes=[4, 2], labelstyle='+/-', fontsize=10)
        m.drawcountries()
        coasts = m.drawcoastlines(zorder=2, color='k', linewidth=1)

        m.drawmapboundary(fill_color=[1.0, 1.0, 1.0])

        x, y = m(xx, yy)

        contours = [1., 15, 1.e2, 1.e3, 1.e4]#[1.e0,1.e1,1.e2,1.e3,1.e4]
        im =plt.contourf(x, y, slice.T, contours, norm=LogNorm(),zorder=1)
   

        fig.subplots_adjust(bottom=.2)
        cbar_ax = fig.add_axes([0.2, 0.1, 0.6, 0.05])
        cb = fig.colorbar(im, cax=cbar_ax, orientation='horizontal')
        cb.set_label('Sum of weights at ' + str(depth) + ' km')
    


#
# Plot topography maps
#

    def plot_topography(self,mindepth,maxdepth,name='Megavolume',filter='rff2',conversion='prem',factor=2.,mincoverage=15., amplitude = False, color_scheme = 'spectral', reverse = False):
        # Plots topography of maximum between mindepth and maxdepth, masking if sum of weights is beneath mincoverage.
        # If amplitude =True, it will plot the amplitude and not the depth
        
        plt.figure(figsize=(10, 8))
        depths = self.VOL.grid_depth
        val_list = [x for x in range(len(depths)) if depths[x] > mindepth and depths[x] < maxdepth]


        thickness = np.empty((len(self.VOL.grid_lon), len(self.VOL.grid_lat)))
        dmap = np.empty((len(self.VOL.grid_lon), len(self.VOL.grid_lat)))
        coverage = np.empty((len(self.VOL.grid_lon), len(self.VOL.grid_lat)))


        for i in range(len(self.VOL.grid_lon)):
            for j in range(len(self.VOL.grid_lat)):

                RF = self.VOL.volume[i, j,:]/self.VOL.volumeweight[i, j,:]
                std = 1.96*np.sqrt(self.VOL.volumesigma[i, j,:]/(self.VOL.volumeweight[i, j,:]*self.VOL.volumeweight[i, j,:]))
                maxmap = np.argmax(RF[val_list])

                if amplitude == False:
                    dmap[i, j] = depths[val_list[maxmap]]
                else:
                    dmap[i,j] = RF[val_list[maxmap]]

                if self.VOL.volumeweight[i, j, val_list[maxmap]] < mincoverage:
                    dmap[i, j] = 1000.
        # Prepare map
        m = Basemap(projection='merc', llcrnrlat=np.min(self.VOL.grid_lat)-0, urcrnrlat=np.max(self.VOL.grid_lat)+0, llcrnrlon=np.min(self.VOL.grid_lon)-0, urcrnrlon=np.max(self.VOL.grid_lon)+0, lat_ts=10, resolution='i')
        m.drawparallels(np.arange(0, 70, 10.), labels=[1, 0, 0, 1], linewidth=0.5, dashes=[4, 2], labelstyle='+/-', fontsize=8)#[1,0,0,1])
        m.drawmeridians(np.arange(-20, 60, 10.), labels=[1, 0, 0, 1], linewidth=0.5, dashes=[4, 2], labelstyle='+/-', fontsize=8)#[1,0,0,1])
        m.drawcountries()
        m.drawstates()
        m.drawcoastlines()
        coasts = m.drawcoastlines(zorder=1, color='k', linewidth=0.1)
        xx, yy = np.meshgrid(self.VOL.grid_lon, self.VOL.grid_lat)
        x, y = m(xx, yy)
        #-----------------------------------------------------------------------
        if color_scheme == 'rainbow' and reverse == True: cmap = cm.rainbow_r
        if color_scheme == 'rainbow' and reverse == False: cmap = cm.rainbow
        if color_scheme == 'spectral' and reverse == True: cmap = cm.Spectral_r
        if color_scheme == 'spectral' and reverse == False: cmap = cm.Spectral
        #------------------------------------------------------------------------
        if amplitude is False:
            cs = plt.pcolor(x, y, dmap.T, vmin=mindepth, vmax=maxdepth, cmap=cmap, linewidth=0, rasterized=False)
        else:
            cs = plt.pcolor(x, y, dmap.T, vmin=0.01, vmax=0.12, cmap=cm.cmap, linewidth=0, rasterized=False)
        cs.cmap.set_under([0.8, 0.8, 0.8])
        cs.cmap.set_over([0.8, 0.8, 0.8])
        cb = plt.colorbar()
        cb.set_label('Maximum map between ' + str(mindepth)+' and ' + str(maxdepth)+' (km)')
        # cb.set_ticks([380,400,420,440])
        cb.solids.set_rasterized(True)
        xt, yt = m(-13.2, 70.6)

        m.drawcoastlines(zorder=1, color='k', linewidth=1)
        dmapall = np.ravel(dmap)
        if amplitude == False:
            l = [l for l in range(len(dmapall)) if dmapall[l] > mindepth+1. and dmapall[l] < maxdepth - 1.]
            print ('median', np.median((dmapall[l])))
            print ('variance', np.var((dmapall[l])))




#
# Plot map of MTZ width
#

    def plot_mtzwidth(self,name='Megavolume',filter='rff2',conversion='prem',factor=2., Max_Thickness = 290, Min_Thickness=230):
        plt.figure(figsize=(18, 8))
        depths = self.VOL.grid_depth
        l410 = [x for x in range(len(depths)) if depths[x] > 370 and depths[x] < 460] # limit between 370 and 460
        l660 = [x for x in range(len(depths)) if depths[x] > 630 and depths[x] < 710] # limit between 630 and 710
        thickness1D = np.empty((len(self.VOL.grid_lon), len(self.VOL.grid_lat))) # create grids the size of the box to plot the data into
        d4101D = np.empty((len(self.VOL.grid_lon), len(self.VOL.grid_lat)))
        d6601D = np.empty((len(self.VOL.grid_lon), len(self.VOL.grid_lat)))
        with open(root+'CCP_Stack/MTZ_'+conversion+'_'+filter+'_'+str(int(factor))+'.txt', 'w') as output:
            for i in range(len(self.VOL.grid_lon)):
                for j in range(len(self.VOL.grid_lat)):
                    RF = self.VOL.volume[i, j,:]/self.VOL.volumeweight[i, j,:]
                    std = 1.96*np.sqrt(self.VOL.volumesigma[i, j,:]/(self.VOL.volumeweight[i, j,:]*self.VOL.volumeweight[i, j,:]))
                    max410 = np.argmax(RF[l410])
                    max660 = np.argmax(RF[l660])
                    # If both picks are significant, store thickness
                    if RF[l410[max410]] > std[l410[max410]] and RF[l660[max660]] > std[l660[max660]]:
                        d4101D[i, j] = depths[l410[max410]]
                        d6601D[i, j] = depths[l660[max660]]
                        thickness1D[i, j] = (depths[l660[max660]]-depths[l410[max410]])
                        output.write(str(depths[l410[max410]])+'\t'+str(depths[l660[max660]])+'\n')
            output.close()
        # Prepare map
        m = Basemap(projection='merc', llcrnrlat=np.min(self.VOL.grid_lat), urcrnrlat=np.max(self.VOL.grid_lat), llcrnrlon=np.min(self.VOL.grid_lon), urcrnrlon=np.max(self.VOL.grid_lon), lat_ts=20, resolution='i')
        m.drawparallels(np.arange(np.min(self.VOL.grid_lat), np.max(self.VOL.grid_lat), 5.), labels=[1,0,0,1])
        m.drawmeridians(np.arange(np.min(self.VOL.grid_lon), np.max(self.VOL.grid_lon), 5.), labels=[1,0,0,1])
        m.drawcoastlines(color='k')
        m.drawcountries(color='k')
        m.drawstates()
        m.drawmapboundary(fill_color=[1.0, 1.0, 1.0])
        xx, yy = np.meshgrid(self.VOL.grid_lon, self.VOL.grid_lat)
        x, y = m(xx, yy)
        cs = plt.contourf(x, y, thickness1D.T, levels=np.linspace(Min_Thickness, Max_Thickness, 81.), cmap=cm.RdYlBu)
        cs.cmap.set_under('w')#Max_Thickness = 290, Min_Thickness=230
        cs.cmap.set_over('w')

        plt.colorbar()
        plt.title('MTZ width')


#
# Plot moveout aligned on 410 or 660
#

    def plot_moveout(self,d660=True,name='Megavolume',filter='rff2',conversion='EU60',factor=2.):
        # ah so the bug is caused by the fact my vertical resolution is 2km not 1km?
    # Picks all profiles in grid and organizes them by 660 depth
        plt.figure(figsize=(8, 8)) # make a square figure
        depths = self.VOL.grid_depth # depths created
        if d660:
            ldisc = [x for x in range(len(depths)) if depths[x] > 630 and depths[x] < 710] ##My 660 does not go above 710
            disc = np.arange(630., 710., 2.) #630 710
            ldisc2 = [x for x in range(len(depths)) if depths[x] > 380 and depths[x] < 430] #380 430 
        else: #will plot 410 instead
            ldisc = [x for x in range(len(depths)) if depths[x] > 380 and depths[x] < 430]#380 430 
            disc = np.arange(380, 430, 2.) #380 430 
        weights = np.empty((len(disc),)) 
        moveout = np.empty((len(disc), len(depths)))
        d660l = [] # an empty list created to store depths of points
        d410l = []
        for i in range(len(self.VOL.grid_lon)):
            for j in range(len(self.VOL.grid_lat)): # iterate through each grid point
                RF = self.VOL.volume[i, j,:] # The vertical depth stack at the grid point
                for k in range(len(depths)): # Look down the vertical
                    if self.VOL.volumeweight[i, j, k] > 0: 
                        RF[k] = RF[k]/self.VOL.volumeweight[i, j, k] # weight out by volumeweight
                        # I think this assumes a depth resolution of 1km
                std = 1.96*np.sqrt(self.VOL.volumesigma[i, j,:]/(self.VOL.volumeweight[i, j,:]*self.VOL.volumeweight[i, j,:])) ### not sure about this line?
                maxdisc = np.argmax(RF[ldisc]) # search for the maximum in the ldisc part - either around the 410 or 660
                if RF[ldisc[maxdisc]] > std[ldisc[maxdisc]]: # 
                    d660l.append(depths[ldisc[maxdisc]]) # search for the maximum
                    n = np.argmin(np.abs(depths[ldisc[maxdisc]]-disc))
                    weights[n] = weights[n]+1.
                    moveout[n,:] = moveout[n,:]+RF
                    maxdisc = np.argmax(RF[ldisc2])
                    d410l.append(depths[ldisc2[maxdisc]])
        d660l = np.array(d660l) # convert the lists to np arrays
        d410l = np.array(d410l)
        d660c = np.arange(630., 710., 2.) #630 710
        d410c = []
        err = []
        for i in range(len(d660c)):
            filt = [d410l[x] for x in range(len(d410l)) if (d660l[x] == d660c[i] and d410l[x] > 360 and d410l[x] < 460)]
            d410c.extend([np.mean(filt)])
            err.extend([np.std(filt)])
        d410c = np.array(d410c) 
        midp = []; discp = []; discp2 = [] #
        for i in range(len(disc)):
            if weights[i] > 0:
                moveout[i,:] = moveout[i,:]/weights[i]
                if d660:
                    max660 = np.argmax(moveout[i, ldisc])
                    discp.append(depths[ldisc[max660]])
                    midp.append(disc[i])
                    l410 = [x for x in range(len(depths)) if depths[x] > 380 and depths[x] < 430]#380 430 
                    max410 = np.argmax(moveout[i, l410])
                    discp2.append(depths[l410[max410]])
                else:
                    max410 = np.argmax(moveout[i, ldisc])
                    discp.append(depths[ldisc[max410]])
                    midp.append(disc[i])
                    l660 = [x for x in range(len(depths)) if depths[x] > 630 and depths[x] < 710]#630 710
                    max660 = np.argmax(moveout[i, l660])
                    discp2.append(depths[l660[max660]])
        ax = plt.subplot2grid((3, 6), (0, 0), colspan=5)
        if d660:
            n, bins, patches = plt.hist(d660l, np.arange(639., 713., 2.), histtype='bar')
            data = zip(bins+1., n) # +1 as the stack resolution is only at even values
            cmbl = plt.cm.get_cmap('bone_r')
            for d, p in zip(n, patches):
                plt.setp(p, 'facecolor', cmbl(d/max(n)*0.6+0.2))
            # f=open('histogram_660.txt','wb')
            # np.savetxt(f,data,delimiter='\t')
        else:
            plt.hist(d660l, np.arange(389, 431, 2.), histtype='bar') # this is for the 440 moveout
        plt.ylabel('# of grid points')
        plt.text(645, 600, 'a.', fontsize=16)
        if d660:
            # plt.xlabel('660 depth (km)')
            plt.xlim([644.9, 691.07])
        else:
            plt.xlabel('410 depth (km)')
            plt.xlim([390, 430])#380 430 
        plt.gca().set_yticks([0, 100, 300, 500, 700])
        plt.gca().set_xticks([650, 660, 670, 680, 690])
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        ax = plt.subplot2grid((3, 6), (1, 0), rowspan=2, colspan=5)
        cs = plt.pcolor(disc-1., depths, moveout.T, vmin=-0.1, vmax=0.1, rasterized=True, cmap=cm.RdYlBu_r)
        plt.plot(midp, discp, '--k', linewidth=2)
        plt.plot(midp, discp2, '--k', linewidth=2)
        plt.ylabel('Depth (km)')
        if d660:
            plt.xlim([644.9, 691.07])#630 710
            plt.xlabel('660 depth (km)')
        else:
            plt.xlim([380, 430])#380 430 
            plt.xlabel('410 depth (km)')
        plt.ylim([350, 750])
        plt.gca().invert_yaxis()
        plt.text(646, 380, 'b.', fontsize=16)
        box = plt.gca().get_position()
        axcb = plt.axes([box.x0*1.05+box.width*1.05, box.y0+0.1, 0.01, box.height-0.2])
        cb = plt.colorbar(cs, cax=axcb, orientation='vertical')
        cb.set_ticks([-0.1, 0., .1])
        cb.set_label('relative amplitude')
        plt.show()

def MTZ_stats():
    '''
A nice script that should allow you to compare the 440 to 660 correlations when using the 1-d and 3-d velocity models - has to be run off each volume that you want to compare, it will place it in a new directory 'CCP_Stack/MTZ_files/'+name+'_'+conversion+'_'+model+'_'+str(int(factor)).txt
    '''
    import sys
    import numpy as np
    import scipy
    from scipy import interpolate
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    import os.path
    import math
    import msgpack
    import shutil
    from matplotlib.colors import LogNorm
    import matplotlib.cm as cm
    from scipy import stats
    import pandas
    from pandas.tools import plotting
    import pickle
    import seaborn as sns
    import mpl_toolkits
    from statsmodels.formula.api import ols

    files =['mtz_1D.txt', 'mtz_3D.txt']

    for i in [0,1]:#range(len(files)):
        file=files[i]
        data=np.loadtxt(file)
        print(data)
        ## pandas!
        mtz=pandas.DataFrame({'d410':data[:,0],'d660':data[:,1]})
        print(mtz.mean())
        #plotting.scatter_matrix(mtz,alpha=0.4,figsize=(6,6),diagonal='kde')
        #sns.pairplot(mtz, vars=['d410','d660'],kind='reg')
        #g = sns.JointGrid('d410','d660',data=mtz)
        #g.plot(sns.regplot, sns.distplot, stats.pearsonr);
        if i==0:
            g = sns.JointGrid(x=mtz.d410,y=mtz.d660,xlim=[370,450],ylim=[630,710], space=0,  ratio=2)
        if i==1:
            g.x=mtz.d410
            g.y=mtz.d660
        if i==0:
            g.plot_joint(sns.kdeplot, shade=True, cmap="PuBu", n_levels=10,alpha=1.0);
        if i==1:
            g.plot_joint(sns.kdeplot, shade=True, cmap="Greens", n_levels=10,alpha=0.8);
        #_ = g.ax_marg_x.hist(mtz["d410"], color="b", alpha=.6,bins=np.arange(370, 450, 10))
        #_ = g.ax_marg_y.hist(mtz["d660"], color="b", alpha=.6,orientation="horizontal",bins=np.arange(630, 710, 10))
        if i==0:
            g.plot_marginals(sns.kdeplot, shade=True,alpha=0.5)
        if i==1:
            g.plot_marginals(sns.kdeplot, shade=True,alpha=0.5)
        if i==1:
            g.annotate(stats.pearsonr, template="{stat} = {val:.2f} (p = {p:.2g})",fontsize=14);
        print(mtz.mean())
        print(mtz.mad())
        print(mtz.median())

    plt.savefig('dist_aftercorrection.pdf')
    plt.show()

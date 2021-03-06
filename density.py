#from lxml import etree
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon
from shapely.prepared import prep
from pysal.esda.mapclassify import Natural_Breaks as nb
from descartes import PolygonPatch
import fiona
from itertools import chain
from pylab import Normalize, concatenate, linspace, matplotlib
import sys

folder = 'data/'
#open shapefile, get some data out of it,in order to set up basemap
shp = fiona.open(folder + 'new_york_city_fire_companies.shp')
bds = shp.bounds
shp.close()

extra = 0.01

ll = (bds[0], bds[1])
ur = (bds[2], bds[3])
coords = list(chain(ll, ur))
w, h = coords[2]-coords[0], coords[3]-coords[1]

#Create a basemapp instance, which we can use to plot our maps on
m = 	Basemap(
	projection='tmerc',
	lon_0 = -74.0,
	lat_0 = 40.16667,
	ellps = 'WGS84',
	llcrnrlon=coords[0] - extra * w,
	llcrnrlat=coords[1] - extra * h,
	urcrnrlon=coords[2] + extra * w,
	urcrnrlat=coords[3] + extra * h,
	lat_ts = 0,
	resolution='i',
	suppress_ticks=True)

m.readshapefile(folder + 'new_york_city_fire_companies','newyork',color='none',zorder=2)


# Convenience functions for working with colour ramps and bars
def colorbar_index(ncolors, cmap, labels=None, **kwargs):
	"""
	This is a convenience function to stop you making off-by-one errors
	Takes a standard colourmap, and discretises it,
	then draws a color bar with correctly aligned labels
	"""
	cmap = cmap_discretize(cmap, ncolors)
	mappable = cm.ScalarMappable(cmap=cmap)
	mappable.set_array([])
	mappable.set_clim(-0.5, ncolors+0.5)
	colorbar = plt.colorbar(mappable, **kwargs)
	colorbar.set_ticks(np.linspace(0, ncolors, ncolors))
	colorbar.set_ticklabels(range(ncolors))
	if labels:
	    colorbar.set_ticklabels(labels)
	return colorbar

def cmap_discretize(cmap, N):
	"""
	Return a discrete colormap from the continuous colormap cmap.

	    cmap: colormap instance, eg. cm.jet. 
	    N: number of colors.

	Example
	    x = resize(arange(100), (5,100))
	    djet = cmap_discretize(cm.jet, 5)
	    imshow(x, cmap=djet)

	"""
	if type(cmap) == str:
	    cmap = get_cmap(cmap)
	colors_i = concatenate((linspace(0, 1., N), (0., 0., 0., 0.)))
	colors_rgba = cmap(colors_i)
	indices = linspace(0, 1., N + 1)
	cdict = {}
	for ki, key in enumerate(('red', 'green', 'blue')):
	    cdict[key] = [(indices[i], colors_rgba[i - 1, ki], colors_rgba[i, ki]) for i in xrange(N + 1)]
	return matplotlib.colors.LinearSegmentedColormap(cmap.name + "_%d" % N, cdict, 1024)
##################################################################
def show_density(genre):
	infile=folder + genre + ' Restaurant.txt'

	#Extract all the data into a dict
	output = dict()
	output['lon']=[]
	output['lat']=[]
	output['rat']=[]

	with open(infile) as f:
		for line in f:
			LineList = line.split('\t')
			output['rat'].append(LineList[2].split()[0])
			output['lat'].append(LineList[6].split(',')[0])
			output['lon'].append(LineList[6].split(',')[1])
		
	#Create a Pandas DataFrame
	df = pd.DataFrame(output)
	#Drop data contains None(Just for practice)
	df = df.dropna()
	df[['rat','lat','lon']] = df[['rat','lat','lon']].astype(float)
 	
	#Create Point objects in map coordinates from dataframe lon and lat values
	map_points = pd.Series([Point(m(mapped_x, mapped_y)) for mapped_x , mapped_y in zip(df['lon'], df['lat'])])

	rstrnt_points = MultiPoint(list(map_points.values))
	#print len(m.newyork[1]),type(m.newyork),m.newyork_info
	df_map = pd.DataFrame({
		'poly':[Polygon(xy) for xy in m.newyork]})
	df_map['area_m'] = df_map['poly'].map(lambda x:x.area)
	df_map['area_km'] = df_map['area_m']/1000000
	#prepared object
	wards_polygon = prep(MultiPolygon(list(df_map['poly'].values)))
	#Calculate points that fall within the New York boundary
	ny_points = filter(wards_polygon.contains,rstrnt_points)
	
	#########Creating a Choropleth Map, Normalised by Ward Area
	df_map['count'] = df_map['poly'].map(lambda x: int(len(filter(prep(x).contains, ny_points))))
	df_map['density_m'] = df_map['count'] / df_map['area_m']
	df_map['density_km'] = df_map['count'] / df_map['area_km']
	# it's easier to work with NaN values when classifying
	df_map.replace(to_replace={'density_m': {0: np.nan}, 'density_km': {0: np.nan}}, inplace=True)

	# Calculate Jenks natural breaks for density
	breaks = nb(
	    df_map[df_map['density_km'].notnull()].density_km.values,
	    initial=300,
	    k=5)
	# the notnull method lets us match indices when joining
	jb = pd.DataFrame({'jenks_bins': breaks.yb}, index=df_map[df_map['density_km'].notnull()].index)
	df_map = df_map.join(jb)
	df_map.jenks_bins.fillna(-1, inplace=True)

	jenks_labels = ["<= %0.1f/km$^2$(%s blocks)" % (b, c) for b, c in zip(
	    breaks.bins, breaks.counts)]
	jenks_labels.insert(0, 'No restaurant (%s blocks)' % len(df_map[df_map['density_km'].isnull()]))
	plt.close()
	fig = plt.figure()
	ax = fig.add_subplot(111, axisbg='w', frame_on=False)
	# use a blue colour ramp - we'll be converting it to a map using cmap()
	cmap = plt.get_cmap('Blues')
	# draw wards with grey outlines
	df_map['patches'] = df_map['poly'].map(lambda x: PolygonPatch(x, ec='#555555', lw=.2, alpha=1., zorder=4))
	pc = PatchCollection(df_map['patches'], match_original=True)
	# impose our colour map onto the patch collection
	norm = Normalize()
	pc.set_facecolor(cmap(norm(df_map['jenks_bins'].values)))
	ax.add_collection(pc)

	# Add a colour bar
	cb = colorbar_index(ncolors=len(jenks_labels), cmap=cmap, shrink=0.5, labels=jenks_labels)
	cb.ax.tick_params(labelsize=6)

	# Show highest densities, in descending order
	highest = '\n'.join(
	    str(value[1]) for value in df_map[(df_map['jenks_bins'] == 4)][:10].sort().iterrows())
	highest = 'Most Dense Blocks:\n\n' + highest

	# Draw a map scale
	m.drawmapscale(
	    coords[0] + 0.19, coords[1] + 0.015,
	    coords[0], coords[1],
	    10.,
	    barstyle='fancy', labelstyle='simple',
	    fillcolor1='w', fillcolor2='#555555',
	    fontcolor='#555555',
	    zorder=5)

	# this will set the image width to 722px at 100dpi
	plt.title(genre + " Restaurant Density, New York")
	plt.tight_layout()
	fig.set_size_inches(7.22, 5.25)
	plt.savefig('image/' + genre+'_Restaurants_Density_NewYork.png', dpi=100, alpha=True)
	plt.show()

if __name__ == '__main__':
	genre=sys.argv[1]
	show_density(genre)

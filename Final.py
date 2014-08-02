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
import sys

folder = 'data/'

def genrePlot(genre, genreColor):

	infile=folder + genre+' Restaurant.txt'
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
	df = df.dropna()#drop data contains None(Just for practice)
	df[['rat','lat','lon']] = df[['rat','lat','lon']].astype(float)

	ny_xs=[]
	ny_ys=[]
	ny_zs=[]

	for mapped_x, mapped_y, mapped_z in zip(df['lon'], df['lat'], df['rat']):
		mapped_xy=m(mapped_x, mapped_y)

		if wards_polygon.contains(Point(mapped_xy)):
			ny_xs.append(mapped_xy[0])
			ny_ys.append(mapped_xy[1])
			ny_zs.append(mapped_z)
	area = [np.pi*s*s for s in ny_zs]#np.pi*(ny_zs**2)
	m.scatter(ny_xs,ny_ys,s=area,alpha=0.3,color = genreColor)
			
#Draw basemap
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

m.readshapefile(folder + 'new_york_city_fire_companies','newyork',drawbounds=False,color='none',zorder=2)
#print len(m.newyork[1]),type(m.newyork),m.newyork_info
df_map = pd.DataFrame({
	'poly':[Polygon(xy) for xy in m.newyork]})#,
#	'info':[ward['BoroName'] for ward in m.newyork_info]})
df_map['area_m'] = df_map['poly'].map(lambda x:x.area)
df_map['area_km'] = df_map['area_m']/1000000
wards_polygon = prep(MultiPolygon(list(df_map['poly'].values)))

# Draw a map scale
def show_regular(GenreList):
        colors = iter(cm.rainbow(np.linspace(0, 1, len(GenreList))))    
	# draw ward patches from polygons

	df_map['patches'] = df_map['poly'].map(lambda x: PolygonPatch(
		x,
		fc='#D3D3D3',
		ec='#787878', lw=.25, alpha=.9,
		zorder=4))

	plt.close()
	fig = plt.figure()
	ax = fig.add_subplot(111, axisbg='w', frame_on=False)
	
	# plot fire_companies by adding the PatchCollection to the axes instance
	ax.add_collection(PatchCollection(df_map['patches'].values, match_original=True))

        for genre in GenreList:
                genrePlot(genre, next(colors))
	m.drawmapscale(
		coords[0] + 0.19, coords[1] + 0.015,
		coords[0], coords[1],
		10.,
		barstyle='fancy', labelstyle='simple',
		fillcolor1='w', fillcolor2='#555555',
		fontcolor='#555555',
		zorder=5)
	plt.title(genre + " Restaurant Locations, New York")
	#plt.tight_layout()
	Name='_'.join(GenreList)
	#fig.set_size_inches(7.22, 5.25)
	plt.savefig('image/' + Name + '_Restaurants_Ratings_A_NewYork.png', dpi=100, alpha=0.1)
        plt.show()

if __name__ == '__main__':
        GenreList =sys.argv[1:]
        show_regular(GenreList)

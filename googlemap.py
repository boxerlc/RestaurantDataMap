import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.basemap import Basemap
import matplotlib.image as mpimg
import sys
folder='data/'

map = Basemap(projection='cyl',resolution = 'i', area_thresh = 0.1,
              llcrnrlon=-74.026335, llcrnrlat=40.697321,
              urcrnrlon=-73.806808, urcrnrlat=40.827598)

def genrePlot(genre, genreColor):
	
	InFile =folder + genre + ' Restaurant.txt'
	
	Lati = []
	Longi = []
	Value = []
	
	with open(InFile) as f:
		for Line in f:
			LineList = Line.split('\t')
			Value.append(float(LineList[2].split()[0]))
			Lati.append(float(LineList[6].split(',')[0].strip()))
			Longi.append(float(LineList[6].split(',')[1].strip()))
			
	area = np.pi*(np.log1p(80*Value))**2
	map.scatter(Longi, Lati ,s=area,alpha=0.35, color = genreColor)

def show_google(GenreList):
        colors = iter(cm.rainbow(np.linspace(0, 1, len(GenreList))))
        x = -73.872808
        y = 40.822598
        #map.drawcoastlines()
        #map.drawcountries()
        #map.drawmapboundary()
        im=mpimg.imread('bg.png')
        map.imshow(im,interpolation='lanczos',origin='upper')
        for genre in GenreList:
                color = next(colors)
                genrePlot(genre, color)
                map.scatter(x - 0.003, y + 0.0015 ,s=80,alpha=1, color = color)
                plt.text(x, y,genre)
                y = y -0.008
	Name='_'.join(GenreList)
	plt.savefig('image/' + Name + '_Restaurants_Ratings_B_NewYork.png', dpi=100, alpha=0.1)
        plt.show()

if __name__ == '__main__':
        GenreList = sys.argv[1:]#['Chinese', 'French', 'Japanese', 'Mexican', 'Italian', 'Korea']
        show_google(GenreList)

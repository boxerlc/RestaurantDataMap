from cStringIO import StringIO
import Image
import urllib




url = 'http://maps.googleapis.com/maps/api/staticmap?center=40.7629516,-73.9164846&zoom=12&size=1000x500&maptype=roadmap&sensor=false'
buffer1 = StringIO(urllib.urlopen(url).read())
image = Image.open(buffer1)
image.save('bg.png')
image.show()

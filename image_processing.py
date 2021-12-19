
from PIL import Image

from PIL.ExifTags import TAGS


def getPhysicalSize(fn):

    #Open the image file and get the size in pixels

    im = Image.open(fn)
    width, height = im.size

    #Try to get dpi information directly

    try:
        dpi = im.info['dpi']
    except:
        #If the direct acquisition fails, then try to obtain exif information

        t = {}
        info = im._getexif()

        #Get failed, return directly
        if not info:

            return 'Not known'

        #Extract horizontal resolution and vertical resolution from exif information

        for k, v in info.items():

            tt = TAGS.get(k)

            if tt in ('XResolution', 'YResolution'):

                t[tt] = v

        dpi = [item[1] for item in sorted(t.items())]

    #Get failed, return

    if not dpi:
        return 'Not known'




    if isinstance(dpi[0], tuple):
        w_dpi, h_dpi = dpi[0][0], dpi[1][0]
    else:
        w_dpi, h_dpi = dpi
    #Return physical size information, pixels/dpi resolution, and then convert to millimeters
    return (round(width/w_dpi*25.4,2), round(height/h_dpi*25.4,2))

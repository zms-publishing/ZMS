import _imaging
import os, sys
from PIL import Image

def main(argv):

    try:
        if len(argv) < 6:
            raise "CommandLineError"
        
        x0 = int(argv[0])
        y0 = int(argv[1])
        x1 = int(argv[2])
        y2 = int(argv[3])
        infile = argv[4]
        qual = int(argv[5])
        box = (x0, y0, x1, y2)
        
        try:
          im = Image.open(infile)
          im = im.crop(box)
          im.save(infile,"JPEG", quality=qual)
        except IOError:
          sys.stderr.write("cannot crop image for %s\n" % infile)
          sys.exit(1)
        
    except "CommandLineError":
      usage = """python img_crop.py x0 y0 x1 y1 infile quality\n"""
      sys.stderr.write(usage)
      sys.exit(1)

    
# If called from the command line
if __name__=='__main__': main(sys.argv[1:])



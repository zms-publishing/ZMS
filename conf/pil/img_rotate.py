import _imaging
import os, sys
from PIL import Image

def main(argv):

    try:
        if len(argv) < 3:
            raise "CommandLineError"

        direction = int(argv[0])
        infile = argv[1]
        qual   = int(argv[2])
        
        try:
          im = Image.open(infile)
          im = im.rotate(direction)    
          im.save(infile,"JPEG", quality=qual)
        except IOError:
          sys.stderr.write("cannot rotate image for %s\n" % infile)
          sys.exit(1)
        
    except "CommandLineError":
      usage = """python img_rotate.py direction infile quality\n"""
      sys.stderr.write(usage)
      sys.exit(1)

    
# If called from the command line
if __name__=='__main__': main(sys.argv[1:])




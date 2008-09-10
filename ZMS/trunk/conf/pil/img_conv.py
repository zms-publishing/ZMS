import _imaging
import os, sys
from PIL import Image

def main(argv):

    try:
        if len(argv) < 3:
            raise "CommandLineError"
        
        maxdim = int(argv[0])
        infile = argv[1]
        qual   = argv[2]
        
        outfile = os.path.splitext(infile)[0] + "_thumbnail"
        try:
          im = Image.open(infile)
          im = im.convert("RGB")
          try:
            im.thumbnail((maxdim,maxdim),Image.ANTIALIAS)
          except:
            im.thumbnail((maxdim,maxdim))
          im.save(outfile + ".jpg","JPEG",quality=int(qual))
        except IOError:
          sys.stderr.write("cannot create thumbnail for %s\n" % infile)
          sys.exit(1)
        
    except "CommandLineError":
      usage = """python img_conf.py maxdim infile quality\n"""
      sys.stderr.write(usage)
      sys.exit(1)

    
# If called from the command line
if __name__=='__main__': main(sys.argv[1:])


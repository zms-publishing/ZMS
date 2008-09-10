import _imaging
import os, sys
from PIL import Image

def main(argv):

    try:
        if len(argv) < 4:
            raise "CommandLineError"

        width = int(argv[0])
        height = int(argv[1])
        infile = argv[2]
        size = ( width, height)
        maxdim = int(argv[0])
        mode = argv[3]
        qual = int(argv[4])
        
        try:
            im = Image.open(infile)
            im = im.convert("RGB")

            if mode == 'thumbnail':
                try:
                    im.thumbnail((maxdim,maxdim),Image.ANTIALIAS)
                except:
                    im.thumbnail((maxdim,maxdim))
                im.save(infile,"JPEG", quality=qual)
            elif mode == 'resize':
                try:
                    im2 = im.resize(size,Image.ANTIALIAS)
                except:
                    im2 = im.resize(size)
                im2.save(infile,"JPEG", quality=qual)
            elif mode == 'square':
                try:
                    src_width, src_height = im.size
                    src_ratio = float(src_width) / float(src_height)
                    dst_width, dst_height = maxdim, maxdim
                    dst_ratio = float(dst_width) / float(dst_height)
                    if dst_ratio < src_ratio:
                        crop_height = src_height
                        crop_width = crop_height * dst_ratio
                        x_offset = float(src_width - crop_width) / 2
                        y_offset = 0
                    else:
                        crop_width = src_width
                        crop_height = crop_width / dst_ratio
                        x_offset = 0
                        y_offset = float(src_height - crop_height) / 3
                    im = im.crop((x_offset, y_offset, x_offset+int(crop_width), y_offset+int(crop_height)))
                    im = im.resize((dst_width, dst_height), Image.ANTIALIAS) 
                except:
                    im.resize(size) 
                im.save(infile,"JPEG", quality=qual)
                    
                
        except IOError:
          sys.stderr.write("cannot resize image for %s\n" % infile)
          sys.exit(1)

    except "CommandLineError":
      usage = """python img_resize.py width height infile quality\n"""
      sys.stderr.write(usage)
      sys.exit(1)

    
# If called from the command line
if __name__=='__main__': main(sys.argv[1:])



################################################################################
# zmsmathutil.py
#
# $Id: zmsmathutil.py,v 1.12 2004/11/24 21:02:52 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.12 $
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
################################################################################

# Imports.
import math


################################################################################
# Define the math-util.
################################################################################
class zmsmathutil:

  def __init__(self):
    pass

  meanstdv__roles__ = None
  def meanstdv(self, x):
    """ 
    Calculate mean and standard deviation of data x[]: 
      mean = {\sum_i x_i \over n} 
      std = sqrt(\sum_i (x_i - mean)^2 \over n-1) 
    """ 
    n, mean, std = len(x), 0, 0 
    for a in x: 
      mean = mean + a
    mean = mean / float(n) 
    for a in x:
      std = std + (a - mean)**2
    std = math.sqrt(std / float(n-1))
    seed = math.exp(math.floor(math.log(mean)/math.log(10))*math.log(10))
    std = int(std*seed)/seed
    return mean, std 

################################################################################

import importlib
import pkgutil
from pprint import pprint

import Products
# what the __path__ contains
pprint(Products.__path__)
# what python packaging suggests
pprint(list(pkgutil.iter_modules(Products.__path__, Products.__name__ + ".")))
# what the __path__ contains
pprint(Products.__path__)

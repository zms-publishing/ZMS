#!/usr/bin/env python3

import sys

from ZEO.ClientStorage import ClientStorage
from ZODB.DB import DB

SOCKET = "var/zeosocket"  # sys.argv[1]

try:
    # Depending on ZEO version, address argument may be ('AF_UNIX', SOCKET)
    # or just SOCKET or a tuple/path. Try the AF_UNIX form first.
    cs = ClientStorage(addr=SOCKET, storage="main")
    db = DB(cs)
    conn = db.open()
    root = conn.root()
    # simple access to ensure the storage is responsive:
    _ = list(root.keys())  # read-only, cheap
    conn.close()
    db.close()
    cs.close()
    print("OK")
    sys.exit(0)
except Exception as e:
    print("FAIL:", e, file=sys.stderr)
    sys.exit(1)

# ZMS Development: Proxy Cache and NGINX Control

This document explains in depth how ZMS controls HTTP caching for reverse proxies (especially NGINX) and browsers, and how this behavior is connected to content activation times.

## 1. Why this matters
In production, ZMS is usually behind a reverse proxy such as NGINX or Apache. The proxy serves cached responses quickly, but editorial use cases often require precise invalidation:

- publish content immediately
- unpublish at a specific date/time
- avoid stale pages for preview or restricted content

ZMS addresses this with response headers generated at render time and with a dynamic request-level expiration value.

## 2. Core mechanism in ZMS
The central helper is:

- Products/zms/standard.py: `set_response_headers_cache(context, request=None, cache_max_age=24*3600, cache_s_maxage=-1)`

It writes cache headers into the outgoing response and can set:

- Cache-Control
- Expires
- Pragma
- X-Accel-Expires (NGINX-specific)

### 2.1 No-cache cases (preview/restricted)
If a request is a preview request or if any object in the breadcrumb path is restricted, ZMS disables caching:

- Cache-Control: no-cache
- Expires: -1
- Pragma: no-cache

This prevents private or unpublished contexts from being cached by proxies.

### 2.2 Normal public caching
For public requests, ZMS sets default cache policy with shared and private TTLs (Time-To-Live):

- *s-maxage* controls shared/proxy caches
- *max-age* controls browser/private caches

Example header shape:

- Cache-Control: s-maxage=<seconds>, max-age=<seconds>, public, must-revalidate, proxy-revalidate

If cache_s_maxage is -1, ZMS uses cache_max_age for both.

## 3. Dynamic expiry from content lifecycle
The key to precise invalidation is request variable ZMS_CACHE_EXPIRE_DATETIME.

During rendering, object activation checks in ObjAttrs.isActive evaluate attributes such as:

- active
- attr_active_start
- attr_active_end

When a future start/end timestamp is found, ZMS stores the nearest relevant datetime in the current request as ZMS_CACHE_EXPIRE_DATETIME. This creates a per-request "earliest next change" deadline.

Implementation path:

- Products/zms/_objattrs.py: ObjAttrs.isActive
- Products/zms/standard.py: set_response_headers_cache reads ZMS_CACHE_EXPIRE_DATETIME

## 4. How X-Accel-Expires is used
After computing the dynamic expiration, ZMS calculates expire_in_secs and compares it with configured _cache_s_maxage_.

If the dynamic expiry is earlier than the configured proxy TTL, ZMS tightens headers to the shorter value and sets:

- X-Accel-Expires: <expire_in_secs>

This allows NGINX to expire cache entries exactly when content timing requires, instead of waiting for a static longer TTL.

The important detail is header precedence:

- NGINX treats Expires as the final cache-lifetime header when both Expires and X-Accel-Expires are present.
- That means a badly chosen or stale Expires value can neutralize a more precise X-Accel-Expires value.
- ZMS therefore separates the responsibilities: it computes the real content deadline in the application layer, while the proxy layer is configured to forward the final value only when it should be authoritative.

In the provisioning NGINX snippets this is handled in two steps:

- add_cache_headers.include sets the default proxy policy, handles static assets, request arguments, and the explicit ?ETag=... cache-busting pattern.
- add_cache_headers_override.include resolves the final X-Accel-Expires value lazily in the http context so that a later response-time override can still win.

The practical result is:

- static TTL defines an upper bound
- dynamic content dates can reduce that TTL per response
- the proxy configuration can still honor a server-side override when ZMS provides one

## 5. ETag-based cache busting
ZMS also supports explicit cache-busting by ETag-like URL variants.

The provisioning NGINX configuration recognizes URLs of the form ?ETag=... and treats them as a deliberate version token:

- if the ETag token changes, the resource is considered changed
- the proxy can then cache that URL effectively forever because the cache key changes with the token
- this is useful for static assets or generated resources where the caller can embed a content hash or revision identifier

In the current NGINX include logic:

- regular URLs with query arguments are not cached by default
- ?ETag=... is the exception
- when the ETag token is present, the cache lifetime is promoted to a long-lived value

In ZMS itself, ETag support exists in the binary/resource handling layer as well, especially for blob fields and browser resources. That means ZMS can use validator-based caching for assets where the content fingerprint is more reliable than a simple TTL.

At the code level this shows up in two places:

- blob field responses advertise HTTP caching metadata such as Last-Modified and ETags, and they also honor If-Range / ETag checks for partial transfers.
- the browser resource registration path provides a fallback NoETagAdapter so resource publishing remains compatible even when no resource-specific ETag implementation is available.

The practical rule is:

- use X-Accel-Expires for time-based expiration
- use ETags for content-version-based expiration
- use both when you want the proxy to expire by date for dynamic pages and still cache versioned assets very aggressively

## 6. Integration in page templates
Cache headers are usually applied in standard_html templates via TAL, for example:

```html
<tal:block tal:define="
  standard modules/Products.zms/standard;
  cache_expire python:standard.set_response_headers_cache(this, request, cache_max_age=6*3600, cache_s_maxage=-1)">
</tal:block>
```

This pattern is used in bundled themes and can be adapted per project.

## 7. Parameter tuning strategy
Typical tuning goals:

- editorial freshness for users
- high proxy hit ratio
- controlled bandwidth for clients

Guidance:

- Use lower max-age when browser freshness is important.
- Use higher s-maxage when proxy offloading is important.
- Rely on dynamic expiry plus X-Accel-Expires to avoid stale windows around scheduled publish/unpublish times.

A common setup is:

- cache_max_age=0 (or low) for browsers
- cache_s_maxage=hours for proxy caches

## 8. Relationship to NGINX config
This logic assumes an NGINX proxy cache setup that honors upstream cache headers and uses a stable cache key (usually scheme + host + request URI).

Example assumptions used by purge tooling:

- proxy_cache_path /var/cache/nginx levels=2:2 keys_zone=...;
- proxy_cache_key $scheme://$host$request_uri;

If your proxy cache key strategy differs, purge scripts must be adapted.

## 9. Instant cache purge by action
Besides passive expiration headers, ZMS can trigger active cache removal.

### 9.1 ZMS action workflow
A ZMS action manage_cachepurge can be imported. It exposes actions in the contextual UI (single page or list purge) and triggers an External Method cache_purge.

### 9.2 External Method example
```python
import subprocess, shlex
import os

def cache_purge(arg):
    args = ['sudo', '-u', 'nginx', '/usr/local/bin/cache_purge'] + shlex.split(arg)
    subprocess.check_call(args)
    return ('Cache Deleted: %s' % arg)
```

### 9.3 Shell/Python purge script example
```python
#!/usr/bin/env python

import os
from hashlib import md5
from os import path

"""
    This script assumes an nginx proxy configuration that looks similar to this:

    proxy_cache_path /var/cache/nginx levels=2:2 keys_zone=varcachenginx:10m;
    proxy_cache_key $scheme://$host$request_uri;
"""

PROXY_CACHE_PATH="/var/cache/nginx"

def proxy_cache_key(url):
    # This assumes exactly the URL is the cache key for nginx.
    # If that ever changes, this script needs adaptation.
    m = md5()
    m.update(url)
    return m.hexdigest()

def purge(url):
    key = proxy_cache_key(url)
    level1 = key[-2:]
    level2 = key[-4:-2]
    potential_cache_file = path.join(PROXY_CACHE_PATH, level1, level2, key)

    if path.exists(potential_cache_file):
        os.unlink(potential_cache_file)
    else:
        print("File %s for URL %r does not exist" % (potential_cache_file, url))


def _main():
    import sys
    for url in sys.argv[1:]:
        purge(url)

if __name__ == '__main__':
    _main()
```

## 10. Practical verification checklist
When validating behavior in staging/production:

1. Request a public page and inspect headers:
   - Cache-Control
   - Expires
   - X-Accel-Expires (when dynamic tightening applies)
2. Request preview or restricted content and verify no-cache headers.
3. Configure future attr_active_start or attr_active_end and verify response TTL drops toward the nearest change.
4. Trigger manual purge and verify cache file/key invalidation in proxy storage.

## 11. References

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control#directives
- http://nginx.org/en/docs/http/ngx_http_headers_module.html#expires
- https://github.com/nginxinc/nginx-wiki/blob/master/source/start/topics/examples/x-accel.rst


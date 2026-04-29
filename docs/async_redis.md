# Run Redis Server
## Easiest way: Run Redis using Docker (works everywhere)
If you have Docker installed:

```bash
docker run -d --name redis-server -p 6379:6379 redis
That’s it — Redis is now running on port 6379.
```

## Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

Check if it’s running:
```bash
redis-cli ping
```

Should return:
```
PONG
```

## Windows
Redis does not officially support Windows natively anymore, but you have two good options:

### Option A — Use Windows Subsystem for Linux (WSL)
Install WSL (Ubuntu recommended)

Inside Ubuntu:
```bash
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

### Option B — Use Docker on Windows
```bash
docker run -d --name redis-server -p 6379:6379 redis
```

## Test your Redis server
Run:
```bash
redis-cli
```

Then inside the shell:
```
set mykey hello
get mykey
```

You should see:
```
"hello"
```

If you want, I can also show you how to run Redis as a background service, configure persistence, or secure it with a password.

# Minimal Redis integration pattern for Zope 6
1. Install the Redis Python client
``` bash
pip install redis
```
2. Create a small Redis utility module
Create a file in your Zope package, e.g. myapp/redisutil.py:

``` python 
import redis

# Create a global Redis connection pool
_pool = redis.ConnectionPool(host="localhost", port=6379, db=0)

def get_redis():
    return redis.Redis(connection_pool=_pool)
This avoids reconnecting on every request.
```

3. Use Redis inside a Zope view
Example Zope BrowserView (myapp/browser/redisview.py):

``` python
from zope.publisher.browser import BrowserView
from .redisutil import get_redis

class RedisDemo(BrowserView):
    def __call__(self):
        r = get_redis()
        r.set("zope-demo", "Hello from Zope 6!")
        value = r.get("zope-demo").decode()

        return f"<html><body><h1>{value}</h1></body></html>"
```

Register the view in ZCML:

``` xml
<browser:page
    name="redis-demo"
    for="*"
    class=".redisview.RedisDemo"
    permission="zope.Public"
/>
```
Now visit:

``` Code
http://localhost:8080/redis-demo
```
You should see:

``` Code
Hello from Zope 6!
```
📮 Optional: Using Redis as a simple task queue
Zope itself is synchronous, but you can push jobs to Redis and process them with an external worker:

In Zope:
``` python
r = get_redis()
r.lpush("taskqueue", "do-something")
```
Worker script (outside Zope):
``` python
import redis
r = redis.Redis()

while True:
    task = r.brpop("taskqueue")
    print("Processing:", task[1].decode())
```

# Project layout
```text
my.rqdemo/
├─ pyproject.toml
├─ src/
│  └─ my/
│     └─ rqdemo/
│        ├─ __init__.py
│        ├─ configure.zcml
│        ├─ rqutil.py
│        ├─ worker.py
│        └─ browser/
│           ├─ __init__.py
│           └─ queue.py
```
pyproject.toml
```toml
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my.rqdemo"
version = "0.1.0"
description = "Zope 6 demo add-on using Redis RQ"
requires-python = ">=3.9"
dependencies = [
    "zope.publisher",
    "zope.browserpage",
    "redis",
    "rq",
]

[project.optional-dependencies]
test = ["pytest"]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```
src/my/rqdemo/__init__.py
```python
from zope.i18nmessageid import MessageFactory

_ = MessageFactory("my.rqdemo")

def initialize(context):
    """Zope 2-style init hook (kept for compatibility, often unused in Zope 6)."""
    pass
src/my/rqdemo/configure.zcml
xml
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:browser="http://namespaces.zope.org/browser"
    i18n_domain="my.rqdemo">

    <!-- Include browser views -->
    <include package=".browser" />

</configure>
```
src/my/rqdemo/rqutil.py — RQ + Redis helper
```python
import redis
from rq import Queue

_redis_connection = None
_queue = None

def get_redis():
    global _redis_connection
    if _redis_connection is None:
        _redis_connection = redis.Redis(host="localhost", port=6379, db=0)
    return _redis_connection

def get_queue(name="default"):
    global _queue
    if _queue is None:
        _queue = Queue(name, connection=get_redis())
    return _queue

# Example job function
def example_job(message):
    # In real life, do something useful here
    print(f"[RQ JOB] Received message: {message}")
    return f"Processed: {message}"
```
src/my/rqdemo/browser/__init__.py
```python
# empty is fine, just marks this as a package
```
src/my/rqdemo/browser/queue.py — BrowserView that enqueues a job
```python
from zope.publisher.browser import BrowserView
from ..rqutil import get_queue, example_job

class EnqueueJob(BrowserView):
    def __call__(self):
        q = get_queue()
        job = q.enqueue(example_job, "Hello from Zope 6!")

        self.request.response.setHeader("Content-Type", "text/html; charset=utf-8")
        return (
            "<html><body>"
            f"<h1>Job enqueued</h1>"
            f"<p>Job ID: {job.id}</p>"
            "</body></html>"
        )
```
src/my/rqdemo/browser/configure.zcml
```xml
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:browser="http://namespaces.zope.org/browser">

    <browser:page
        name="enqueue-job"
        for="*"
        class=".queue.EnqueueJob"
        permission="zope.Public"
    />

</configure>
```
src/my/rqdemo/worker.py — RQ worker process
Run this outside Zope (e.g. via python -m my.rqdemo.worker or python src/my/rqdemo/worker.py).

```python
import redis
from rq import Worker, Queue, Connection

listen = ["default"]

redis_url = "redis://localhost:6379/0"

def main():
    conn = redis.from_url(redis_url)
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()

if __name__ == "__main__":
    main()
```
## How to wire it into Zope 6
Install Redis and run a server (e.g. docker run -p 6379:6379 redis).

Install your add‑on into the Zope environment:

```bash
pip install -e .
```
Make sure Zope loads my.rqdemo (e.g. via zope.conf / wsgi.ini or buildout’s eggs list).

Start Zope 6.

Start the RQ worker:

```bash
python -m my.rqdemo.worker
```
Visit:

```text
http://localhost:8080/@@enqueue-job
```
You should see “Job enqueued” in the browser, and the worker process should log the job execution.
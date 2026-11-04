# encoding: utf-8

"""
Unit test for the schema reflection of ZMSSqlDb with a SQLAlchemyDA connection.

getEntitiesSQLAlchemyDA() runs once per request. It must use the engine of the
database adapter: a new engine per call keeps its pooled connection open until
the garbage collector removes the engine, which exhausts max_connections under
load (1040 Too many connections).

Only an in-memory SQLite engine is needed, no Zope instance and no database server.
The test auto-skips if SQLAlchemy is not installed.
"""

import unittest
from unittest import mock

# Product imports.
from Products.zms import zmssqldb


class StubWrapper:

  def __init__(self, engine):
    self.engine = engine


class StubDA:

  def __init__(self, engine):
    self.engine = engine

  def sa_zope_wrapper(self):
    return StubWrapper(self.engine)

  def getProperty(self, name):
    return {'dsn': 'sqlite://'}[name]


class StubSqlDb:

  def __init__(self, engine):
    self.da = StubDA(engine)

  def getDA(self):
    return self.da


# /ZMS5> python3 -m unittest tests.test_zmssqldb_reflection.ZMSSqlDbReflectionTest
class ZMSSqlDbReflectionTest(unittest.TestCase):

  def setUp(self):
    try:
      import sqlalchemy
    except ImportError:
      self.skipTest('SQLAlchemy not installed')
    self.engine = sqlalchemy.create_engine('sqlite://')
    self.addCleanup(self.engine.dispose)
    with self.engine.begin() as connection:
      connection.execute(sqlalchemy.text('CREATE TABLE fruit (id INTEGER PRIMARY KEY, name VARCHAR(32))'))

  def test_uses_engine_of_the_adapter(self):
    with mock.patch('sqlalchemy.create_engine') as create_engine:
      entities = zmssqldb.ZMSSqlDb.getEntitiesSQLAlchemyDA(StubSqlDb(self.engine))
    create_engine.assert_not_called()
    self.assertEqual(['fruit'], [x['id'] for x in entities])
    self.assertEqual(['id', 'name'], sorted(x['id'] for x in entities[0]['columns']))


if __name__ == '__main__':
  unittest.main()

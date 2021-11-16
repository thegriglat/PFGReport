
def rows_as_dicts(cursor):
    """ returns cx_Oracle rows as dicts """
    colnames = [i[0] for i in cursor.description]
    for row in cursor:
        yield dict(zip(colnames, row))

class RunSummary:
  cache = {}

  def __init__(self, connection):
    self.ocur = connection.cursor()

  @staticmethod
  def getValueFromDict(data, column='*'):
    if column == '*':
      return data
    else:
      if column in data:
        return data[column]
      else:
        raise RuntimeError("No such column '{0}'".format(column))

  def getRunInfo(self, run, column='*'):
    if run in self.cache:
      return self.getValueFromDict(self.cache[run], column)
    self.ocur.execute("select * from CMS_WBM.RUNSUMMARY where runnumber = :1", (run,))
    res = [x for x in rows_as_dicts(self.ocur)]
    if len(res) == 0:
      return None
    else:
      self.cache[run] = res[0]
      return self.getRunInfo(run, column)

  def getBField(self, run):
    return self.getRunInfo(run, 'BFIELD')

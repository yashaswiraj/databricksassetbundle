import dlt

@dlt.table
def demo_table_dab():
  return spark.range(100)


@dlt.table
def demo_table_dab1():
  return spark.range(500)


import req

def print_shifter_info(connection):
    from req import getCurrentShifter
    _l = (("ECAL", "DOC"), ("ECAL", "DG Lieutenant"),
          ("ECAL", "PFG expert"), ("ECAL", "trigger expert on call"))
    for subsys, shift in _l:
        getCurrentShifter(connection, shift, subsys)


def print_lhc_fills(connection, startdate, enddate):
    ocur = connection.cursor()
    ocur.execute(
        "select NVL(lhcfill, 0), id, begintime, endtime, name, integratedlumi, integratedlivelumi from CMS_RUNTIME_LOGGER.RUNTIME_SUMMARY where (begintime >= :startq or endtime >= :startq or endtime is NULL) and (endtime is NULL or begintime <= :endq or endtime <= :endq)",
        startq=startdate, endq=enddate)

    tableh = ("LHCFILL", "Start", "End", "Name",
              "Integrated Lumi", "Integrated Live Lumi", "Link")

    print("\n")
    print("|" + "|".join(tableh) + "|")
    print("|" + "|".join(("---" for x in tableh)) + "|")


    for row in sorted(ocur.fetchall(), key=lambda x: x[0], reverse=True):
        datarow = [row[0], row[2], row[3], row[4], row[5] / 1000.0, row[6] / 1000.0,
                   "[link]({0})".format(
            "https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/FillRuntimeChart?runtimeID=" + str(row[1]))
        ]
        print("|" + "|".join((str(x) for x in datarow)) + "|")

    print("\n")

def print_longest_runs(connection, startdate, enddate, maxn):
    print ("## {} longest runs".format(maxn))
    print ("\n")
    runs = req.getRuns(connection, startdate, enddate)
    runs.sort(key=lambda x: x['duration'], reverse=True)
    print_runs(runs[:maxn])
    print ("\n")

def print_all_runs(connection, startdate, enddate):
    print ("## All runs")
    print ("\n")
    runs = req.getRuns(connection, startdate, enddate)
    print_runs(runs)
    print ("\n")

def print_runs(runs):
    header = runs[0].keys()
    print("\n")
    print("|" + "|".join(header) + "|")
    print("|" + "|".join(("---" for x in header)) + "|")

    for r in runs:
        print("|" + "|".join((str(x[1]) for x in r.items())) + "|")
    
    print("\n")

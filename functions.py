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
        "select NVL(lhcfill, 0), id, begintime, endtime, name, integratedlumi, integratedlivelumi from CMS_RUNTIME_LOGGER.RUNTIME_SUMMARY where (begintime >= :startq or endtime >= :startq or endtime is NULL) and (endtime is NULL or begintime <= :endq or endtime <= :endq) and (begintime is not NULL) and (systime - begintime < 5)",
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


def print_longest_runs(runs, maxn):
    print("## {} longest runs".format(maxn))
    print("\n")
    q = sorted(runs, key=lambda x: x['Duration'], reverse=True)
    print_runs(q[:maxn])
    print("\n")


def print_all_runs(runs):
    print("## All runs")
    print("\n")
    q = sorted(runs, key=lambda x: x['Run nb'], reverse=True)
    print_runs(q)
    print("\n")


def print_runs(runs):
    header = [
        "Run nb",
        "Start",
        "End",
        "Duration",
        "Trigger Base",
        "B Field",
        "ECAL",
        "ES",
        "Deliv Lumi",
        "Live Lumi",
        "N Lumi",
        "Coll",
        "Stable Beam",
        "TCDS Diff",
        "LHC status"
    ]
    print("\n")
    print("|" + "|".join(header) + "|")
    print("|" + "|".join(("---" for x in header)) + "|")

    for r in runs:
        print("|" + "|".join((str(r[x]) for x in header)) + "|")
    print("\n")

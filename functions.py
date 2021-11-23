import req
from datetime import timedelta

coll_runs_style = """
font-weight: bold;
"""

coll_5m_runs_style = """
border: 2px solid green;
"""

coll_wo_ecal_es_runs_style = """
background-color: #FFCCCC;
"""

cosmic_runs_style = """
background-color: #E0E0E0;
"""


def print_shifter_info(connection):
    from req import getCurrentShifter
    _l = (("ECAL", "DOC"), ("ECAL", "DG Lieutenant"),
          ("ECAL", "PFG expert"), ("ECAL", "trigger expert on call"))
    for subsys, shift in _l:
        getCurrentShifter(connection, shift, subsys)


def print_lhc_fills(connection, startdate, enddate):
    ocur = connection.cursor()
    ocur.execute(
        "select NVL(lhcfill, 0), id, begintime, endtime, name, integratedlumi, integratedlivelumi from CMS_RUNTIME_LOGGER.RUNTIME_SUMMARY where (begintime >= :startq or endtime >= :startq or endtime is NULL) and (endtime is NULL or begintime <= :endq or endtime <= :endq) and (begintime is not NULL) and (sysdate - begintime < interval '5' day)",
        startq=startdate, endq=enddate)

    tableh = ("LHCFILL", "Start", "End", "Name",
              "Integrated Lumi", "Integrated Live Lumi", "Link")

    data = ocur.fetchall()
    if len(data) != 0:
        print("\n")
        print("|" + "|".join(tableh) + "|")
        print("|" + "|".join(("---" for x in tableh)) + "|")
        for row in sorted(data, key=lambda x: x[0], reverse=True):
            datarow = [row[0], row[2], row[3], row[4], row[5] / 1000.0, row[6] / 1000.0,
                       "[link]({0})".format(
                "https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/FillRuntimeChart?runtimeID=" + str(row[1]))
            ]
            print("|" + "|".join((str(x) for x in datarow)) + "|")
        print("\n")


def filter_collision_runs_ids(runs):
    r = []
    i = 0
    for x in runs:
        if "collision" in x["Trigger Base"]:
            r.append(i)
        i += 1
    return r


def filter_time_ids(runs, seconds):
    r = []
    i = 0
    for x in runs:
        h = int(x["Duration"].split(":")[0])
        m = int(x["Duration"].split(":")[1])
        s = int(x["Duration"].split(":")[2])
        if "collision" in x["Trigger Base"] and timedelta(hours=h, minutes=m, seconds=s).total_seconds() > seconds:
            r.append(i)
        i += 1
    return r


def filter_ecal_es_ids(runs):
    r = []
    i = 0
    for x in runs:
        if "collision" in x["Trigger Base"] and (x["ECAL"] == "OUT" or x["ES"] == "OUT"):
            r.append(i)
        i += 1
    return r


def filter_cosmic_runs(runs):
    r = []
    i = 0
    for x in runs:
        if "cosmic" in x["Trigger Base"]:
            r.append(i)
        i += 1
    return r


def print_longest_runs(runs, maxn):
    print("## {} longest runs".format(maxn))
    print("\n")
    q = sorted(runs, key=lambda x: x['Duration'], reverse=True)
    q = sorted(q[:maxn], key=lambda x: x['Run nb'], reverse=True)
    print_runs(q, "longestruns")
    print("\n")


def print_styles(tablename, run_ids, style):
    print("<style>")
    for i in run_ids:
        print(
            ".{tn} table tbody > tr:nth-child({n}) {{".format(tn=tablename, n=i + 1))
        print(style)
        print("}")
    print("</style>")


def print_all_runs(runs):
    print("## All runs")
    q = sorted(runs, key=lambda x: x['Run nb'], reverse=True)
    print_runs(q, "allruns")
    print("\n")


def print_runs(runs, tablename):
    header = [
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
    if tablename:
        print("<div class='{0}'>\n\n".format(tablename))
    else:
        print("\n")
    print("| Run nb | " + "|".join(header) + "|")
    print("| ---    | " + "|".join(("---" for x in header)) + "|")

    for r in runs:
        print("| [{0}](https://cmsoms.cern.ch/cms/runs/report?cms_run={0}) | ".format(
            r['Run nb']) + "|".join((str(r[x]) for x in header)) + "|")
    print("\n</div>\n")

    coll_runs = filter_collision_runs_ids(runs)
    coll_5m_runs = filter_time_ids(runs, 5*60)
    coll_wo_ecal_es_runs = filter_ecal_es_ids(runs)
    cosmic_runs = filter_cosmic_runs(runs)

    print_styles(tablename, coll_runs, coll_runs_style)
    print_styles(tablename, coll_5m_runs, coll_5m_runs_style)
    print_styles(tablename, coll_wo_ecal_es_runs, coll_wo_ecal_es_runs_style)
    print_styles(tablename, cosmic_runs, cosmic_runs_style)

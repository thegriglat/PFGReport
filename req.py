import subprocess
import datetime


def rows_as_dicts(cursor):
    """ returns cx_Oracle rows as dicts """
    colnames = [i[0] for i in cursor.description]
    for row in cursor:
        yield dict(zip(colnames, row))


def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


FEDS = {
    "EB+": list(range(628, 646)) + [663],
    "EB-": list(range(610, 628)) + [662],
    "EE+": list(range(646, 655)) + [664],
    "EE-": list(range(601, 610)) + [661],
    "ES-": [520, 522, 523, 524, 525, 528, 529, 530, 531, 532, 534, 535, 537, 539, 540, 541, 542, 545, 546, 547],
    "ES+": [548, 549, 551, 553, 554, 555, 556, 557, 560, 561, 563, 564, 565, 566, 568, 570, 571, 572, 573, 574]
}


def getCurrentShifter(connection, shift, subsystem="DAQ"):
    cur = connection.cursor()
    cur.execute("select shift_type_id from CMS_SHIFTLIST.SHIFT_TYPE where shift_type = :1 and sub_system = :2",
                (shift, subsystem))
    res = cur.fetchone()
    if res is None:
        return None
    shifttype_id = res[0]
    cur.execute(
        "select shifter_id from CMS_SHIFTLIST.SHIFT_ROSTER where SHIFT_TYPE_ID = :1 and sysdate between shift_start and shift_end",
        (shifttype_id,))
    a = cur.fetchone()
    if a:
        shifter_id = a[0]
    else:
        shifter_id = None
    subp = subprocess.Popen(['phonebook', '--ccid', str(shifter_id), '-a'], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = subp.communicate()
    stdout = stdout.decode().split('\n')
    displayname = ""
    email = ""
    for _l in stdout:
        if "Display Name" in _l:
            displayname = _l.split(':')[1].strip()
        if "E-mail" in _l:
            email = _l.split(':')[1].strip()
    if email == '' and displayname == '':
        print("Current {0} {1}: Not found".format(subsystem, shift))
    print("Current {2} {3}: [{0}]({1})\n".format(displayname,
          "mailto:" + email, subsystem, shift))


def getRuns(connection, startdate, enddate):
    result = []
    ocur = connection.cursor()
    ocur.execute("select runnumber, starttime, stoptime, stoptime - starttime as duration, triggerbase, bfield, ecal_present, es_present \
  from CMS_WBM.runsummary where (starttime >= :startq or stoptime >= :startq) and (starttime <= :endq or stoptime <= :endq) order by runnumber desc",
                 startq=startdate, endq=enddate)
    for row in ocur.fetchall():
        # row[5] = "{0:.1f}".format(row[5])  # BFIELD
        # 0: ECAL IN/OUT, 1: ES IN/OUT
        in_out_ecal = ["OUT", "IN"][row[-2]]
        in_out_es = ["OUT", "IN"][row[-1]]
        excludedFEDs = {}
        fedstatus = getExcludedFEDs(connection, row[0])
        for det in ('EB-', "EB+", "EE-", "EE+", "ES-", "ES+"):
            excludedFEDs[det] = [
                x for x in fedstatus if x in FEDS[det]]
        if in_out_ecal != "OUT" and sum([len(excludedFEDs[x]) for x in ('EB-', "EB+", "EE-", "EE+")]) != 0:
            redrun = True
            in_out_ecal = "PARTIAL " + in_out_ecal
            in_out_ecal = "<span title=\"{0}\">{1}</span>".format(", ".join([str(x) for x in fedstatus if x in FEDS["EB+"] or x in FEDS["EB-"]
                                                                             or x in FEDS["EE+"] or x in FEDS["EE+"]]), in_out_ecal)
        if in_out_es != "OUT" and sum([len(excludedFEDs[x]) for x in ('ES-', "ES+")]) != 0:
            redrun = True
            in_out_es = "PARTIAL " + in_out_es
            in_out_es = "<span title=\"{0}\">{1}</span>".format(", ".join([str(x) for x in fedstatus if x in FEDS["ES+"] or x in FEDS["ES-"]]),
                                                                in_out_es)
        # if row[2] is None:  # stoptime
        #    row[3] = datetime.datetime.now() - row[1]
        stablebeam = isStableBeam(connection, row[0])
        if not stablebeam and 'collision' in row[4]:  # row[4] is triggerbase
            pass
            # row[4] = row[4] + \
            #    " <span title=\"No STABLE BEAM found in this run\">[..]</span>"
        iscollision = isCollision(connection, row[0])
        ocur.execute(
            "select delivlumi, livelumi from CMS_RUNTIME_LOGGER.LUMI_SECTIONS where runnumber = :run order by lumisection", run=row[0])
        res = ocur.fetchall()
        n_lumisections = len(res)
        delivlumi = "--"
        livelumi = "--"
        if iscollision and n_lumisections > 1:
            lsidx = n_lumisections - 1
            startlsidx = 0
            while lsidx > 0 and (res[lsidx][0] == 0 or res[lsidx][1] == 0):
                lsidx -= 1
            while startlsidx < n_lumisections and (res[startlsidx][0] is None or res[startlsidx][1] is None):
                startlsidx += 1
            try:
                delivlumi = "{0:.2f}".format(
                    (res[lsidx][0] - res[startlsidx][0]) / 1000.0)
                livelumi = "{0:.2f}".format(
                    (res[lsidx][1] - res[startlsidx][1]) / 1000.0)
            except Exception as e:
                print("<!-- ", str(e), " -->")
        elif n_lumisections == 0:
            delivlumi = 0
            livelumi = 0
        lhcstatuses = getLHCStatusForRun(connection, row[0])[0]
        tcdsdiff = getTCDSFreqMonVDiff(connection, row[0])
        if tcdsdiff is None:
            tcdsdiff = 0
        duration = "00:00:00"
        if row[3] is not None:
            duration = strfdelta(
                row[3], "{hours:02d}:{minutes:02d}:{seconds:02d}")
        tmp = {
            "Run nb": row[0],
            "Start": row[1],
            "End": row[2],
            "Duration":  duration,
            "Trigger Base": row[4],
            "B Field": "{:.3f}".format(row[5]),
            "Ecal": row[6],
            "Es": row[7],
            "Deliv Lumi": delivlumi,
            "Live Lumi": livelumi,
            "Coll": iscollision,
            "Stable Beam": stablebeam,
            "TCDS Diff": tcdsdiff,
            "LHC status": lhcstatuses
        }
        result.append(tmp)
    return result


def getTCDSFreqMonVDiff(connection, run):
    ocur = connection.cursor()
    import runsummary
    rs = runsummary.RunSummary(connection)
    runstart = rs.getRunInfo(run, "STARTTIME")
    runend = rs.getRunInfo(run, "STOPTIME")
    sql = "select max(frequency) - min(frequency) from CMS_TCDS_MONITORING.TCDS_FREQMON_V where timestamp between :1 and :2"
    ocur.execute(sql, (runstart, runend))
    r = ocur.fetchone()
    if r is not None:
        return r[0]
    return r


def getLHCStatuses(connection):
    ocur = connection.cursor()
    ocur.execute(
        "select * from CMS_LHC_BEAM_COND.LHC_BEAMMODE order by diptime asc")
    _lhcstatuses = [x for x in rows_as_dicts(ocur)]
    return _lhcstatuses


def getLHCStatusForRun(connection, run):
    import runsummary
    rs = runsummary.RunSummary(connection)
    runstart = rs.getRunInfo(run, "STARTTIME")
    runend = rs.getRunInfo(run, "STOPTIME")
    if runend is None:
        import datetime
        runend = datetime.datetime.now()
    lhcstatuses = getLHCStatuses(connection)
    statuses = []
    for sti in range(len(lhcstatuses)):
        st = lhcstatuses[sti]
        try:
            nextst = lhcstatuses[sti + 1]
        except:
            if st['DIPTIME'] <= runend:
                statuses.append(st)
            continue
        if st['DIPTIME'] <= runstart and nextst['DIPTIME'] <= runstart:
            continue
        elif st['DIPTIME'] >= runend:
            continue
        else:
            statuses.append(st)
    return [x['VALUE'] for x in statuses]


def isCollision(connection, run):
    from runsummary import RunSummary
    try:
        triggerbase = RunSummary().getRunInfo(run, 'TRIGGERBASE')
    except:
        # no such run
        triggerbase = ""
    if triggerbase is None:
        triggerbase = ""
    if 'collision' not in triggerbase:
        return False
    lumis = getLumisections(connection, run)
    stablels = sum((1 for x in lumis if x['BEAM1_STABLE']
                    == 1 and x['BEAM2_STABLE'] == 1))
    # run has mpre than 0 normal lumi
    return stablels > 0


def isStableBeam(connection, run):
    lumis = getLumisections(connection, run)
    return sum((1 for x in lumis if x['BEAM1_STABLE']
                == 1 and x['BEAM2_STABLE'] == 1)) != 0


def getLumisections(connection, run):
    ocur = connection.cursor()
    ocur.execute(
        "select * from CMS_RUNTIME_LOGGER.LUMI_SECTIONS where runnumber = :run", run=run)
    return [x for x in rows_as_dicts(ocur)]


def getFEDStatus(connection, run):
    sql = "select string_value from CMS_RUNINFO.RUNSESSION_PARAMETER where runnumber = :1 and name = :2"
    ocur = connection.cursor()
    ocur.execute(sql, (run, "CMS.LVL0:FED_ENABLE_MASK"))
    res = ocur.fetchone()
    if res is None:
        return None
    res = res[0].strip()
    if len(res) == 0:
        return {}
    fedlist = res.split('%')
    result = {}
    for pair in fedlist:
        if '&' not in pair:
            continue
        fed, status = pair.split('&')
        fed = int(fed)
        if status == '':
            status = 0
        status = 1 if int(status) != 0 else 0
        result[fed] = status
    return result


def getExcludedFEDs(connection, run):
    st = getFEDStatus(connection, run)
    return [x for x in st if st[x] == 0]

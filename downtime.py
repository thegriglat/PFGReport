
# from CMS_RUNTIME_LOGGER.DOWNTIME_CATEGORIES
CAT_IDS = {'ECAL_DAQ': 6, "ES_DAQ": 81, 'ES_PWR': 82, 'L1_ECAL_TPG': 24}


def get_keys():
    return sorted(CAT_IDS.keys())


def print_downtime(connection, startdate, enddate, key):
    print("### {0} downtime\n".format(key))
    header = ("Run", "Downtime", "Uptime", "Duration", "Details",
              "Fill name", "Lumilost (approx.), pb<sup>-1</sup>")
    catid = CAT_IDS[key]
    sql = "select de.id, de.runnumber, to_char(de.downtime, 'DD-MON-YYYY HH24:MI:SS'), to_char(de.uptime, 'DD-MON-YYYY HH24:MI:SS'), de.uptime - de.downtime as losttime, de.DETAILS, rs.NAME as fillname from \
  CMS_RUNTIME_LOGGER.DOWNTIME_EVENTS de \
  inner join CMS_RUNTIME_LOGGER.RUNTIME_SUMMARY rs \
  on rs.id = de.RUNTIME_ID \
  where uptime >= :startq and downtime <= :endq and cat_id = :catid order by runnumber desc"
    ocur = connection.cursor()
    ocur.execute(sql, startq=startdate, endq=enddate, catid=catid)
    tableb = ocur.fetchall()[:]
    if len(tableb) == 0:
        print("no downtime info found\n")
        return
    for row in tableb:
        lumisql = "select delivlumi from CMS_RUNTIME_LOGGER.LUMI_SECTIONS where  \
 STARTTIME >= (select downtime from CMS_RUNTIME_LOGGER.DOWNTIME_EVENTs where runnumber = :run and cat_id = :catid and id = :id) \
 and  starttime <= (select uptime from CMS_RUNTIME_LOGGER.DOWNTIME_EVENTs where runnumber = :run and cat_id = :catid and id = :id)"
        ocur.execute(lumisql, run=row[1], id=row[0], catid=catid)
        r = ocur.fetchall()
        try:
            lumilost = (r[-1][0] - r[0][0]) / 1000.0
        except:
            lumilost = "None"
        # lslist.append(lumilost)
        tableb[tableb.index(row)] = ["[{0}](https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/RunParameters?RUN={1})".format(
            row[1], str(row[1]))] + list(row[2:]) + [lumilost]

    print("\n")
    print("|" + "|".join(header) + "|")
    print("|" + "|".join(("---" for x in header)) + "|")

    for r in tableb:
        print("|" + "|".join((str(x) for x in r)) + "|")
    print("\n")


import argparse
import datetime

from oracle import OracleInit
import functions

DATEFORMAT = "%d-%m-%Y"


def main():
    parser = argparse.ArgumentParser(description='PDF report')
    parser.add_argument('-u', '--user', dest='user', default="cms_ecal_r",
                        help='Oracle user')
    parser.add_argument('-c', '--connect', dest='host', default="cms_omds_lb",
                        help='Oracle connection string')
    parser.add_argument('-p', '--password', dest='password', required=True,
                        help='Oracle password')
    parser.add_argument('-s', '--start', dest='start',
                        help='Start date')
    parser.add_argument('-e', '--end', dest='end',
                        help='End date')
    args = parser.parse_args()

    startdate = datetime.datetime.now() - datetime.timedelta(days=1)
    if args.start:
        startdate = datetime.datetime.strptime(args.start, DATEFORMAT)

    enddate = datetime.datetime.now()
    if args.end:
        enddate = datetime.datetime.strptime(args.start, DATEFORMAT)

    print("# PFG Report for the period from {0} until {1}".format(
        startdate.strftime(DATEFORMAT), enddate.strftime(DATEFORMAT)))

    connection = OracleInit(args.user, args.password, args.host)

    functions.print_shifter_info(connection)

    functions.print_lhc_fills(connection,startdate, enddate)


if __name__ == "__main__":
    main()

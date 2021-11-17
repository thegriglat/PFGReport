# PFGReport

CMS ECAL PFG report utility

## How to install

Requirements:

 * `python3`
 * `pip3`
 * Oracle client libraries
 

```bash
git clone https://github.com/thegriglat/PFGReport.git
cd PFGReport

virtualenv env
source env/bin/activate
pip3 install -r requirements.txt
```

## Usage

```
usage: report.py [-h] [-u USER] [-c HOST] -p PASSWORD [-s START] [-e END]

PDF report

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  Oracle user
  -c HOST, --connect HOST
                        Oracle connection string
  -p PASSWORD, --password PASSWORD
                        Oracle password
  -s START, --start START
                        Start date
  -e END, --end END     End date
```

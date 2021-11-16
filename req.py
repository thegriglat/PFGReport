import subprocess


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
    print("Current {2} {3}: [{0}]({1})".format(displayname,
          "mailto:" + email, subsystem, shift))

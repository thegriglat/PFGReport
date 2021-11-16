import cx_Oracle


def OracleInit(user, password, host):
    return cx_Oracle.connect(user=user, password=password,
                             dsn=host,
                             encoding="UTF-8")

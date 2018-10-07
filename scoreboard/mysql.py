import MySQLdb


def check(addr, port, username, password, db='', query=None, result=None, **kwargs):
    up = False

    try:
        db = MySQLdb.connect(addr, username, password, db, port)

        cursor = db.cursor()

        up = True

        if query is not None:
            cursor.execute(query)

            if result is not None:
                up = up and cursor.fetchall() == result
    except MySQLdb.Error:
        up = False

    return up

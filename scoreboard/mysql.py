import logging

import MySQLdb


log = logging.getLogger('scoreboard:poll')


def check(addr, port, username, password, db='', query=None, result=None, timeout=1, **kwargs):
    log.info(('MySQL: trying {addr}:{port}' + (' with {username}' if username else '') + (' for {db}' if db else '')).format(addr=addr, port=port, username=username, db=db))

    up = False

    try:
        db = MySQLdb.connect(addr, username, password, db, port, connect_timeout=timeout)

        cursor = db.cursor()

        up = True

        if query is not None:
            cursor.execute(query)

            if result is not None:
                up = up and cursor.fetchall() == result
    except MySQLdb.Error:
        up = False
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            db.close()
        except Exception:
            pass

    return up

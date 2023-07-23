import sqlite3

con = sqlite3.connect('panopto.db')
cur = con.cursor()


def is_url_in_database(url):
    cur.execute("SELECT COUNT(*) FROM videos WHERE url=?", (url,))
    count = cur.fetchone()[0]
    return count > 0


def ToDatabase(classname, videotitle, classid, url):
    if not is_url_in_database(url):
        data = [
            (classname, classid, url, videotitle, False)
        ]
        cur.executemany("INSERT INTO videos VALUES (?,?,?,?,?)", data)
        con.commit()
        print("Data inserted successfully.")
    else:
        print("URL already exists in the database. Skipping insertion.")

import os
import notes

db_test_path = 'db_test.db'


def db_test_connection():
    # db_test_connection is not used as test function.
    # it's used to connect a test db instead of production one

    return notes.db_conn(db_test_path)


def test_connection():
    conn, cur = notes.db_conn(db_test_path)
    assert cur.connection == conn


def test_db_write_create_table():
    query = """
    CREATE TABLE IF NOT EXISTS notes (
            id                  INTEGER     NOT NULL    PRIMARY KEY
            AUTOINCREMENT,
            title               TEXT        NOT NULL,
            note                TEXT        NOT NULL,
            last_modification   TIMESTAMP   NOT NULL
        );
    """
    assert notes.db_write(db_test_connection, query, try_create_table=True)


def test_db_write_insert():
    query = """
    INSERT INTO notes
        (title, note, last_modification)
        VALUES
        ('Buzz Lightyear', 'To infinite and beyond', DATETIME('now')),
        ('Thundercats', 'Hooooooo', DATETIME('now')),
        ('Tom', 'Jerry', DATETIME('now')
    );
    """
    assert notes.db_write(db_test_connection, query)


def test_db_read():
    query = 'SELECT * FROM notes;'

    result = notes.db_read(db_test_connection, query)
    if (result):
        for row in result:
            print()
            print('ID:          ', row[0])
            print('Title:       ', row[1])
            print('Note:        ', row[2])
            print('Edited at:   ', row[3])
            print('-' * 80)
    assert result


def test_db_write_edit():
    delete_query = """
        UPDATE notes
        set title = 'Johnny Bravo'
        WHERE
        id = ?
        """
    id = 3

    assert notes.db_write(db_test_connection, delete_query, (id,))


def test_db_write_delete():
    delete_query = """
        DELETE FROM notes
        WHERE
        id = ?
        """
    id = 3

    assert notes.db_write(db_test_connection, delete_query, (id,))


def test_drop_db():
    # test_drop_db delete the test db after run that

    if (os.path.exists(db_test_path)):
        os.remove(db_test_path)

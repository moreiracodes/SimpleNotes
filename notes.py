import sqlite3
import datetime
import argparse


def db_conn(db_path='data.db'):
    # db_conn return a tuple with connection and cursor
    # open db connection
    try:
        connection = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES |
            sqlite3.PARSE_COLNAMES)
        cur = connection.cursor()

    except Exception as err:
        print(f"DB connect error: {err.args[0]}")

    return (connection, cur)


def db_read(db_conn, query, params=None):
    # db_read receive a db connection function to be
    # possible pass a mocking db on tests
    #
    # This function run a query and return an array of results
    try:

        connection, cur = db_conn()
        # check if was given parameters
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)

        # get result from query
        result = cur.fetchall()
        return result

    except sqlite3.Error as err:
        print(f"Error: {err.args[0]}")

    except Exception as err:
        print(f"Error: {err.args[0]}")

    finally:
        # close connection, if it open
        if cur.connection == connection:
            cur.close()
            connection.close()


def db_write(db_conn, query, params=None, try_create_table=False):
    # db_write receive a db connection function to be
    # possible pass a mocking db on tests
    try:

        connection, cur = db_conn()

        # check if was given parameters
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)

        connection.commit()

        # if the query try to create table, even with success,
        # it will return zero row affects so just use rowcount to check success
        # in case select, update or delete queries
        if ((not try_create_table) and (cur.rowcount > 0)):
            result = True
        else:
            result = False

            if (try_create_table):
                result = True

    except sqlite3.Error as err:
        print(f"Error: {err.args[0]}")
        result = False

    except Exception as err:
        print(f"Error: {err.args[0]}")
        result = False

    finally:
        # close connection, if it open
        if cur.connection == connection:
            cur.close()
            connection.close()

        return result


def list_all():

    query = """
        SELECT
            id,
            title,
            note,
            strftime('%d/%m/%Y %Hh%M', last_modification)
        FROM notes;
        """

    result = db_read(db_conn, query)

    if (result):
        for row in result:
            print()
            print('ID:          ', row[0])
            print('Title:       ', row[1])
            print('Note:        ', row[2])
            print('Edited at:   ', row[3])
            print('-' * 80)

    else:
        print('there is no notes to show')


def create_new_note():
    try:
        title = input("Enter a note title: ")
        text = input("Type your note: ")

        if (text == ""):
            raise Exception('note can not be empty')

        insert_query = """
        INSERT INTO notes
        (title, note, last_modification)
        VALUES
        (?, ?, ?);
        """
        if not db_write(
            db_conn,
            insert_query,
            (title, text, datetime.datetime.now())
        ):
            raise Exception('Something goes wrong on run insert query')

        return True

    except Exception as Ex:
        print(f"Error: {Ex.args[0]}")

        return False


def delete_note(id):

    # ask for a valid note id
    # this id must be a digit and exist in db
    ask_enter = True
    while (ask_enter):

        # check if id is integer or not
        try:
            # convert input to int to check if is a digit or not
            id = int(id)

            delete_query = """
            DELETE FROM notes
            WHERE
            id=?
            """

            result = db_write(db_conn, delete_query, (id,))

            if (result):
                print()
                print('note deleted')
                print()

                ask_enter = False

                return True

            else:
                raise Exception('invalid id')

        except ValueError:
            print('Error: id is not a digit')

            return False

        except Exception as Ex:
            print(f"Error: {Ex.args[0]}")

            return False


def edit_note(id):

    try:
        id = int(id)

        select_query = 'SELECT * FROM notes WHERE id=? ;'

        row = db_read(db_conn, select_query, (id,))

        print()
        print('ID:          ', row[0][0])
        print('Title:       ', row[0][1])

        answer_title = input('Do you want to edit this title? (y/n) ')
        answer_title = answer_title.lower()

        # check if the user want to edit the title
        match answer_title:
            case 'y':
                new_title = str(input("Enter a new title: "))
            case _:
                new_title = row[0][1]

        print('Note: ', row[0][2])

        answer_description = input('Do you want to edit this note? (y/n) ')
        answer_description = answer_description.lower()

        # check if the user want to edit the note
        match answer_description:
            case 'y':
                new_description = str(input("Enter a new note: "))
            case _:
                new_description = row[0][2]
                pass

        edit_query = """
        UPDATE notes
        SET title=?, note=?, last_modification=?
        WHERE
        id=?
        """

        if db_write(db_conn,
                    edit_query,
                    (new_title, new_description, datetime.datetime.now(), id)):
            print()
            print('note edited')
            print()

            return True
        else:
            raise Exception('Something goes wrong on run update query')

    except ValueError:
        print('Error: id is not a digit')

        return False

    except Exception as Ex:
        print(f"Error: {Ex.args[0]}")

        return False


if (__name__ == '__main__'):
    # If the table not exist create
    try:
        table_schema = """
        CREATE TABLE IF NOT EXISTS notes (
            id                  INTEGER     NOT NULL    PRIMARY KEY
            AUTOINCREMENT,
            title               TEXT        NOT NULL,
            note                TEXT        NOT NULL,
            last_modification   TIMESTAMP   NOT NULL
        );
        """
        if (not db_write(db_conn, table_schema, try_create_table=True)):
            raise Exception('Something goes wrong on run create table query')

    except sqlite3.Error as err:
        print(f"Error: {err.args[0]}")

    except Exception as err:
        print(f"Error: {err.args[0]}")

    # parse arguments passed from cmd
    parser = argparse.ArgumentParser(
        prog='SimpleNotes',
        description="This program serves to do notes")

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-l', '--list',
                       action='store_true',
                       help='List all notes')

    group.add_argument('-c', '--create',
                       action='store_true',
                       help='Create a new note')

    group.add_argument('-e', '--edit',
                       type=int,
                       default=False,
                       nargs='?',
                       help='Must be pass the id from the \
                            note which you want to edit')

    group.add_argument('-d', '--delete',
                       type=int,
                       default=False,
                       nargs='?',
                       help='Must be pass the id from the \
                            note which you want to delete')

    args = parser.parse_args()

    if (args.list):
        list_all()

    elif (args.create):
        create_new_note()

    elif (args.edit):
        edit_note(args.edit)

    elif (args.delete):
        delete_note(args.delete)

    else:
        parser.print_help()

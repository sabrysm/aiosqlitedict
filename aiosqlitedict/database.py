import aiosqlite
from ast import literal_eval


class Connect:
    """
    Instantiate a conversion to and from sqlite3 database and python dictionary.
    """

    def __init__(self, database_name: str, table_name: str, id_column: str):
        self.database_name = database_name
        self.table_name = table_name
        self.id_column = id_column

    async def to_dict(self, my_id, *column_names: str):
        """
        Convert a sqlite3 table into a python dictionary.
        :param my_id: The id of the row.
        :type my_id: int
        :param column_names: The column name.
        :type column_names: str
        :return: The dictionary.
        :rtype: dict
        """
        async with aiosqlite.connect(self.database_name) as db:
            async with db.cursor() as cursor:

                table_name = self.table_name.replace("'", "").replace('"', "")
                data = {}
                columns = str(column_names).replace("(", "").replace(
                    ")", "").replace('"', "").replace("'", "")
                columns = columns.replace(
                    columns[-1], "") if columns.endswith(",") else columns

                async def faster_literal_eval(lis):
                    return literal_eval(lis)
                if columns == "*":
                    getID = await cursor.execute(
                        f"SELECT {columns} FROM {table_name} WHERE {self.id_column} = ?", (my_id,))
                    fieldnames = [f[0] for f in getID.description]
                    values = await getID.fetchone()
                    values = list(values)
                    for v in range(len(values)):
                        if str(values[v]).startswith("[") or str(values[v]).startswith("{") or str(values[v]).startswith("("):
                            try:
                                values[v] = await faster_literal_eval(values[v])
                            except Exception as e:
                                raise Exception(e)
                        else:
                            continue
                    for i in range(len(fieldnames)):
                        data[fieldnames[i]] = values[i]
                    return data
                else:
                    getID = await cursor.execute(
                        f"SELECT {columns} FROM {table_name} WHERE {self.id_column} = ?", (my_id, ))
                    values = await getID.fetchone()
                    values = list(values)
                    for v in range(len(values)):
                        if str(values[v]).startswith("[") or str(values[v]).startswith("{") or str(values[v]).startswith("("):
                            try:
                                values[v] = await faster_literal_eval(values[v])
                            except Exception as e:
                                raise Exception(e)
                        else:
                            continue
                    for i in range(len(column_names)):
                        data[column_names[i]] = values[i]
                    return data

    #  To push data to db

    async def to_sql(self, my_id, dictionary: dict):
        """
        Convert a python dictionary into a sqlite3 table.
        :param my_id: The id of the row.
        :type my_id: int
        :param dictionary: The dictionary object.
        :type dictionary: dict
        :return: The SQLite3 Table.
        :rtype: sqlite
        """
        async with aiosqlite.connect(self.database_name) as db:
            async with db.cursor() as cursor:
                table_name = self.table_name
                getUser = await cursor.execute(f"SELECT {self.id_column} FROM {table_name} WHERE {self.id_column} = ?", (my_id, ))
                isUserExists = await getUser.fetchone()
                if isUserExists:
                    for key, val in dictionary.items():
                        if str(val).startswith("[") or str(val).startswith("{") or str(val).startswith("("):
                            val = str(val)
                        else:
                            pass
                        await cursor.execute(f"UPDATE {table_name} SET {key} = ? WHERE {self.id_column} = ?", (val, my_id,))
                else:
                    await cursor.execute(f"INSERT INTO {table_name} ({self.id_column}) VALUES ( ? )", (my_id, ))
                    for key, val in dictionary.items():
                        if str(val).startswith("[") or str(val).startswith("{") or str(val).startswith("("):
                            val = str(val)
                        else:
                            pass
                        await cursor.execute(f"UPDATE {table_name} SET {key} = ? WHERE {self.id_column} = ?", (val, my_id,))

            await db.commit()

    async def select(self, column_name: str, limit: int = None, order_by: str = None, ascending: bool = True
                     , equal=None, like: str = None, between: tuple = None, distinct: bool = False, offset: int = None):
        """
        Select a column from the table.

        :param column_name: The column name.
        :type column_name: str
        :param limit:
        :rtype: int
        :param order_by:
        :rtype: str
        :param ascending:
        :rtype: bool
        :param equal:
        :param like:
        :rtype: str
        :param distinct:
        :rtype: bool
        :param between:
        :rtype: tuple
        :param offset:
        :rtype: int
        :return: The list.
        :rtype: list
        """
        async with aiosqlite.connect(self.database_name) as db:
            async with db.cursor() as cursor:

                query = f"SELECT {column_name} FROM {self.table_name}"
                condition = False
                if distinct is True:
                    query = f"SELECT DISTINCT {column_name} FROM {self.table_name}"
                if equal is not None and condition is False:
                    condition = True
                    query += f" WHERE {column_name} = '{equal}'"
                elif equal is not None and condition is True:
                    query += f" AND {column_name} = '{equal}'"

                if like is not None and condition is False:
                    condition = True
                    query += f" WHERE {column_name} LIKE '%{like}%'"
                elif like is not None and condition is True:
                    query += f" AND {column_name} LIKE '%{like}%'"
                if between is not None and condition is False:
                    condition = True
                    query += f" WHERE {column_name} BETWEEN {range(between[0], between[1]).start} AND {range(between[0], between[1]).stop}"
                elif between is not None and condition is True:
                    query += f" AND {column_name} BETWEEN {range(between[0], between[1]).start} AND {range(between[0], between[1]).stop}"
                if order_by is not None:
                    query += f" ORDER BY {order_by}"
                if ascending is False:
                    query += f" DESC"
                else:
                    query += f""
                if limit is not None:
                    query += f" LIMIT {limit}"
                if offset is not None and limit is not None:
                    query += f" OFFSET {offset}"
                elif offset is not None and limit is None:
                    raise Exception("You can't use kwarg 'offset' without kwarg 'limit'")
                getValues = await cursor.execute(query)
                values = await getValues.fetchall()
                my_list = []

                def isfloat(num):
                    try:
                        float(num)
                        return True
                    except ValueError:
                        return False

                for i in values:
                    i = str(i)
                    i = i[1:-2]  # Remove round brackets in i
                    # Check the type of i
                    if i.isnumeric():
                        my_list.append(int(i))
                    elif isfloat(i):
                        my_list.append(float(i))
                    elif i == 'None' or i is None:
                        my_list.append(i)
                    elif i.startswith("'[") or i.startswith("'{") or i.startswith("'("):
                        i = eval(i)
                        my_list.append(eval(i))
                    elif i.isascii():
                        i = i[1:-1]
                        my_list.append(i)
                    else:
                        my_list.append(i)

                return my_list

    async def delete(self, my_id):
        """
        deletes a certain row from the table.
        :param my_id: The id of the row.
        :type my_id: int
        """
        async with aiosqlite.connect(self.database_name) as db:
            async with db.cursor() as cursor:
                table_name = self.table_name
                await cursor.execute(
                    f"DELETE FROM {table_name} WHERE {self.id_column} = ?", (my_id, ))
            await db.commit()

    async def execute(self, query):
        """
        Execute SQL query.
        """
        async with aiosqlite.connect(self.database_name) as db:
            async with db.cursor() as cursor:
                cur = await cursor.execute(query)
                res = await cur.fetchall()
            await db.commit()
            return res

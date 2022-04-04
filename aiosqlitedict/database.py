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
                getID = await cursor.execute(
                    f"SELECT {columns} FROM {table_name} WHERE {self.id_column} = ?", (my_id, ))
                values = await getID.fetchone()
                values = list(values)
                for v in range(len(values)):
                    if str(values[v]).startswith("["):
                        values[v] = values[v].replace("[", "").replace(']', "").replace(" ' ", "").\
                            replace(' " ', "").replace(" '", "").replace(' "', "").replace("' ", "").\
                            replace('" ', "").replace("'", "").replace('"', "").replace(",", "|")
                        values[v] = values[v].split("|")
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
                table_name = self.table_name.replace("'", "").replace('"', "")
                getUser = await cursor.execute(f"SELECT {self.id_column} FROM {table_name} WHERE {self.id_column} = ?", (my_id, ))
                isUserExists = await getUser.fetchone()
                if isUserExists:
                    for key, val in dictionary.items():
                        key = key.replace("'", "").replace('"', "")
                        val = str(val) if str(val).startswith("[") else val
                        await cursor.execute(f"UPDATE {table_name} SET {key} = ? WHERE {self.id_column} = ?", (val, my_id,))
                else:
                    await cursor.execute(f"INSERT INTO {table_name} ({self.id_column}) VALUES ( ? )", (my_id, ))
                    for key, val in dictionary.items():
                        key = key.replace("'", "").replace('"', "")
                        val = str(val) if str(val).startswith("[") else val
                        await cursor.execute(f"UPDATE {table_name} SET {key} = ? WHERE {self.id_column} = ?", (val, my_id,))

            await db.commit()

    async def select(self, column_name: str, limit=None, order_by=None, ascending=True):
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

        :return: The list.
        :rtype: list
        """
        async with aiosqlite.connect(self.database_name) as db:
            async with db.cursor() as cursor:

                table_name = self.table_name.replace("'", "").replace('"', "")
                column = str(column_name).replace("(", "").replace(
                    ")", "").replace('"', "").replace("'", "")
                column = column.replace(
                    column[-1], "") if column.endswith(",") else column
                if order_by is None:
                    order_by = column
                if limit is not None and order_by is None:
                    getValues = await cursor.execute(f"SELECT {column} FROM {table_name} LIMIT {limit}", (limit,))
                elif limit is None and order_by is not None and ascending is True:
                    getValues = await cursor.execute(f"SELECT {column} FROM {table_name} ORDER BY {order_by} ASC")
                elif limit is None and order_by is not None and ascending is not True:
                    getValues = await cursor.execute(f"SELECT {column} FROM {table_name} ORDER BY {order_by} DESC")
                elif limit is not None and order_by is not None and ascending is True:
                    getValues = await cursor.execute(f"SELECT {column} FROM {table_name} ORDER BY {order_by} ASC LIMIT {limit}")
                elif limit is not None and order_by is not None and ascending is not True:
                    getValues = await cursor.execute(f"SELECT {column} FROM {table_name} ORDER BY {order_by} DESC LIMIT {limit}")
                values = await getValues.fetchall()
                my_list = []
                holder = ''
                for i in values:
                    try:
                        if str(i).startswith("(") and str(i).endswith(",)") and "'" in str(values) and "[" in str(i):
                            my_list = [literal_eval(s) for t in values for s in t]
                            break
                        elif "'" not in str(values):
                            i = str(i).replace("(", "").replace(",)", "")
                            if "." in i:
                                i = float(i)
                            else:
                                i = int(i)
                            my_list.append(i)
                        else:
                            i = holder.join(str(i).replace("(", "").replace(",)", "").replace("'", ""))
                            my_list.append(i)
                    except:
                        print("None values")
                        break

                return my_list

    async def delete(self, my_id):
        """
        deletes a certain row from the table.

        :param my_id: The id of the row.
        :type my_id: int
        """
        async with aiosqlite.connect(self.database_name) as db:
            async with db.cursor() as cursor:
                table_name = self.table_name.replace("'", "").replace('"', "")
                await cursor.execute(
                    f"DELETE FROM {table_name} WHERE {self.id_column} = ?", (my_id, ))
            await db.commit()

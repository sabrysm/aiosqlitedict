![aiosqlitedictbanner](https://user-images.githubusercontent.com/51752028/160848765-35b1577d-0d94-44e3-bca4-d7ef133b5a97.png)

![PyPI](https://img.shields.io/pypi/v/aiosqlitedict?style=flat)
[![Downloads](https://pepy.tech/badge/aiosqlitedict)](https://pepy.tech/project/aiosqlitedict)    
 

aiosqlitedict is a Python package that provides fast, flexible and expressive data structures designed to make working with "relational" or "labeled" data both easy and intuitive.


## Main Features:
* Easy conversion between sqlite table and Python dictionary and vice-versa.
* Get values of a certain column in a Python list.
* delete from your table.
* convert your json file into a sql database table.
* Order your list with parameters like ``order_by``, ``limit`` ..etc
* Choose any number of columns to your dict, which makes it faster for your dict to load instead of selecting all.


## Installation

```bash
py -m pip install -U aiosqlitedict
```

## Getting Started
We start by connecting our database along with 
the table name and the reference column
```python
from aiosqlitedict.database import Connect

DB = Connect("database.db", "my_table", "user_id")
```


## Make a dictionary
The dictionary should be inside an async function.
```python
async def some_func():
    data = await DB.to_dict(123, "col1_name", "col2_name", ...)
```
You can insert any number of columns, or you can get all by specifying
the column name as '*'
```python
    data = await DB.to_dict(123, "*")
```

so you now have made some changes to your dictionary and want to
export it to sql format again?

## Convert dict to sqlite table
```python
async def some_func():
    ...
    await DB.to_sql(123, data)
```

But what if you want a list of values for a specific column?

## Select method
you can have a list of all values of a certain column.
```python
column1_values = await DB.select("col1_name")
```
to limit your selection use ``limit`` parameter.
```python
column1_values = await DB.select("col1_name", limit=10)
```
to start from a certain row.
```python
column1_values = await DB.select("col1_name", limit=10, offset=11)
#  returns 10 results starting from row number 11
```
to avoid duplicates use ``distinct``.
```python
column1_values = await DB.select("col1_name", distinct=True)
```
you can also get numbers in a certain range using ``between``
```python
column1_values = await DB.select("score", between=(1, 2000))
```
you can also arrange your ``list`` by using ``ascending`` parameter 
and/or ``order_by`` parameter and specifying a certain column to order your list accordingly.
```python
column1_values = await DB.select("col1_name", order_by="col2_name", ascending=False)
```

## delete method
delete a certain row from the table by defining the id of the row.
```python
async def some_func():
    ...
    await DB.delete(123)
```
if you prefer doing SQL Queries by yourself, you can use ``execute`` method

## Execute SQL query
```python
async def some_func():
    ...
    await DB.execute('SELECT * FROM my_table')
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
Please notice that
this package is built-on top of ``aiosqlite``
[MIT](https://github.com/sabrysm/aiosqlitedict/blob/main/LICENSE)

# Cpunk Mongo
[![CI](https://github.com/CyberpunkTeam/cpunk_mongo/actions/workflows/ci.yml/badge.svg)](https://github.com/CyberpunkTeam/cpunk_mongo/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/CyberpunkTeam/cpunk_mongo/badge.svg?branch=release/0.2.0)](https://coveralls.io/github/CyberpunkTeam/cpunk_mongo?branch=release/0.2.0)

It's a lib for working with MongoDB


## Usage

### Entity class representation
```python
from json import loads
from typing import Optional
from pydantic import BaseModel

class Item(BaseModel):
    item_id: str
    price: float
    currency_id: Optional[str] = "ARG"

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

    @staticmethod
    def get_schema():
        return {"item_id": str, "price": float, "currency_id": str}
```
### Create connection

```python
from cpunk_mongo.db import DataBase

url = 'server.example.com'
db_name = "example"
db = DataBase(url, db_name)
```

### Save entity

```python
from cpunk_mongo.db import DataBase
from json import loads
from typing import Optional
from pydantic import BaseModel


class Item(BaseModel):
    item_id: str
    price: float
    currency_id: Optional[str] = "ARG"

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

    @staticmethod
    def get_schema():
        return {"item_id": str, "price": float, "currency_id": str}

url = 'server.example.com'
db_name = "example"
db = DataBase(url, db_name)

item = Item(item_id="123", price=123.4)
ok = db.save(collection_name="items", item_to_save=item)
```
### Update entity

```python
from cpunk_mongo.db import DataBase
from json import loads
from typing import Optional
from pydantic import BaseModel


class Item(BaseModel):
    item_id: str
    price: float
    currency_id: Optional[str] = "ARG"

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

    @staticmethod
    def get_schema():
        return {"item_id": str, "price": float, "currency_id": str}

url = 'server.example.com'
db_name = "example"
db = DataBase(url, db_name)

item_id="123"
new_price = 140.0
item = Item(item_id=item_id, price=new_price)
ok = db.update(collection_name="items", param_filter="item_id", value=item_id, new_document=item)
```

### Delete entity

```python
from cpunk_mongo.db import DataBase


url = 'server.example.com'
db_name = "example"
db = DataBase(url, db_name)

item_id="123"
ok = db.delete(collection_name="items",
               param_filter="item_id",
               value=item_id)
```

### Delete all entities

```python
from cpunk_mongo.db import DataBase


url = 'server.example.com'
db_name = "example"
db = DataBase(url, db_name)

item_id="123"
ok = db.delete_all(collection_name="items")
```

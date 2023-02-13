from json import loads

import mongomock

from cpunk_mongo.db import DataBase
from typing import Optional, List
from pydantic import BaseModel


@mongomock.patch(servers=(("server.example.com", 27017),))
def test_init_db():
    db = create_db()
    assert db is not None


@mongomock.patch(servers=(("server.example.com", 27017),))
def test_insert_item():
    db = create_db()
    item_id = "145123213"
    price = 100.4
    item = create_item(item_id, price)
    ok = db.save(collection_name="items", item_to_save=item)
    assert ok is True


@mongomock.patch(servers=(("server.example.com", 27017),))
def test_insert_many_items():
    db = create_db()
    item_id_1 = "145123213"
    item_id_2 = "145123212"
    price = 100.4
    item_1 = create_item(item_id_1, price)
    item_2 = create_item(item_id_2, price)
    ok = db.save_many(collection_name="items", items_to_save=[item_1, item_2])
    assert ok is True

    result = db.find_by(collection_name="items", param="item_id", value=item_id_1)
    assert len(result) == 1

    result = db.find_by(collection_name="items", param="item_id", value=item_id_2)
    assert len(result) == 1


@mongomock.patch(servers=(("server.example.com", 27017),))
def test_get_item():
    db = create_db()
    item_id = "145123213"
    price = 100.4
    item = create_item(item_id, price)
    db.save(collection_name="items", item_to_save=item)

    result = db.find_by(collection_name="items", param="item_id", value=item_id)

    assert len(result) == 1


@mongomock.patch(servers=(("server.example.com", 27017),))
def test_get_item_with_output_model():
    db = create_db()
    item_id = "145123213"
    price = 100.4
    item = create_item(item_id, price)
    db.save(collection_name="items", item_to_save=item)

    result = db.find_by(
        collection_name="items", param="item_id", value=item_id, output_model=Item
    )

    assert len(result) == 1

    item_returned = result[0]

    assert item_returned.item_id == item_id
    assert item_returned.price == price


@mongomock.patch(servers=(("server.example.com", 27017),))
def test_filter_by_two_params():
    db = create_db()
    item_id = "145123213"
    price = 100.4
    currency_id = "USD"
    item = create_item(item_id, price, currency_id)
    db.save(collection_name="items", item_to_save=item)
    params = {"item_id": item_id, "currency_id": currency_id}
    result = db.filter(collection_name="items", filter_params=params, output_model=Item)

    assert len(result) == 1

    item_returned = result[0]

    assert item_returned.item_id == item_id
    assert item_returned.price == price
    assert item_returned.currency_id == currency_id


@mongomock.patch(servers=(("server.example.com", 27017),))
def test_delete_all():
    db = create_db()
    item_id = "145123213"
    price = 100.4
    item = create_item(item_id, price)
    db.save(collection_name="items", item_to_save=item)

    result = db.find_by(
        collection_name="items", param="item_id", value=item_id, output_model=Item
    )

    assert len(result) == 1

    db.delete_all(collection_name="items")

    result = db.find_by(
        collection_name="items", param="item_id", value=item_id, output_model=Item
    )

    assert len(result) == 0


@mongomock.patch(servers=(("server.example.com", 27017),))
def test_update_one():
    db = create_db()
    item_id = "145123213"
    price = 100.4
    item = create_item(item_id, price)
    db.save(collection_name="items", item_to_save=item)

    result = db.find_by(
        collection_name="items", param="item_id", value=item_id, output_model=Item
    )

    assert len(result) == 1
    new_price = 140.0
    item.price = new_price
    db.update(
        collection_name="items",
        param_filter="item_id",
        value=item_id,
        new_document=item,
    )

    result = db.find_by(
        collection_name="items", param="item_id", value=item_id, output_model=Item
    )

    assert len(result) == 1
    item_returned = result[0]
    assert item_returned.price == new_price
    assert item_returned.item_id == item_id


@mongomock.patch(servers=(("server.example.com", 27017),))
def test_delete_one():
    db = create_db()
    item_id = "145123213"
    price = 100.4
    item = create_item(item_id, price)
    db.save(collection_name="items", item_to_save=item)

    result = db.find_by(
        collection_name="items", param="item_id", value=item_id, output_model=Item
    )

    assert len(result) == 1

    ok = db.delete(collection_name="items", param_filter="item_id", value=item_id)
    assert ok is True

    result = db.find_by(
        collection_name="items", param="item_id", value=item_id, output_model=Item
    )

    assert len(result) == 0


@mongomock.patch(servers=(("server.example.com", 27017),))
def test_get_complex_item():
    db = create_db()
    item_id = "145123213"
    price = 100.4
    features = [Feature(name="color", value="red"), Feature(name="size", value="small")]
    item = create_item(item_id, price, features=features)

    db.save(collection_name="items", item_to_save=item)

    result = db.find_by(
        collection_name="items", param="item_id", value=item_id, output_model=Item
    )

    assert len(result) == 1
    assert len(result[0].features) == 2
    features = result[0].features
    feature_1 = features[0]
    assert feature_1.name == "color"
    assert feature_1.value == "red"


@mongomock.patch(servers=(("server.example.com", 27017),))
def test_like():
    db = create_db()
    user_1 = User(uid="1", name="Matias", lastname="Fonseca")
    user_2 = User(uid="2", name="Marcos", lastname="Lopez")
    user_3 = User(uid="3", name="Gonzalo", lastname="Marino")
    user_4 = User(uid="4", name="Jorge", lastname="Lopez")
    ok = db.save(collection_name="users", item_to_save=user_1)
    assert ok is True

    ok = db.save(collection_name="users", item_to_save=user_2)
    assert ok is True

    ok = db.save(collection_name="users", item_to_save=user_3)
    assert ok is True

    ok = db.save(collection_name="users", item_to_save=user_4)
    assert ok is True

    # filter by one field
    value = "mar"

    result = db.ilike(
        collection_name="users", fields=["name"], value=value, output_model=User
    )

    assert len(result) == 1

    # filter by two field
    value = "op"

    result = db.ilike(
        collection_name="users",
        fields=["name", "lastname"],
        value=value,
        output_model=User,
    )

    assert len(result) == 2

    value = "m"

    result = db.ilike(
        collection_name="users",
        fields=["name", "lastname"],
        value=value,
        output_model=User,
    )

    assert len(result) == 3

    # Remove duplicates
    value = "a"

    result = db.ilike(
        collection_name="users",
        fields=["name", "lastname"],
        value=value,
        output_model=User,
    )

    assert len(result) == 3


class User(BaseModel):
    name: str
    lastname: str
    uid: str

    def get_id(self):
        return self.uid

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

    @staticmethod
    def get_schema():
        return {"uid": str, "name": str, "lastname": str}


class Feature(BaseModel):
    name: str
    value: str


class Item(BaseModel):
    item_id: str
    price: float
    currency_id: Optional[str] = "ARG"
    features: List[Feature] = []

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

    @staticmethod
    def get_schema():
        return {"item_id": str, "price": float, "currency_id": str, "features": list}


def create_item(item_id, price, currency_id=None, features=None):
    if features is None:
        features = []
    item = Item(
        item_id=item_id, price=price, currency_id=currency_id, features=features
    )
    return item


def create_db():
    url = "server.example.com"
    db_name = "example"
    return DataBase(url, db_name)

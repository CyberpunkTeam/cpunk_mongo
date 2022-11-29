from json import loads

import mongomock

from cpunk_mongo.db import DataBase
from typing import Optional
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


class Item(BaseModel):
    item_id: str
    price: float
    currency_id: Optional[str] = "ARG"

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

    @staticmethod
    def get_schema():
        return {"item_id": str, "price": float, "currency_id": str}


def create_item(item_id, price, currency_id=None):
    item = Item(item_id=item_id, price=price, currency_id=currency_id)
    return item


def create_db():
    url = "server.example.com"
    db_name = "example"
    return DataBase(url, db_name)

import pymongo
from bson.json_util import dumps
from bson.json_util import loads


class DataBase:
    def __init__(self, url, db_name):
        self.db = pymongo.MongoClient(url).get_database(db_name)

    def save(self, collection_name, item_to_save):
        # item_to_save must has json() method for getting the document to save
        self.db[collection_name].insert_one(item_to_save.to_json())
        return True

    def update(self, collection_name, param_filter, value, new_document):
        self.db[collection_name].find_one_and_update(
            filter={param_filter: value}, update={"$set": new_document.to_json()}
        )
        return True

    def delete(self, collection_name, param_filter, value):
        param = {param_filter: value}
        result = self.db[collection_name].delete_many(param)
        return result.acknowledged

    def delete_all(self, collection_name):
        result = self.db[collection_name].delete_many({})
        return result.acknowledged

    def filter(self, collection_name, filter_params=None, output_model=None):
        # params is a dict like {field1: value1, field2:value2}
        if filter_params is None:
            filter_params = {}
        result = self.db[collection_name].find(filter_params)
        result = loads(dumps(result, default=str))
        if output_model is not None:
            result = list(
                map(lambda item: Transform.json_to_model(output_model, item), result)
            )
        return result

    def find_by(self, collection_name, param, value, output_model=None):
        # output_model must has method get_schema that return a list of name fields
        result = self.db[collection_name].find({param: value})

        result = loads(dumps(result, default=str))
        if output_model is not None:
            result = list(
                map(lambda item: Transform.json_to_model(output_model, item), result)
            )
        return result

    def ilike(self, collection_name, fields, value, output_model):
        results = []
        for field in fields:
            result_i = self.db[collection_name].find(
                {field: {"$regex": value, "$options": "i"}}
            )
            results += result_i

        result = loads(dumps(results, default=str))
        if output_model is not None:
            result = list(
                map(lambda item: Transform.json_to_model(output_model, item), result)
            )

        ids = {}
        final_result = []
        if len(fields) > 1:
            for result_i in result:
                m_id = result_i.get_id()
                if not (m_id in ids):
                    final_result.append(result_i)
                    ids[m_id] = True
        else:
            final_result = result
        return final_result


class Transform:
    @staticmethod
    def json_to_model(model, data):
        schema = model.get_schema()
        result = {}
        for field in schema:
            value = data.get(field)
            if value is not None:
                result[field] = schema[field](value)

        return model(**result)

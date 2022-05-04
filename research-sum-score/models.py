import configparser

import pymongo

config = configparser.ConfigParser()
config.read("config.ini")
MONGODB_HOST = config["Database"]["MONGODB_HOST"]
MONGODB_PORT = config["Database"]["MONGODB_PORT"]
DBUSER = config["Database"]["DBUSER"]
DBPASS = config["Database"]["DBPASS"]

assoc_absa_factor_mapping = {
    "stay":"stay_period",
    "length_of_stay":"length_of_stay_period",
    "review_group":"review_group_default_casted",
    "country":"country_iso_casted",
    "room_type":"room_type_casted",
}

class MongoDB:
    def __init__(self):
        self.DB_absa = None
        try:
            mongo = pymongo.MongoClient(host=f'{MONGODB_HOST}:{MONGODB_PORT}',
                                        username=f'{DBUSER}', password=f'{DBPASS}')
            if mongo.admin.command('ping'):
                self.DB_absa = mongo.absa
        except Exception as e:
            print(e)

    def count_by_factors(self, hotel_name, factors):
        filter_dict = [{"hotel_name": {"$eq": hotel_name}}]
        for factor in factors:
            factor_split = factor.split(":")
            factor_name = factor_split[0]
            factor_value = factor_split[1]
            mapped_factor_name = assoc_absa_factor_mapping[factor_name]
            filter_dict.append({mapped_factor_name: {"$eq": factor_value}})
        q_filter = {"$match": {"$and": [{"$and": filter_dict}]}}
        q_group = {"$group": {"_id": None, "COUNT(*)": {"$sum": 1}}}
        q_project = {"$project": {"COUNT(*)": "$COUNT(*)", "_id": 0}}
        pipeline = [q_filter, q_group, q_project]
        schema = self.DB_absa.reviewer_info_polarity
        results = list(schema.aggregate(pipeline)).copy()
        if len(results) > 0:
            count = results[0]["COUNT(*)"]
        else:
            count = 0
        return count

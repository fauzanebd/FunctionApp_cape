import logging
import os
import azure.functions as func
import json
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from DatabaseFunction.databaseFunctions import update_user_by_id

config = {
    "ENDPOINT": os.environ['COSMOS_URI'],
    "DATABASE_ID": "cape-db",
    "CONTAINER_ID": "user",
    "MASTERKEY": os.environ['COSMOS_PRIMARY_KEY']
}

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        client = cosmos_client.CosmosClient(config['ENDPOINT'], {'masterKey': config['MASTERKEY']})
        db = client.create_database_if_not_exists(id=config['DATABASE_ID'])
        container = db.create_container_if_not_exists(id=config['CONTAINER_ID'], partition_key=PartitionKey(path="/id"))
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f'Cosmos DB connection error: {e}')
        return func.HttpResponse(f'Cosmos DB connection error: {e}', status_code=500)
    except Exception as e:
        logging.error(f'Unknown error: {e}')
        return func.HttpResponse(f'Unknown error: {e}', status_code=500)

    data = {}
    data['id'] = req.params.get('id')
    data['user_name'] = req.params.get('user_name')
    data['user_email'] = req.params.get('user_email')
    data['user_phone'] = req.params.get('user_phone')
    data['user_balance'] = req.params.get('user_balance')
    

    if not data:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            data['id'] = req_body.get('id')
            data['user_name'] = req_body.get('user_name')
            data['user_email'] = req_body.get('user_email')
            data['user_phone'] = req_body.get('user_phone')
            data['user_balance'] = req_body.get('user_balance')

    new_data = {}
    for value in data:
        if value == 'id':
            continue
        if data[value] is not None :
            new_data[value] = data[value]
    
    logging.info(f'updating item with id: {data["id"]}')

    if new_data: 
        response = update_user_by_id(container, data['id'], new_data)
        return func.HttpResponse(
            json.dumps({
                "id": response.get('id'),
                "user_name": response.get('user_name'),
                "user_email": response.get('user_email'),
                "user_phone": response.get('user_phone'),
                "user_balance": response.get('user_balance')
            }),
            mimetype="application/json",
            status_code=200
        )
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a id in the query string or in the request body for a personalized response.",
             status_code=200
        )

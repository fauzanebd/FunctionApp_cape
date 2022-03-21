import logging
import os
import azure.functions as func
from DatabaseFunction.databaseFunctions import delete_user

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

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

    id = req.params.get('id')
    logging.info(f'id: {id}')

    if not id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            id = req_body.get('id')

    if id: 
        _ = delete_user(container, id)
        return func.HttpResponse(f"{id} Deleted successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a id in the query string or in the request body for a personalized response.",
             status_code=200
        )

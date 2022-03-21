import logging
import os
import azure.functions as func
import json
from DatabaseFunction.databaseFunctions import get_user_by_id, create_container

config = {
    "ENDPOINT": os.environ['COSMOS_URI'],
    "DATABASE_ID": "cape-db",
    "CONTAINER_ID": "user",
    "MASTERKEY": os.environ['COSMOS_PRIMARY_KEY']
}

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        container = create_container(config)
    except Exception as e:
        logging.error(f'Cosmos DB connection error: {e}')
        return func.HttpResponse(f'Cosmos DB connection error: {e}', status_code=500)

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
        response = get_user_by_id(container, id)
        return func.HttpResponse(
            json.dumps({
                "id": response.get('id'),
                "user_name": response.get('user_name'),
                "user_email": response.get('user_email'),
                "user_phone": response.get('user_phone'),
                "user_balance": response.get('user_balance')
            }),
            mimetype='application/json',
            status_code=200
        )
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a id in the query string or in the request body for a personalized response.",
             status_code=200
        )

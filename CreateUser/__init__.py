import logging
import uuid
import azure.functions as func
import os
from DatabaseFunction.databaseFunctions import create_item, create_container

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
    

    # user_name = req.route_params.get('user_name')
    user_name = req.params.get('user_name')
    user_email = req.params.get('user_email')
    user_phone = req.params.get('user_phone')
    user_balance = req.params.get('user_balance')
    logging.info(f'user_name: {user_name}')
    if (not user_name) and (not user_email) and (not user_phone) and (user_balance is None):
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            user_name = req_body.get('user_name')
            user_email = req_body.get('user_email')
            user_phone = req_body.get('user_phone')
            user_balance = req_body.get('user_balance')

    if user_name and user_email and user_phone and user_balance is not None:
        
        new_user = {
            'id': str(uuid.uuid4()),
            'user_name': user_name,
            'user_email': user_email,
            'user_phone': user_phone,
            'user_balance': user_balance
        }
        create_item(container, new_user)
        
        return func.HttpResponse(f"Hello, {user_name}. Your account created successfully.")
    else:
        return func.HttpResponse(
             "Mandatory parameters missing. user_name, user_email, user_phone, user_balance are mandatory.",
             status_code=200
        )

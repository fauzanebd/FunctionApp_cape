import logging
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

def create_container(config):
    try:
        client = cosmos_client.CosmosClient(config['ENDPOINT'], {'masterKey': config['MASTERKEY']})
        db = client.create_database_if_not_exists(id=config['DATABASE_ID'])
        container = db.create_container_if_not_exists(id=config['CONTAINER_ID'], partition_key=PartitionKey(path="/id"))
        
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f'Cosmos DB connection error: {e}')
        raise Exception(f'Cosmos DB connection error: {e}')
    except Exception as e:
        logging.error(f'Unknown error: {e}')
        raise Exception(f'Unknown error: {e}')
        
    return container

def create_item(container, data):
    print('Creating Items')
    print('\n1.1 Create Item\n')

    container.create_item(body=data)

def delete_user(container, user_id):
    response = container.delete_item(
        item=user_id,
        partition_key=user_id
    )
    logging.info(f'Deleted user {user_id}')
    return response

def get_user_by_id(container, user_id):
    response = container.read_item(
        item=user_id,
        partition_key=user_id
    )
    return response

def update_user_by_id(container, user_id, new_data):
    read_item = container.read_item(
        item=user_id,
        partition_key=user_id
    )
    for data in new_data:
        read_item[data] = new_data[data]
    try:
        response = container.replace_item(
            item=read_item,
            body=read_item,
        )
        return response
    except Exception as e:
        logging.error(f'Error updating user: {e}')
        return None
import logging

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
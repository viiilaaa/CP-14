import todoList

# Función delete: Esta funcion borra
def delete(event, context):
    todoList.delete_item(event['pathParameters']['id'])

    # create a response
    response = {
        "statusCode": 200
    }

    return response

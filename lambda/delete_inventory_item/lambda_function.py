import json

import boto3


def lambda_handler(event, context):
    dynamo_client = boto3.client("dynamodb")
    table_name = "Inventory"

    if "pathParameters" not in event or "id" not in event["pathParameters"]:
        return {"statusCode": 400, "body": json.dumps("Missing 'id' path parameter")}

    key_value = event["pathParameters"]["id"]

    # Query using the id
    response = dynamo_client.query(
        TableName=table_name,
        KeyConditionExpression="id = :id",
        ExpressionAttributeValues={":id": {"S": key_value}},
    )

    items = response.get("Items", [])
    if not items:
        return {"statusCode": 404, "body": json.dumps("Item not found")}

    # Get the location id of the item
    location_id_value = items[0]["location_id"]["N"]

    try:
        dynamo_client.delete_item(
            TableName=table_name,
            Key={"id": {"S": key_value}, "location_id": {"N": location_id_value}},
        )
        return {
            "statusCode": 200,
            "body": json.dumps(f"Item with ID {key_value} deleted successfully."),
        }

    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": json.dumps(f"Error deleting item: {str(e)}")}

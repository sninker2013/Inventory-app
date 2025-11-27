import json
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

# Initialize the DynamoDB client
dynamodb = boto3.resource("dynamodb")

# Define the DynamoDB table name and GSI name
TABLE_NAME = "Inventory"
GSI_NAME = "GSI"


def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return (
            int(obj) if obj % 1 == 0 else float(obj)
        )  # Convert to int if whole number, else float
    return obj


def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)

    if "pathParameters" not in event or "location_id" not in event["pathParameters"]:
        return {
            "statusCode": 400,
            "body": json.dumps("Missing 'location id' path parameter"),
        }

    try:
        location_id_value = int(event["pathParameters"]["location_id"])
    except ValueError:
        return {"statusCode": 400, "body": json.dumps("location_id must be a number")}

    # Get the item from the table
    try:
        response = table.query(
            IndexName=GSI_NAME,
            KeyConditionExpression=Key("location_id").eq(location_id_value),
        )
        items = response.get("Items", [])

        items = convert_decimals(items)

        return {"statusCode": 200, "body": json.dumps(items)}
    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": json.dumps(str(e))}

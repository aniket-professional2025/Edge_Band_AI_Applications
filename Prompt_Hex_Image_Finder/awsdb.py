# Importing Required Packages
import boto3
import json
import os
from dotenv import load_dotenv

# Loading Environmental Variables
print("[DEBUG] Loading environment variables...")
load_dotenv()

# Load AWS region and Lambda name
AWS_REGION = os.getenv("AWS_REGION")
LAMBDA_NAME = "db-connection"
print(f"[DEBUG] AWS Region: {AWS_REGION}")
print(f"[DEBUG] Lambda Name: {LAMBDA_NAME}")

# Initialize boto3 Lambda client
print("[DEBUG] Initializing boto3 Lambda client...")
lambda_client = boto3.client("lambda", region_name = AWS_REGION)

# Function to Invoke the Lambda Operation
def invoke_lambda(action: str, params: dict) -> dict:
    """Invoke AWS Lambda with given action and parameters."""
    print(f"[DEBUG] Preparing lambda invocation - Action: {action}")
    # print(f"[DEBUG] Parameters: {json.dumps(params, indent=2)}")
    
    payload = json.dumps({
        "action": action,
        "params": params
    })
    print("[DEBUG] Payload prepared")

    try:
        print("[DEBUG] Invoking Lambda function...")
        response = lambda_client.invoke(
            FunctionName=LAMBDA_NAME,
            InvocationType="RequestResponse",
            Payload=payload.encode("utf-8")
        )
        print("[DEBUG] Lambda invocation successful")
        response_payload = response.get("Payload")
        print("[DEBUG] Raw response payload received")
        result = json.load(response_payload)
        print("[DEBUG] Parsed result")
        return result
    except Exception as e:
        print(f"[ERROR] Failed to invoke lambda: {e}")
        print(f"[DEBUG] Exception details: {str(e)}")
        return {}

# Function to Fetching all Laminates
def fetch_all_laminates():
    """Fetch all laminates from the database via Lambda."""
    print("[DEBUG] Starting fetch_all_laminates function")
    params = {
        "category": None,
        "subcategory": None,
        "page": 1,
        "pageSize": 100,
        "itemType": "Laminates"
    }
    print("[DEBUG] Request parameters")

    result = invoke_lambda("getLaminates", params)
    print("[DEBUG] Lambda invocation result")
    
    laminates = result.get("response", [])
    print(f"[DEBUG] Extracted laminates from response, count: {len(laminates)}")

    print(f"Fetched {len(laminates)} laminates.")
    # for i, lam in enumerate(laminates[:10], start=1):  # Only show first 10 for brevity
    # print(f"{i}. Name: {lam.get('name')} | ID: {lam.get('id')} | Hex: {lam.get('hexcode')}")
    return laminates

# Making Inference 
if __name__ == "__main__":
    print("[DEBUG] Starting main execution")
    result = invoke_lambda("getLaminates", {
        "category": None,
        "subcategory": None,
        "page": 1,
        "pageSize": 100,
        "itemType": "Laminates"
    })

    # Extract laminates from the Lambda response
    laminates = []
    if "body" in result:
        body_data = json.loads(result["body"])
        laminates = body_data.get("laminates", [])

    # Save to laminates.json starting with key "laminates"
    with open("laminates.json", "w", encoding="utf-8") as f:
        json.dump({"laminates": laminates}, f, ensure_ascii=False, indent=2)
        print("Laminates data saved to laminates.json")

    print("[DEBUG] Main execution completed")
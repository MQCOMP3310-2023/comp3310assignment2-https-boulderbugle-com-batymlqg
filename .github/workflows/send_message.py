import requests

import os
print("hello world\n")
print(os.getcwd())

# Read the webhook ID and token from id.txt and token.txt respectively
with open("id.txt", "r") as id_file, open("token.txt", "r") as token_file:
    webhook_id = id_file.read().strip()
    webhook_token = token_file.read().strip()

# Define the message to send
message = "A new push has been made to the repository!"

# Define the payload to send to the webhook
payload = {
    "content": message
}

# Construct the webhook URL
webhook_url = f"https://discord.com/api/webhooks/{webhook_id}/{webhook_token}"

# Send the payload to the webhook URL
response = requests.post(webhook_url, json=payload)

# Print the status code of the response
print(response.status_code)

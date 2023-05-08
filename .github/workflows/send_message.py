import requests

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
try:
    response = requests.post(webhook_url, json=payload)

    # Check the response status code
    if response.status_code == 204:
        print("Message sent successfully!")
    else:
        print(f"Error sending message. Response code: {response.status_code}")
except Exception as e:
    print(f"Error sending message: {e}")


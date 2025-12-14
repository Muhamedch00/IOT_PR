import requests

def trigger_alert():
    url = 'http://127.0.0.1:8000/api/post'
    data = {'temp': 30, 'hum': 50} # Temp 30 > 8, should trigger alert
    
    print(f"Sending POST request to {url} with data {data}...")
    try:
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 201:
            print("✅ Data posted successfully. Check your server console for debug messages!")
        else:
            print("❌ Failed to post data.")
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")

if __name__ == "__main__":
    trigger_alert()

import requests
import sys

def test_api():
    url = "http://localhost:8000/chat"
    message = {"message": "Hello, how are you?"}
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=message)
        if response.status_code == 200:
            print("✅ Success! API Response:")
            print(response.json())
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to localhost:8000. Is the server running?")
        print("Run 'python main.py' in the 'backend' directory first.")

if __name__ == "__main__":
    test_api()
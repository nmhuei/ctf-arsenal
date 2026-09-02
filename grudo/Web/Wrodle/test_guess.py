import requests

URL = "http://10.112.0.12:44574"

def test():
    # Start session
    r = requests.post(f"{URL}/api/start")
    print("Start response status:", r.status_code)
    data = r.json()
    print("Start response data:", data)
    
    token = data.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check state
    r = requests.get(f"{URL}/api/state", headers=headers)
    print("State response:", r.json())
    
    # Make a guess
    guess = "tares"
    r = requests.post(f"{URL}/api/guess", headers=headers, json={"guess": guess})
    print("Guess response:", r.json())

if __name__ == "__main__":
    test()

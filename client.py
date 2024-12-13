import requests
import threading
def make_request():
    url = "http://localhost:8001"
    for _ in range(200):
        print('req sent')
        response = requests.get(url)
        print(f"Response from {url}: {response.status_code}")
# List of URLs to make requests to

# Create and start threads for each URL
threads = []
for _ in range(40):
    thread = threading.Thread(target=make_request)
    thread.start()
    threads.append(thread)
# Wait for all threads to finish
for thread in threads:
    thread.join()

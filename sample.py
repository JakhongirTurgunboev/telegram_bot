import requests
link = 'https://www.instagram.com/reel/C0Y3ra6ItS7/?igshid=MzRlODBiNWFlZA=='

print(requests.get(link).text)
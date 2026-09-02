from bs4 import BeautifulSoup
import requests

url = 'https://himalayas.app/jobs/api'
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, 'html.parser')

print(soup.prettify())

print(soup.find_previous_sibling(class_='\"content-conclusion\"'))
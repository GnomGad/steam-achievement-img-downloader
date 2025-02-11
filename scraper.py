import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import config

os.makedirs(config.SAVE_DIR, exist_ok=True)

response = requests.get(config.URL, headers=config.HEADERS)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'html.parser')

achievements = soup.find_all('div', class_='achieveRow')

for achievement in achievements:
    try:
        img_tag = achievement.find('div', class_='achieveImgHolder').find('img')
        title_tag = achievement.find('div', class_='achieveTxtHolder').find('h3')

        if title_tag:
            title = title_tag.text.strip()
        else:
            continue

        img_url = img_tag['src']
        title = title.replace(" ", "_") + '.jpg'
        title = title.replace(":", "").replace("/", "").replace("\\", "")
        img_path = os.path.join(config.SAVE_DIR, title)

        img_response = requests.get(img_url)
        img_response.raise_for_status()

        img = Image.open(BytesIO(img_response.content))
        img = img.resize(config.IMAGE_SIZE, Image.LANCZOS)
        img.save(img_path, 'JPEG')

        print(f"+ {title}")
    except Exception as e:
        print(f"ERROR {e}")

print("Success")

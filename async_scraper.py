import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import config
from concurrent.futures import ThreadPoolExecutor

os.makedirs(config.SAVE_DIR, exist_ok=True)

async def fetch_page(session):
    async with session.get(config.URL, headers=config.HEADERS) as response:
        return await response.text()

async def fetch_image(session, url):
    async with session.get(url) as response:
        return await response.read()

def process_image(img_data, title):
    try:
        img = Image.open(BytesIO(img_data))
        img = img.resize(config.IMAGE_SIZE, Image.LANCZOS)
        img.save(os.path.join(config.SAVE_DIR, title), 'JPEG')
        print(f"+ {title}")
    except Exception as e:
        print(f"ERROR {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        page_content = await fetch_page(session)
        soup = BeautifulSoup(page_content, 'html.parser')
        achievements = soup.find_all('div', class_='achieveRow')

        tasks = []
        with ThreadPoolExecutor() as executor:
            for achievement in achievements:
                try:
                    img_tag = achievement.find('div', class_='achieveImgHolder').find('img')
                    title_tag = achievement.find('div', class_='achieveTxtHolder').find('h3')

                    if not title_tag:
                        continue

                    title = title_tag.text.strip().replace(" ", "_") + ".jpg"
                    title = title.replace(":", "").replace("/", "").replace("\\", "")
                    img_url = img_tag['src']

                    tasks.append(asyncio.create_task(fetch_image(session, img_url)))
                except Exception as e:
                    print(f"ERROR {e}")

        images_data = await asyncio.gather(*tasks)

        with ThreadPoolExecutor() as executor:
            for img_data, achievement in zip(images_data, achievements):
                title_tag = achievement.find('div', class_='achieveTxtHolder').find('h3')
                title = title_tag.text.strip().replace(" ", "_") + ".jpg"
                title = title.replace(":", "").replace("/", "").replace("\\", "")
                executor.submit(process_image, img_data, title)

asyncio.run(main())
print("Success")

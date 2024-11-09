import asyncio
import aiohttp
from bs4 import BeautifulSoup, Tag, NavigableString
import json
from config_data.config import logger


async def scrape_phrase(url):
    """Асинхронно парсит страницу с итальянскими фразами"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                hr_tag = soup.find("hr", {"class": None, "id": None})
                if not hr_tag:
                    return []

                phrase_list = []
                paragraphs = hr_tag.find_all_next("p")

                for p in paragraphs:
                    span = p.find("span", style=lambda x: x and "font-size:16px" in x)
                    if span:
                        text = span.get_text().strip()
                        logger.info(text)
                        if "—" in text:
                            italian, russian = text.split("—", 1)
                        elif "–" in text:
                            italian, russian = text.split("–", 1)
                        elif " - " in text:
                            italian, russian = text.split(" - ", 1)
                        else:
                            continue
                        logger.info(f'"italian": {italian.strip()}, "russian": {russian.strip()}')
                        phrase_list.append({
                            "italian": italian.strip(),
                            "russian": russian.strip()
                        })

                return phrase_list

    except aiohttp.ClientError as e:
        logger.info(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        logger.info(f"An error occurred: {e}")
        return None


async def main():
    idiom_urls = [
        "https://reallanguage.club/italyanskie-idiomy-so-slovom-laria/",
        "https://reallanguage.club/italyanskie-idiomy-pro-chasti-tela/"
    ]

    all_idioms = []

    async with aiohttp.ClientSession() as session:
        tasks = [scrape_phrase(url) for url in idiom_urls]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result:
                all_idioms.extend(result)

    # Save to JSON file
    with open('../database/italian_idioms.json', 'w', encoding='utf-8') as f:
        json.dump(all_idioms, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(all_idioms)} idioms to italian_idioms.json")


if __name__ == "__main__":
    asyncio.run(main())


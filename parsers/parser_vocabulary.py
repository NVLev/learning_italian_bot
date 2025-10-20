import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json


async def scrape_vocabulary(url):
    """Асинхронно парсит страницу с итальянскими словами"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                rows = soup.select("table tr")
                vocabulary_list = []
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        italian_word = cells[0].text.strip()
                        russian_word = cells[1].text.strip()
                        vocabulary_list.append({"italian": italian_word, "russian": russian_word})
                return vocabulary_list
    except aiohttp.ClientError as e:
        print(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


async def main():
    theme_urls = {
        "Дни недели, месяцы, времена года": "https://reallanguage.club/italyanskie-slova-na-temu-dni-nedeli-mesyacy"
                                            "-vremena-goda/",
        "Семья": "https://reallanguage.club/italyanskie-slova-na-temu-semya/",
        "Одежда": "https://reallanguage.club/italyanskie-slova-na-temu-odezhda/",
        "Цвета": "https://reallanguage.club/italyanskie-slova-na-temu-cveta/",
        "Чувства": "https://reallanguage.club/italyanskie-slova-na-temu-chuvstva/",
        "Части тела": "https://reallanguage.club/italyanskie-slova-na-temu-chasti-tela/",
        "Еда": "https://reallanguage.club/italyanskie-slova-na-temu-eda/",
        "Мясо, птица, морепродукты": "https://reallanguage.club/italyanskie-slova-na-temu-myaso-ptica-moreprodukty/",
        "Приготовление еды": "https://reallanguage.club/italyanskie-slova-na-temu-prigotovlenie-edy/",
        "Посуда и кухонные принадлежности": "https://reallanguage.club/italyanskie-slova-na-temu-posuda-i-kuxonnye"
                                            "-prinadlezhnosti/",
        "Фрукты": "https://reallanguage.club/italyanskie-slova-na-temu-frukty/",
        "Овощи": "https://reallanguage.club/italyanskie-slova-na-temu-ovoshhi/",
        "В ресторане": "https://reallanguage.club/italyanskie-slova-na-temu-v-restorane/",
        "Город": "https://reallanguage.club/italyanskie-slova-na-temu-gorod/",
        "Спальная комната": "https://reallanguage.club/italyanskie-slova-na-temu-spalnaya-komnata",
        "Столовая комната": "https://reallanguage.club/italyanskie-slova-na-temu-stolovaya-komnata/",
        "Кухня": "https://reallanguage.club/italyanskie-slova-na-temu-kuxnya/",
        "Ванная комната": "https://reallanguage.club/italyanskie-slova-na-temu-vannaya-komnata/"
    }

    vocabulary_data = {}
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_vocabulary(url) for url in theme_urls.values()]  # Corrected line
        results = await asyncio.gather(*tasks)
        for i, result in enumerate(results):
            if result:
                vocabulary_data[list(theme_urls.keys())[i]] = result

    # Write to JSON file
    with open("../database/vocabulary.json", "w", encoding="utf-8") as f:
        json.dump(vocabulary_data, f, ensure_ascii=False, indent=4)

    print("Vocabulary data written to vocabulary.json")


if __name__ == "__main__":
    asyncio.run(main())


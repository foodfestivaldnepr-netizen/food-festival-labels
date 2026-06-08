#!/usr/bin/env python3
"""
Generate JPG label files for all 11 Food Festival products.
Layout mirrors build_svg_labels.py exactly — same panel positions,
same font sizes, same proportions.
"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

BASE       = os.path.dirname(__file__)
LOGO_PATH  = os.path.join(BASE, "food festival logo.png")
OUTPUT_DIR = os.path.join(BASE, "output_labels")
ICONS_DIR  = os.path.join(BASE, "icons")

FONT_B = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
FONT_R = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
FONT_I = "/usr/share/fonts/truetype/ubuntu/Ubuntu-RI.ttf"

LW, LH = 1178, 594

# ── product data ──────────────────────────────────────────────────────────────

PRODUCTS = [
    {
        "key": "01_sauce_bbq", "category": "СОУС", "name": "БАРБЕКЮ",
        "weight": "4900", "accent": (100, 0, 18), "accent2": (144, 0, 32),
        "nutrition": {"energy_kj": "775", "energy_kcal": "182", "fat": "0,05",
                      "sat_fat": "0,0", "carbs": "45,0", "sugars": "40,0",
                      "protein": "0,4", "salt": "2,5"},
        "ingredients": (
            "ВОДА ПИТНА, ЦУКОР БІЛИЙ, ТОМАТНА ПАСТА, ЗАГУЩУВАЧ - МОДИФІКОВАНИЙ "
            "КУКУРУДЗЯНИЙ АБО КАРТОПЛЯНИЙ КРОХМАЛЬ, СІЛЬ КУХОННА, РЕГУЛЯТОРИ "
            "КИСЛОТНОСТІ - КИСЛОТА ОЦТОВА ХАРЧОВА, ЛИМОННА КИСЛОТА, КОНСЕРВАНТ - "
            "СОРБАТ КАЛІЮ, БАРВНИК - КАРАМЕЛЬНИЙ КОЛІР, АРОМАТИЗАТОР ДИМУ ГІКОРІ, "
            "СПЕЦІЇ МЕЛЕНІ (ПЕРЕЦЬ ДУХМЯНИЙ МЕЛЕНИЙ, КОРІАНДР, ГВОЗДИКА)."
        ),
        "storage": (
            "ЗА ТЕМПЕРАТУРИ t ВІД 0 °С ДО +24 °С В СУХИХ ВЕНТИЛЬОВАНИХ "
            "ПРИМІЩЕННЯХ З ВІДНОСНОЮ ВОЛОГІСТЮ ПОВІТРЯ НЕ БІЛЬШЕ 75%. ТЕРМІН "
            "ЗБЕРІГАННЯ ПІСЛЯ РОЗКРИТТЯ СПОЖИВЧОЇ ТАРИ ЗА ТЕМПЕРАТУРИ t ВІД "
            "0 °С ДО +11 °С - 14 d(діб) В МЕЖАХ ЗАГАЛЬНОГО СТРОКУ ПРИДАТНОСТІ. "
            "НЕ ДОЗВОЛЕНО ЗБЕРІГАТИ РАЗОМ ІЗ ПРОДУКТАМИ, ЯКІ МАЮТЬ СПЕЦИФІЧНИЙ "
            "ЗАПАХ. НЕ ДОПУСКАТИ ВПЛИВУ ПРЯМИХ СОНЯЧНИХ ПРОМЕНІВ."
        ),
        "address": "ВУЛ. ПАРКОВА, 37/1, СЕЛИЩЕ ВЕЛИКОДОЛИНСЬКЕ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67802, УКРАЇНА, тел.: +38(048)737-65-46.",
        "manufacturer": 'ТОВ "АККАРЖА ПЛЮС", ВУЛ. ШЕВЧЕНКА, 368, СЕЛИЩЕ ОВІДІОПОЛЬ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67801, УКРАЇНА.',
        "commission": 'ТОВ "ФУД ФЕСТИВАЛЬ", ТЕЛЕФОН ДЛЯ СКАРГ ТА ПРОПОЗИЦІЙ +38066-777-99-80.',
        "phone": "",
        "output": "01_sauce_bbq.jpg",
    },
    {
        "key": "02_ketchup_classic_5kg", "category": "КЕТЧУП", "name": "КЛАСИЧНИЙ",
        "sweetener_note": "з цукром та підсолоджувачем",
        "weight": "5000", "accent": (185, 15, 15), "accent2": (235, 65, 25),
        "nutrition": {"energy_kj": "200", "energy_kcal": "47", "fat": "0,1",
                      "sat_fat": "0,0", "carbs": "10,8", "sugars": "4,5",
                      "protein": "0,7", "salt": "2,0"},
        "ingredients": (
            "ВОДА ПИТНА, ТОМАТНА ПАСТА, ЦУКОР БІЛИЙ, ЗАГУЩУВАЧ - МОДИФІКОВАНИЙ "
            "КУКУРУДЗЯНИЙ АБО КАРТОПЛЯНИЙ КРОХМАЛЬ, СІЛЬ КУХОННА, РЕГУЛЯТОРИ "
            "КИСЛОТНОСТІ - КИСЛОТА ОЦТОВА ХАРЧОВА, ЛИМОННА КИСЛОТА, КОНСЕРВАНТ - "
            "БЕНЗОАТ НАТРІЮ, СПЕЦІЇ (МУСКАТНИЙ ГОРІХ, ПЕРЕЦЬ ДУХМЯНИЙ, КОРИЦЯ, "
            "ГВОЗДИКА), ПІДСОЛОДЖУВАЧ."
        ),
        "storage": (
            "ЗА ТЕМПЕРАТУРИ t ВІД 0 °С ДО +24 °С В СУХИХ ВЕНТИЛЬОВАНИХ "
            "ПРИМІЩЕННЯХ З ВІДНОСНОЮ ВОЛОГІСТЮ ПОВІТРЯ НЕ БІЛЬШЕ 75%. ТЕРМІН "
            "ЗБЕРІГАННЯ ПІСЛЯ РОЗКРИТТЯ СПОЖИВЧОЇ ТАРИ ЗА ТЕМПЕРАТУРИ t ВІД "
            "0 °С ДО +11 °С - 14 d(діб) В МЕЖАХ ЗАГАЛЬНОГО СТРОКУ ПРИДАТНОСТІ. "
            "НЕ ДОЗВОЛЕНО ЗБЕРІГАТИ РАЗОМ ІЗ ПРОДУКТАМИ, ЯКІ МАЮТЬ СПЕЦИФІЧНИЙ "
            "ЗАПАХ. НЕ ДОПУСКАТИ ВПЛИВУ ПРЯМИХ СОНЯЧНИХ ПРОМЕНІВ."
        ),
        "address": "ВУЛ. ПАРКОВА, 37/1, СЕЛИЩЕ ВЕЛИКОДОЛИНСЬКЕ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67802, УКРАЇНА, тел.: +38(048)737-65-46.",
        "manufacturer": 'ТОВ "АККАРЖА ПЛЮС", ВУЛ. ШЕВЧЕНКА, 368, СЕЛИЩЕ ОВІДІОПОЛЬ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67801, УКРАЇНА.',
        "commission": 'ТОВ "ФУД ФЕСТИВАЛЬ", ТЕЛЕФОН ДЛЯ СКАРГ ТА ПРОПОЗИЦІЙ +38066-777-99-80.',
        "phone": "",
        "output": "02_ketchup_classic_5kg.jpg",
    },
    {
        "key": "03_mayo_67", "category": "МАЙОНЕЗ", "name": "ПРЕМІУМ",
        "subtitle": "67% жиру",
        "bold_wds": {'СУХИЙ', 'ЯЄЧНИЙ', 'ЖОВТОК', 'СОЇ'},
        "weight": "4900", "accent": (10, 75, 165), "accent2": (25, 150, 220),
        "nutrition": {"energy_kj": "2528", "energy_kcal": "614", "fat": "67,0",
                      "sat_fat": "8,7", "carbs": "3,0", "sugars": "2,5",
                      "protein": "0,3", "salt": "1,0"},
        "ingredients": (
            "ОЛІЯ СОНЯШНИКОВА РАФІНОВАНА ДЕЗОДОРОВАНА, ВОДА ПИТНА, ЦУКОР БІЛИЙ, "
            "СУХИЙ ЯЄЧНИЙ ЖОВТОК, СІЛЬ КУХОННА, ЗАГУЩУВАЧ – МОДИФІКОВАНИЙ "
            "КУКУРУДЗЯНИЙ АБО КАРТОПЛЯНИЙ КРОХМАЛЬ, РЕГУЛЯТОРИ КИСЛОТНОСТІ – "
            "КИСЛОТА ОЦТОВА ХАРЧОВА ТА КИСЛОТА ЛИМОННА, СТАБІЛІЗАТОРИ – ГУАРОВА "
            "ТА КСАНТАНОВА КАМЕДІ, КОНСЕРВАНТ – СОРБАТ КАЛІЮ, АРОМАТИЗАТОР "
            "«ГІРЧИЦЯ», АНТИОКСИДАНТ - КАЛЬЦІЮ ДИНАТРІЮ ЕДТА, БАРВНИК ХАРЧОВИЙ - "
            "БЕТА-КАРОТИН. ПРОДУКТ МОЖЕ МІСТИТИ СЛІДИ СОЇ."
        ),
        "storage": (
            "ЗА ТЕМПЕРАТУРИ t ВІД 0 °С ДО +24 °С В СУХИХ ВЕНТИЛЬОВАНИХ "
            "ПРИМІЩЕННЯХ З ВІДНОСНОЮ ВОЛОГІСТЮ ПОВІТРЯ НЕ БІЛЬШЕ 75%. ТЕРМІН "
            "ЗБЕРІГАННЯ ПІСЛЯ РОЗКРИТТЯ СПОЖИВЧОЇ ТАРИ ЗА ТЕМПЕРАТУРИ t ВІД "
            "0 °С ДО +11 °С - 14 d(діб). НЕ ДОЗВОЛЕНО ЗБЕРІГАТИ РАЗОМ ІЗ "
            "ПРОДУКТАМИ, ЯКІ МАЮТЬ СПЕЦИФІЧНИЙ ЗАПАХ. НЕ ДОПУСКАТИ ВПЛИВУ "
            "ПРЯМИХ СОНЯЧНИХ ПРОМЕНІВ."
        ),
        "address": "ВУЛ. ПАРКОВА, 37/1, СЕЛИЩЕ ВЕЛИКОДОЛИНСЬКЕ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67882, УКРАЇНА, тел.: +38(048)737-65-46.",
        "manufacturer": 'ТОВ "АККАРЖА ПЛЮС", ВУЛ. ШЕВЧЕНКА, 368, СЕЛИЩЕ ОВІДІОПОЛЬ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67801, УКРАЇНА.',
        "commission": 'ТОВ "ФУД ФЕСТИВАЛЬ", ТЕЛЕФОН ДЛЯ СКАРГ ТА ПРОПОЗИЦІЙ +38066-777-99-80.',
        "phone": "",
        "output": "03_mayo_67.jpg",
    },
    {
        "key": "04_mayo_real", "category": "МАЙОНЕЗНИЙ СОУС", "name": "РЕАЛ",
        "subtitle": "30% жирності",
        "bold_wds": {'СОЇ'},
        "weight": "4900", "accent": (100, 175, 30), "accent2": (173, 255, 47),
        "nutrition": {"energy_kj": "1236", "energy_kcal": "300", "fat": "30,0",
                      "sat_fat": "3,9", "carbs": "7,4", "sugars": "3,6",
                      "protein": "0,05", "salt": "1,3"},
        "ingredients": (
            "ВОДА ПИТНА, ОЛІЯ СОНЯШНИКОВА РАФІНОВАНА ДЕЗОДОРОВАНА, ЗАГУЩУВАЧ – "
            "МОДИФІКОВАНИЙ КУКУРУДЗЯНИЙ АБО КАРТОПЛЯНИЙ КРОХМАЛЬ, ЦУКОР БІЛИЙ, "
            "СІЛЬ КУХОННА, ЕМУЛЬГАТОР – МОДИФІКОВАНИЙ КУКУРУДЗЯНИЙ АБО "
            "КАРТОПЛЯНИЙ КРОХМАЛЬ, РЕГУЛЯТОРИ КИСЛОТНОСТІ – КИСЛОТА ОЦТОВА "
            "ХАРЧОВА, ЛИМОННА КИСЛОТА, СТАБІЛІЗАТОРИ – ГУАРОВА ТА КСАНТАНОВА "
            "КАМЕДІ, КОНСЕРВАНТ – СОРБАТ КАЛІЮ, АРОМАТИЗАТОР «ГІРЧИЦЯ», "
            "АНТИОКСИДАНТ - КАЛЬЦІЮ ДИНАТРІЮ EDTA, БАРВНИК ХАРЧОВИЙ - "
            "БЕТА-КАРОТИН. ПРОДУКТ МОЖЕ МІСТИТИ СЛІДИ СОЇ."
        ),
        "storage": (
            "ЗА ТЕМПЕРАТУРИ t ВІД 0 °С ДО +24 °С В СУХИХ ВЕНТИЛЬОВАНИХ "
            "ПРИМІЩЕННЯХ З ВІДНОСНОЮ ВОЛОГІСТЮ ПОВІТРЯ НЕ БІЛЬШЕ 75%. ТЕРМІН "
            "ЗБЕРІГАННЯ ПІСЛЯ РОЗКРИТТЯ СПОЖИВЧОЇ ТАРИ ЗА ТЕМПЕРАТУРИ t ВІД "
            "0 °С ДО +11 °С - 14 d(діб) В МЕЖАХ ЗАГАЛЬНОГО СТРОКУ ПРИДАТНОСТІ. "
            "НЕ ДОЗВОЛЕНО ЗБЕРІГАТИ РАЗОМ ІЗ ПРОДУКТАМИ, ЯКІ МАЮТЬ СПЕЦИФІЧНИЙ "
            "ЗАПАХ. НЕ ДОПУСКАТИ ВПЛИВУ ПРЯМИХ СОНЯЧНИХ ПРОМЕНІВ."
        ),
        "address": "ВУЛ. ПАРКОВА, 37/1, СЕЛИЩЕ ВЕЛИКОДОЛИНСЬКЕ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67802, УКРАЇНА, тел.: +38(048)737-65-46.",
        "manufacturer": 'ТОВ "АККАРЖА ПЛЮС", ВУЛ. ШЕВЧЕНКА, 368, СЕЛИЩЕ ОВІДІОПОЛЬ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67801, УКРАЇНА.',
        "commission": 'ТОВ "ФУД ФЕСТИВАЛЬ", ТЕЛЕФОН ДЛЯ СКАРГ ТА ПРОПОЗИЦІЙ +38066-777-99-80.',
        "phone": "",
        "output": "04_mayo_real.jpg",
    },
    {
        "key": "05_tomato_pasta", "category": "ПАСТА", "name": "ТОМАТНА 25%",
        "weight": "5000", "accent": (227, 38, 54), "accent2": (0, 146, 70),
        "nutrition": {"energy_kj": "337", "energy_kcal": "79", "fat": "0,0",
                      "sat_fat": "0,0", "carbs": "15,8", "sugars": "1,3",
                      "protein": "4,0", "salt": "1,5"},
        "ingredients": (
            "ТОМАТНА ПАСТА, СІЛЬ КУХОННА, КОНСЕРВАНТ (БЕНЗОАТ НАТРІЮ). "
            "МАСОВА ЧАСТКА РОЗЧИННИХ СУХИХ РЕЧОВИН 25%."
        ),
        "storage": (
            "ЗА ТЕМПЕРАТУРИ t ВІД 0 °С ДО +24 °С В СУХИХ ВЕНТИЛЬОВАНИХ "
            "ПРИМІЩЕННЯХ З ВІДНОСНОЮ ВОЛОГІСТЮ ПОВІТРЯ НЕ БІЛЬШЕ 75%. ТЕРМІН "
            "ЗБЕРІГАННЯ ПІСЛЯ РОЗКРИТТЯ СПОЖИВЧОЇ ТАРИ ЗА ТЕМПЕРАТУРИ t ВІД "
            "0 °С ДО +11 °С - 14 d(діб) В МЕЖАХ ЗАГАЛЬНОГО СТРОКУ ПРИДАТНОСТІ. "
            "НЕ ДОЗВОЛЕНО ЗБЕРІГАТИ РАЗОМ ІЗ ПРОДУКТАМИ, ЯКІ МАЮТЬ СПЕЦИФІЧНИЙ "
            "ЗАПАХ. НЕ ДОПУСКАТИ ВПЛИВУ ПРЯМИХ СОНЯЧНИХ ПРОМЕНІВ."
        ),
        "address": "ВУЛ. ПАРКОВА, 37/1, СЕЛИЩЕ ВЕЛИКОДОЛИНСЬКЕ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67802, УКРАЇНА, тел.: +38(048)737-65-46.",
        "manufacturer": 'ТОВ "АККАРЖА ПЛЮС", ВУЛ. ШЕВЧЕНКА, 368, СЕЛИЩЕ ОВІДІОПОЛЬ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67801, УКРАЇНА.',
        "commission": 'ТОВ "ФУД ФЕСТИВАЛЬ", ТЕЛЕФОН ДЛЯ СКАРГ ТА ПРОПОЗИЦІЙ +38066-777-99-80.',
        "phone": "",
        "output": "05_tomato_pasta.jpg",
    },
    {
        "key": "06_ketchup_premium", "category": "КЕТЧУП", "name": "ПРЕМІУМ",
        "weight": "5000", "accent": (200, 20, 40), "accent2": (212, 175, 55),
        "bg_dark": (0, 0, 0), "border": (212, 175, 55),
        "name_color": (212, 175, 55), "logo_color": (212, 175, 55),
        "nutrition": {"energy_kj": "348", "energy_kcal": "82", "fat": "0,1",
                      "sat_fat": "0,0", "carbs": "19,1", "sugars": "12,7",
                      "protein": "1,1", "salt": "2,6"},
        "ingredients": (
            "ВОДА ПИТНА, ТОМАТНА ПАСТА, ЦУКОР БІЛИЙ, ЗАГУЩУВАЧ - МОДИФІКОВАНИЙ "
            "КУКУРУДЗЯНИЙ АБО КАРТОПЛЯНИЙ КРОХМАЛЬ, СІЛЬ КУХОННА, РЕГУЛЯТОРИ "
            "КИСЛОТНОСТІ - КИСЛОТА ОЦТОВА ХАРЧОВА, ЛИМОННА КИСЛОТА, КОНСЕРВАНТ - "
            "БЕНЗОАТ НАТРІЮ, СПЕЦІЇ МЕЛЕНІ (ГВОЗДИКА, КОРИЦЯ, ПЕРЕЦЬ ДУХМЯНИЙ "
            "МЕЛЕНИЙ)."
        ),
        "storage": (
            "ЗА ТЕМПЕРАТУРИ t ВІД 0 °С ДО +24 °С В СУХИХ ВЕНТИЛЬОВАНИХ "
            "ПРИМІЩЕННЯХ З ВІДНОСНОЮ ВОЛОГІСТЮ ПОВІТРЯ НЕ БІЛЬШЕ 75%. ТЕРМІН "
            "ЗБЕРІГАННЯ ПІСЛЯ РОЗКРИТТЯ СПОЖИВЧОЇ ТАРИ ЗА ТЕМПЕРАТУРИ t ВІД "
            "0 °С ДО +11 °С - 14 d(діб) В МЕЖАХ ЗАГАЛЬНОГО СТРОКУ ПРИДАТНОСТІ. "
            "НЕ ДОЗВОЛЕНО ЗБЕРІГАТИ РАЗОМ ІЗ ПРОДУКТАМИ, ЯКІ МАЮТЬ СПЕЦИФІЧНИЙ "
            "ЗАПАХ. НЕ ДОПУСКАТИ ВПЛИВУ ПРЯМИХ СОНЯЧНИХ ПРОМЕНІВ."
        ),
        "address": "ВУЛ. ПАРКОВА, 37/1, СЕЛИЩЕ ВЕЛИКОДОЛИНСЬКЕ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67802, УКРАЇНА, тел.: +38(048)737-65-46.",
        "manufacturer": 'ТОВ "АККАРЖА ПЛЮС", ВУЛ. ШЕВЧЕНКА, 368, СЕЛИЩЕ ОВІДІОПОЛЬ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67801, УКРАЇНА.',
        "commission": 'ТОВ "ФУД ФЕСТИВАЛЬ", ТЕЛЕФОН ДЛЯ СКАРГ ТА ПРОПОЗИЦІЙ +38066-777-99-80.',
        "phone": "",
        "output": "06_ketchup_premium.jpg",
    },
    {
        "key": "07_ketchup_shashlik_830", "category": "КЕТЧУП", "name": "ШАШЛИЧНИЙ",
        "sweetener_note": "з цукром та підсолоджувачем",
        "weight": "830", "accent": (145, 18, 75), "accent2": (215, 55, 125),
        "nutrition": {"energy_kj": "200", "energy_kcal": "47", "fat": "0,1",
                      "sat_fat": "0,0", "carbs": "10,8", "sugars": "4,5",
                      "protein": "0,7", "salt": "2,0"},
        "ingredients": (
            "ВОДА ПИТНА, ТОМАТНА ПАСТА, ЦУКОР БІЛИЙ, ЗАГУЩУВАЧ - МОДИФІКОВАНИЙ "
            "КУКУРУДЗЯНИЙ АБО КАРТОПЛЯНИЙ КРОХМАЛЬ, СІЛЬ КУХОННА, РЕГУЛЯТОРИ "
            "КИСЛОТНОСТІ - КИСЛОТА ОЦТОВА ХАРЧОВА, ЛИМОННА КИСЛОТА, КОНСЕРВАНТ - "
            "БЕНЗОАТ НАТРІЮ, СПЕЦІЇ МЕЛЕНІ (КОРІАНДР, ЗІРА, МУСКАТНИЙ ГОРІХ, "
            "ПЕРЕЦЬ ЧИЛІ), ПІДСОЛОДЖУВАЧ."
        ),
        "storage": (
            "ЗА ТЕМПЕРАТУРИ t ВІД 0 °С ДО +24 °С В СУХИХ ВЕНТИЛЬОВАНИХ "
            "ПРИМІЩЕННЯХ З ВІДНОСНОЮ ВОЛОГІСТЮ ПОВІТРЯ НЕ БІЛЬШЕ 75%. ТЕРМІН "
            "ЗБЕРІГАННЯ ПІСЛЯ РОЗКРИТТЯ СПОЖИВЧОЇ ТАРИ ЗА ТЕМПЕРАТУРИ t ВІД "
            "0 °С ДО +11 °С - 14 d(діб) В МЕЖАХ ЗАГАЛЬНОГО СТРОКУ ПРИДАТНОСТІ. "
            "НЕ ДОЗВОЛЕНО ЗБЕРІГАТИ РАЗОМ ІЗ ПРОДУКТАМИ, ЯКІ МАЮТЬ СПЕЦИФІЧНИЙ "
            "ЗАПАХ. НЕ ДОПУСКАТИ ВПЛИВУ ПРЯМИХ СОНЯЧНИХ ПРОМЕНІВ."
        ),
        "address": "ВУЛ. ПАРКОВА, 37/1, СЕЛИЩЕ ВЕЛИКОДОЛИНСЬКЕ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67802, УКРАЇНА, тел.: +38(048)737-65-46.",
        "manufacturer": 'ТОВ "АККАРЖА ПЛЮС", ВУЛ. ШЕВЧЕНКА, 368, СЕЛИЩЕ ОВІДІОПОЛЬ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67801, УКРАЇНА.',
        "commission": 'ТОВ "ФУД ФЕСТИВАЛЬ", ТЕЛЕФОН ДЛЯ СКАРГ ТА ПРОПОЗИЦІЙ +38066-777-99-80.',
        "phone": "",
        "output": "07_ketchup_shashlik_830.jpg",
    },
    {
        "key": "08_ketchup_shashlik_5kg", "category": "КЕТЧУП", "name": "ШАШЛИЧНИЙ",
        "sweetener_note": "з цукром та підсолоджувачем",
        "weight": "5000", "accent": (145, 18, 75), "accent2": (215, 55, 125),
        "nutrition": {"energy_kj": "200", "energy_kcal": "47", "fat": "0,1",
                      "sat_fat": "0,0", "carbs": "10,8", "sugars": "4,5",
                      "protein": "0,7", "salt": "2,0"},
        "ingredients": (
            "ВОДА ПИТНА, ТОМАТНА ПАСТА, ЦУКОР БІЛИЙ, ЗАГУЩУВАЧ - МОДИФІКОВАНИЙ "
            "КУКУРУДЗЯНИЙ АБО КАРТОПЛЯНИЙ КРОХМАЛЬ, СІЛЬ КУХОННА, РЕГУЛЯТОРИ "
            "КИСЛОТНОСТІ - КИСЛОТА ОЦТОВА ХАРЧОВА, ЛИМОННА КИСЛОТА, КОНСЕРВАНТ - "
            "БЕНЗОАТ НАТРІЮ, СПЕЦІЇ МЕЛЕНІ (КОРІАНДР, ЗІРА, МУСКАТНИЙ ГОРІХ, "
            "ПЕРЕЦЬ ЧИЛІ), ПІДСОЛОДЖУВАЧ."
        ),
        "storage": (
            "ЗА ТЕМПЕРАТУРИ t ВІД 0 °С ДО +24 °С В СУХИХ ВЕНТИЛЬОВАНИХ "
            "ПРИМІЩЕННЯХ З ВІДНОСНОЮ ВОЛОГІСТЮ ПОВІТРЯ НЕ БІЛЬШЕ 75%. ТЕРМІН "
            "ЗБЕРІГАННЯ ПІСЛЯ РОЗКРИТТЯ СПОЖИВЧОЇ ТАРИ ЗА ТЕМПЕРАТУРИ t ВІД "
            "0 °С ДО +11 °С - 14 d(діб) В МЕЖАХ ЗАГАЛЬНОГО СТРОКУ ПРИДАТНОСТІ. "
            "НЕ ДОЗВОЛЕНО ЗБЕРІГАТИ РАЗОМ ІЗ ПРОДУКТАМИ, ЯКІ МАЮТЬ СПЕЦИФІЧНИЙ "
            "ЗАПАХ. НЕ ДОПУСКАТИ ВПЛИВУ ПРЯМИХ СОНЯЧНИХ ПРОМЕНІВ."
        ),
        "address": "ВУЛ. ПАРКОВА, 37/1, СЕЛИЩЕ ВЕЛИКОДОЛИНСЬКЕ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67802, УКРАЇНА, тел.: +38(048)737-65-46.",
        "manufacturer": 'ТОВ "АККАРЖА ПЛЮС", ВУЛ. ШЕВЧЕНКА, 368, СЕЛИЩЕ ОВІДІОПОЛЬ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67801, УКРАЇНА.',
        "commission": 'ТОВ "ФУД ФЕСТИВАЛЬ", ТЕЛЕФОН ДЛЯ СКАРГ ТА ПРОПОЗИЦІЙ +38066-777-99-80.',
        "phone": "",
        "output": "08_ketchup_shashlik_5kg.jpg",
    },
    {
        "key": "09_sauce_cheese", "category": "СОУС", "name": "СИРНИЙ",
        "bold_wds": {'СИРНИЙ', 'ПОРОШОК', '(МОЛОКО', 'ДЛЯ', 'СИРУ', '(МІСТИТЬ', 'МОЛОЧНІ', 'ПРОДУКТИ', 'ЛАКТОЗУ))'},
        "weight": "830", "accent": (215, 205, 0), "accent2": (255, 255, 0),
        "nutrition": {"energy_kj": "1587", "energy_kcal": "385", "fat": "40,0",
                      "sat_fat": "5,2", "carbs": "6,3", "sugars": "3,8",
                      "protein": "0,03", "salt": "1,4"},
        "ingredients": (
            "ВОДА ПИТНА, ОЛІЯ СОНЯШНИКОВА РАФІНОВАНА ДЕЗОДОРОВАНА, ЦУКОР БІЛИЙ, "
            "ЗАГУЩУВАЧ - МОДИФІКОВАНИЙ КУКУРУДЗЯНИЙ АБО КАРТОПЛЯНИЙ КРОХМАЛЬ, "
            "СІЛЬ КУХОННА, ЕМУЛЬГАТОР - МОДИФІКОВАНИЙ КУКУРУДЗЯНИЙ АБО "
            "КАРТОПЛЯНИЙ КРОХМАЛЬ, СИРНИЙ ПОРОШОК (0,5%) (МОЛОКО, СІЛЬ, ФЕРМЕНТ "
            "МІКРОБІОЛОГІЧНОГО ПОХОДЖЕННЯ, БАКТЕРІАЛЬНА ЗАКВАСКА ДЛЯ СИРУ ТИПУ "
            "ЧЕДДЕР) (МІСТИТЬ МОЛОЧНІ ПРОДУКТИ ТА ЛАКТОЗУ)), РЕГУЛЯТОРИ "
            "КИСЛОТНОСТІ - КИСЛОТА ОЦТОВА ХАРЧОВА, ЛИМОННА КИСЛОТА, "
            "СТАБІЛІЗАТОРИ - КСАНТАНОВА ТА ГУАРОВА КАМЕДІ, КОНСЕРВАНТ - СОРБАТ "
            'КАЛІЮ, БАРВНИК - БЕТА-КАРОТИН, АРОМАТИЗАТОР "СИР".'
        ),
        "storage": (
            "ЗА ТЕМПЕРАТУРИ t ВІД 0 °С ДО +24 °С В СУХИХ ВЕНТИЛЬОВАНИХ "
            "ПРИМІЩЕННЯХ З ВІДНОСНОЮ ВОЛОГІСТЮ ПОВІТРЯ НЕ БІЛЬШЕ 75%. ТЕРМІН "
            "ЗБЕРІГАННЯ ПІСЛЯ РОЗКРИТТЯ СПОЖИВЧОЇ ТАРИ ЗА ТЕМПЕРАТУРИ t ВІД "
            "0 °С ДО +11 °С - 14 d(діб) В МЕЖАХ ЗАГАЛЬНОГО СТРОКУ ПРИДАТНОСТІ. "
            "НЕ ДОЗВОЛЕНО ЗБЕРІГАТИ РАЗОМ ІЗ ПРОДУКТАМИ, ЯКІ МАЮТЬ СПЕЦИФІЧНИЙ "
            "ЗАПАХ. НЕ ДОПУСКАТИ ВПЛИВУ ПРЯМИХ СОНЯЧНИХ ПРОМЕНІВ."
        ),
        "address": "ВУЛ. ПАРКОВА, 37/1, СЕЛИЩЕ ВЕЛИКОДОЛИНСЬКЕ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67802, УКРАЇНА, тел.: +38(048)737-65-46.",
        "manufacturer": 'ТОВ "АККАРЖА ПЛЮС", ВУЛ. ШЕВЧЕНКА, 368, СЕЛИЩЕ ОВІДІОПОЛЬ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67801, УКРАЇНА.',
        "commission": 'ТОВ "ФУД ФЕСТИВАЛЬ", ТЕЛЕФОН ДЛЯ СКАРГ ТА ПРОПОЗИЦІЙ +38066-777-99-80.',
        "phone": "",
        "output": "09_sauce_cheese.jpg",
    },
    {
        "key": "10_mustard_american", "category": "ГІРЧИЦЯ", "name": "АМЕРИКАНСЬКА",
        "bold_wds": {'ПОРОШОК', 'ГІРЧИЦІ', 'БІЛОЇ'},
        "weight": "830", "accent": (162, 102, 0), "accent2": (228, 182, 28),
        "nutrition": {"energy_kj": "733", "energy_kcal": "174", "fat": "6,1",
                      "sat_fat": "0,5", "carbs": "22,5", "sugars": "17,0",
                      "protein": "7,3", "salt": "2,0"},
        "ingredients": (
            "ВОДА ПИТНА, ПОРОШОК ГІРЧИЦІ БІЛОЇ (17%), ЦУКОР БІЛИЙ, ОЛІЯ "
            "РОСЛИННА, СІЛЬ КУХОННА, РЕГУЛЯТОР КИСЛОТНОСТІ - КИСЛОТА ОЦТОВА "
            "ХАРЧОВА, СТАБІЛІЗАТОРИ – КСАНТАНОВА ТА ГУАРОВА КАМЕДІ, ПРЯНОЩІ "
            "СУШЕНІ МЕЛЕНІ (КУРКУМА, КОРІАНДР), КОНСЕРВАНТ – БЕНЗОАТ НАТРІЮ."
        ),
        "storage": (
            "ЗА ТЕМПЕРАТУРИ t ВІД 0 °С ДО +24 °С В СУХИХ ВЕНТИЛЬОВАНИХ "
            "ПРИМІЩЕННЯХ З ВІДНОСНОЮ ВОЛОГІСТЮ ПОВІТРЯ НЕ БІЛЬШЕ 75%. ТЕРМІН "
            "ЗБЕРІГАННЯ ПІСЛЯ РОЗКРИТТЯ СПОЖИВЧОЇ ТАРИ ЗА ТЕМПЕРАТУРИ t ВІД "
            "0 °С ДО +11 °С - 14 d(діб) В МЕЖАХ ЗАГАЛЬНОГО СТРОКУ ПРИДАТНОСТІ. "
            "НЕ ДОЗВОЛЕНО ЗБЕРІГАТИ РАЗОМ ІЗ ПРОДУКТАМИ, ЯКІ МАЮТЬ СПЕЦИФІЧНИЙ "
            "ЗАПАХ. НЕ ДОПУСКАТИ ВПЛИВУ ПРЯМИХ СОНЯЧНИХ ПРОМЕНІВ."
        ),
        "address": "ВУЛ. ПАРКОВА, 37/1, СЕЛИЩЕ ВЕЛИКОДОЛИНСЬКЕ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67802, УКРАЇНА, тел.: +38(048)737-65-46.",
        "manufacturer": 'ТОВ "АККАРЖА ПЛЮС", ВУЛ. ШЕВЧЕНКА, 368, СЕЛИЩЕ ОВІДІОПОЛЬ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67801, УКРАЇНА.',
        "commission": 'ТОВ "ФУД ФЕСТИВАЛЬ", ТЕЛЕФОН ДЛЯ СКАРГ ТА ПРОПОЗИЦІЙ +38066-777-99-80.',
        "phone": "",
        "output": "10_mustard_american.jpg",
    },
    {
        "key": "11_ketchup_classic_830", "category": "КЕТЧУП", "name": "КЛАСИЧНИЙ",
        "sweetener_note": "з цукром та підсолоджувачем",
        "weight": "830", "accent": (185, 15, 15), "accent2": (235, 65, 25),
        "nutrition": {"energy_kj": "200", "energy_kcal": "47", "fat": "0,1",
                      "sat_fat": "0,0", "carbs": "10,8", "sugars": "4,5",
                      "protein": "0,7", "salt": "2,0"},
        "ingredients": (
            "ВОДА ПИТНА, ТОМАТНА ПАСТА, ЦУКОР БІЛИЙ, ЗАГУЩУВАЧ - МОДИФІКОВАНИЙ "
            "КУКУРУДЗЯНИЙ АБО КАРТОПЛЯНИЙ КРОХМАЛЬ, СІЛЬ КУХОННА, РЕГУЛЯТОРИ "
            "КИСЛОТНОСТІ - КИСЛОТА ОЦТОВА ХАРЧОВА, ЛИМОННА КИСЛОТА, КОНСЕРВАНТ - "
            "БЕНЗОАТ НАТРІЮ, СПЕЦІЇ (МУСКАТНИЙ ГОРІХ, ПЕРЕЦЬ ДУХМЯНИЙ, КОРИЦЯ, "
            "ГВОЗДИКА), ПІДСОЛОДЖУВАЧ."
        ),
        "storage": (
            "ЗА ТЕМПЕРАТУРИ t ВІД 0 °С ДО +24 °С В СУХИХ ВЕНТИЛЬОВАНИХ "
            "ПРИМІЩЕННЯХ З ВІДНОСНОЮ ВОЛОГІСТЮ ПОВІТРЯ НЕ БІЛЬШЕ 75%. ТЕРМІН "
            "ЗБЕРІГАННЯ ПІСЛЯ РОЗКРИТТЯ СПОЖИВЧОЇ ТАРИ ЗА ТЕМПЕРАТУРИ t ВІД "
            "0 °С ДО +11 °С - 14 d(діб) В МЕЖАХ ЗАГАЛЬНОГО СТРОКУ ПРИДАТНОСТІ. "
            "НЕ ДОЗВОЛЕНО ЗБЕРІГАТИ РАЗОМ ІЗ ПРОДУКТАМИ, ЯКІ МАЮТЬ СПЕЦИФІЧНИЙ "
            "ЗАПАХ. НЕ ДОПУСКАТИ ВПЛИВУ ПРЯМИХ СОНЯЧНИХ ПРОМЕНІВ."
        ),
        "address": "ВУЛ. ПАРКОВА, 37/1, СЕЛИЩЕ ВЕЛИКОДОЛИНСЬКЕ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67802, УКРАЇНА, тел.: +38(048)737-65-46.",
        "manufacturer": 'ТОВ "АККАРЖА ПЛЮС", ВУЛ. ШЕВЧЕНКА, 368, СЕЛИЩЕ ОВІДІОПОЛЬ, ОДЕСЬКИЙ РАЙОН, ОДЕСЬКА ОБЛАСТЬ, 67801, УКРАЇНА.',
        "commission": 'ТОВ "ФУД ФЕСТИВАЛЬ", ТЕЛЕФОН ДЛЯ СКАРГ ТА ПРОПОЗИЦІЙ +38066-777-99-80.',
        "phone": "",
        "output": "11_ketchup_classic_830.jpg",
    },
]

# ── logo helpers (also imported by build_svg_labels.py) ───────────────────────

def load_logo_white(logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    arr  = np.array(logo)
    white = (arr[:, :, 0] > 230) & (arr[:, :, 1] > 230) & (arr[:, :, 2] > 230)
    arr[white,  3]    = 0
    arr[~white, :3]   = 255
    return Image.fromarray(arr, "RGBA")

# ── icon helpers ─────────────────────────────────────────────────────────────

_icon_cache: dict = {}

def load_icon(filename, target_h=62):
    key = (filename, target_h)
    if key in _icon_cache:
        return _icon_cache[key]
    path = os.path.join(ICONS_DIR, filename)
    img  = Image.open(path).convert("RGBA")
    arr  = np.array(img)
    white = (arr[:, :, 0] > 215) & (arr[:, :, 1] > 215) & (arr[:, :, 2] > 215)
    arr[white,   3]  = 0      # white bg → transparent
    arr[~white, :3]  = 255    # dark content → white
    img  = Image.fromarray(arr, "RGBA")
    ow, oh = img.size
    result = img.resize((round(ow / oh * target_h), target_h), Image.LANCZOS)
    _icon_cache[key] = result
    return result

def _default_icons(weight_str):
    if int(weight_str) >= 4000:
        return ["icon_foodsafe.png", "icon_trash.jpeg", "icon_pp05.png", "icon_bez_gmo.png"]
    return ["icon_foodsafe.png", "icon_trash.jpeg", "icon_pet01.png", "icon_hdpe02.png",
            "icon_bez_gmo.png"]

def draw_icons(base, icon_files):
    if not icon_files:
        return
    n        = len(icon_files)
    target_h = 52 if n >= 5 else 62
    spacing  = 7  if n >= 5 else 10
    icons    = [load_icon(f, target_h) for f in icon_files]
    ax1, ax2 = 185, 510
    ay1, ay2 = 492, 582
    total_w  = sum(ic.width for ic in icons) + spacing * (n - 1)
    x = ax1 + (ax2 - ax1 - total_w) // 2
    y = ay1 + (ay2 - ay1 - target_h) // 2
    for ic in icons:
        base.paste(ic, (x, y), ic)
        x += ic.width + spacing

# ── font / text helpers ───────────────────────────────────────────────────────

_font_cache: dict = {}

def _pf(path, size):
    k = (path, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, size)
    return _font_cache[k]

def tw(text, path, size):
    return int(_pf(path, size).getlength(text))

def wrap(text, path, size, max_w):
    font  = _pf(path, size)
    words = text.split()
    lines, line = [], ""
    for word in words:
        cand = f"{line} {word}".strip() if line else word
        if font.getlength(cand) <= max_w:
            line = cand
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

# ── background ────────────────────────────────────────────────────────────────

def make_background(p):
    a   = p["accent"]
    a2  = p["accent2"]
    bd  = p.get("bg_dark")
    br  = p.get("border")
    bar = br if br else a

    if bd:
        base   = Image.new("RGBA", (LW, LH), (*bd, 255))
        alphas = np.linspace(199, 0, LW).astype(np.uint8)
    else:
        dark   = tuple(int(c * 0.25) for c in a)
        base   = Image.new("RGBA", (LW, LH), (*dark, 255))
        alphas = np.linspace(150, 20, LW).astype(np.uint8)

    grad            = np.zeros((LH, LW, 4), dtype=np.uint8)
    grad[:, :, :3]  = a
    grad[:, :,  3]  = alphas
    base = Image.alpha_composite(base, Image.fromarray(grad, "RGBA"))

    deco = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    d    = ImageDraw.Draw(deco)
    d.rectangle([0, 0,      6,  LH],   fill=(*bar, 255))
    d.rectangle([0, 0,      LW, 8],    fill=(*bar, 255))
    d.rectangle([0, LH - 8, LW, LH],  fill=(*bar, 255))
    d.rectangle([5, 15,     LW, 17],  fill=(*a2,  150))
    d.polygon([(549, 0), (629, 0), (579, LH), (499, LH)], fill=(*a2, 13))
    d.line([(722, 12), (722, LH - 12)], fill=(*a2, 102), width=1)
    return Image.alpha_composite(base, deco)

# ── left panel ────────────────────────────────────────────────────────────────

def draw_left_panel(draw, p, a2):
    cx = 14 + 244   # = 258, centre of left panel
    pw = 476        # wrap width
    y  = 18

    def hdr(text, fs=14, gap_before=7):
        nonlocal y
        y += gap_before
        w = tw(text, FONT_B, fs)
        draw.text((cx - w // 2, y), text, font=_pf(FONT_B, fs), fill=a2)
        y += fs + 3

    def body(text, fs=11, lh=None, alpha=255, bold_wds=None, italic_wds=None):
        nonlocal y
        if lh is None:
            lh = round(fs * 1.35)
        col    = (255, 255, 255, alpha)
        font_r = _pf(FONT_R, fs)
        if bold_wds is None and italic_wds is None:
            for line in wrap(text, FONT_R, fs, pw):
                w = tw(line, FONT_R, fs)
                draw.text((cx - w // 2, y), line, font=font_r, fill=col)
                y += lh
        else:
            font_b = _pf(FONT_B, fs) if bold_wds   else font_r
            font_i = _pf(FONT_I, fs) if italic_wds else font_r
            sp_w   = font_r.getlength(' ')
            for line in wrap(text, FONT_R, fs, pw):
                words     = line.split()
                word_data = []
                for wd in words:
                    clean = wd.rstrip('.,;:')
                    if bold_wds and clean in bold_wds:
                        word_data.append((wd, font_b))
                    elif italic_wds and clean in italic_wds:
                        word_data.append((wd, font_i))
                    else:
                        word_data.append((wd, font_r))
                total_w = (sum(f.getlength(wd) for wd, f in word_data)
                           + sp_w * (len(word_data) - 1))
                fx = cx - total_w / 2
                for wd, f in word_data:
                    draw.text((int(fx), y), wd, font=f, fill=col)
                    fx += f.getlength(wd) + sp_w
                y += lh

    hdr("СКЛАД:", 14, gap_before=4)
    body(p["ingredients"], 13, lh=18, bold_wds=p.get("bold_wds"))

    hdr("УМОВИ ЗБЕРІГАННЯ:", 14)
    body(p["storage"], 11, lh=14, italic_wds={'t', 'd(діб)'})

    hdr("АДРЕСА ВИРОБНИЧИХ ПОТУЖНОСТЕЙ:", 12, gap_before=5)
    body(p["address"], 11, lh=14)

    hdr("ВИРОБНИК:", 12, gap_before=4)
    body(p["manufacturer"], 11, lh=14)

    if p.get("commission"):
        hdr("ВИГОТОВЛЕНО НА ЗАМОВЛЕННЯ:", 12, gap_before=4)
        body(p["commission"], 11, lh=14)

    if p.get("phone"):
        y += 3
        body(p["phone"], 11, lh=14, alpha=210)

    body("Дата «Краще спожити до» та номер партії (L) вказані на етикетці.",
         11, lh=14, alpha=210)

# ── nutrition panel ───────────────────────────────────────────────────────────

def draw_nutrition_panel(base, draw, p, a2):
    nx  = 514
    nw  = 198
    ncx = nx + nw // 2
    y   = 14

    n = p["nutrition"]
    rows = [
        ("Енергетична цінність (калорійність)",
         f"{n['energy_kj']} kJ(кДж)/{n['energy_kcal']} kcal(ккал)", False),
        ("Жири",           f"{n['fat']} g(г)",     False),
        ("з них насичені", f"{n['sat_fat']} g(г)", True),
        ("Вуглеводи",      f"{n['carbs']} g(г)",   False),
        ("з них цукри",    f"{n['sugars']} g(г)",  True),
        ("Білки",          f"{n['protein']} g(г)", False),
        ("Сіль",           f"{n['salt']} g(г)",    False),
    ]

    hdr_txt = "Поживна цінність на 100 g(г) продукту"
    hw = tw(hdr_txt, FONT_R, 10)
    draw.text((ncx - hw // 2, y), hdr_txt, font=_pf(FONT_R, 10), fill=a2)
    y += 13
    draw.line([(nx, y + 6), (nx + nw, y + 6)], fill=(*a2, 200), width=1)
    y += 10

    row_h = 28
    shade = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    sd    = ImageDraw.Draw(shade)
    for i in range(len(rows)):
        if i % 2 == 0:
            ry = y + i * row_h
            sd.rectangle([(nx, ry), (nx + nw, ry + row_h)], fill=(255, 255, 255, 25))
    base.alpha_composite(shade)

    for i, (label, value, indent) in enumerate(rows):
        ry        = y + i * row_h
        indent_px = 10 if indent else 0
        lx        = nx + 3 + indent_px
        lw2       = nw - 36 - indent_px
        for j, ll in enumerate(wrap(label, FONT_R, 9, lw2)):
            draw.text((lx, ry + 2 + j * 11), ll, font=_pf(FONT_R, 9),
                      fill=(255, 255, 255))
        vw = tw(value, FONT_B, 10)
        draw.text((nx + nw - 3 - vw, ry + 14), value,
                  font=_pf(FONT_B, 10), fill=(255, 255, 255))

# ── right panel ───────────────────────────────────────────────────────────────

def draw_right_panel(base, draw, logo_white, p, a2, nc):
    rcx = 730 + 410 // 2   # = 935

    # Logo — optionally recolored
    logo = logo_white
    if p.get("logo_color"):
        arr   = np.array(logo_white).copy()
        vis   = arr[:, :, 3] > 10
        arr[vis, 0] = p["logo_color"][0]
        arr[vis, 1] = p["logo_color"][1]
        arr[vis, 2] = p["logo_color"][2]
        logo = Image.fromarray(arr, "RGBA")

    target_h = 200
    ow, oh   = logo.size
    logo_rs  = logo.resize((round(ow / oh * target_h), target_h), Image.LANCZOS)
    lx       = rcx - logo_rs.width // 2
    base.paste(logo_rs, (lx, 62), logo_rs)

    # Category — auto-size so long text fits in 400px
    cat_fs = 20
    while tw(p["category"], FONT_R, cat_fs) > 400 and cat_fs > 12:
        cat_fs -= 1
    cat_y = 62 + target_h + 16
    cw    = tw(p["category"], FONT_R, cat_fs)
    draw.text((rcx - cw // 2, cat_y), p["category"],
              font=_pf(FONT_R, cat_fs), fill=(255, 255, 255))

    # Accent line
    line_y = cat_y + cat_fs + 4
    draw.rectangle([(rcx - 55, line_y), (rcx + 55, line_y + 2)], fill=(*a2, 220))

    # Product name — vertically centred between accent line and mass row
    name_len = len(p["name"])
    ns       = next((s for thr, s in [(4, 90), (6, 78), (8, 66), (10, 54), (12, 48), (14, 42)]
                     if name_len <= thr), 36)
    nw_px    = tw(p["name"], FONT_B, ns)
    mid      = (line_y + LH - 52) // 2
    name_y   = mid - ns // 2
    name_x   = rcx - nw_px // 2
    draw.text((name_x + 2, name_y + 2), p["name"],
              font=_pf(FONT_B, ns), fill=(0, 0, 0, 130))
    draw.text((name_x, name_y), p["name"],
              font=_pf(FONT_B, ns), fill=nc)

    # Subtitle (optional — e.g. "30% жирності" / "67% жиру")
    extra_y = name_y + ns + 8
    if p.get("subtitle"):
        sw = tw(p["subtitle"], FONT_R, 22)
        draw.text((rcx - sw // 2, extra_y), p["subtitle"],
                  font=_pf(FONT_R, 22), fill=(*a2, 255))
        extra_y += 22 + 6

    # Sweetener note (optional — "з цукром та підсолоджувачем")
    if p.get("sweetener_note"):
        snw = tw(p["sweetener_note"], FONT_R, 18)
        draw.text((rcx - snw // 2, extra_y), p["sweetener_note"],
                  font=_pf(FONT_R, 18), fill=(*a2, 255))

    # МАСА НЕТТО + е  (g = Latin, (г) = Cyrillic)
    mass_y   = LH - 50
    mass_txt = f"МАСА НЕТТО {p['weight']} g(г)"
    mw_px    = tw(mass_txt, FONT_R, 13)
    draw.text((rcx - mw_px // 2, mass_y), mass_txt,
              font=_pf(FONT_R, 13), fill=(255, 255, 255))
    draw.text((rcx + mw_px // 2 + 4, mass_y - 6), "е",
              font=_pf(FONT_R, 22), fill=(255, 255, 255))

# ── barcode + date strip ──────────────────────────────────────────────────────

def draw_barcode(base, draw):
    box = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle(
        [(14, 494), (175, 580)], radius=4, fill=(255, 255, 255, 235))
    base.alpha_composite(box)
    bc_txt = "ШТРИХКОД"
    bw = tw(bc_txt, FONT_R, 10)
    draw.text(((14 + 175) // 2 - bw // 2, 530), bc_txt,
              font=_pf(FONT_R, 10), fill=(0, 0, 0, 90))

def draw_date_strip(base):
    strip_w = 48
    strip_x = LW - strip_w
    strip   = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    ImageDraw.Draw(strip).rectangle(
        [(strip_x, 9), (LW - 1, LH - 9)], fill=(255, 255, 255, 230))
    base.alpha_composite(strip)

    lines   = ["Дата «Краще спожити до»", "та номер партії (L)"]
    font    = _pf(FONT_R, 9)
    col_gap = 4
    rendered = []
    for text in lines:
        tw_px   = tw(text, FONT_R, 9)
        txt_img = Image.new("RGBA", (tw_px + 4, 14), (0, 0, 0, 0))
        ImageDraw.Draw(txt_img).text((2, 1), text, font=font, fill=(30, 30, 30))
        rendered.append(txt_img.rotate(90, expand=True))

    total_col_w = sum(r.width for r in rendered) + col_gap * (len(rendered) - 1)
    x = LW - 3 - total_col_w   # right-aligned, 3 px margin from edge
    for rotated in rendered:
        ry = (LH - rotated.height) // 2
        base.paste(rotated, (x, ry), rotated)
        x += rotated.width + col_gap

# ── label generator ───────────────────────────────────────────────────────────

def generate_label(p, logo_white):
    a2 = p["accent2"]
    nc = p.get("name_color", (255, 255, 255))

    base = make_background(p)
    draw = ImageDraw.Draw(base)

    draw_left_panel(draw, p, a2)
    draw_nutrition_panel(base, draw, p, a2)
    draw_right_panel(base, draw, logo_white, p, a2, nc)
    draw_barcode(base, draw)
    draw_icons(base, p.get("icons", _default_icons(p["weight"])))
    draw_date_strip(base)

    out_path = os.path.join(OUTPUT_DIR, p["output"])
    base.convert("RGB").save(out_path, quality=95)
    return out_path


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logo_white = load_logo_white(LOGO_PATH)
    print(f"Generating {len(PRODUCTS)} labels...\n")
    for p in PRODUCTS:
        path = generate_label(p, logo_white)
        print(f"  ✓  {os.path.basename(path)}")
    print(f"\nDone — saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()

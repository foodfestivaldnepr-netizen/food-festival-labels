"""
Food Festival — from-scratch label generator.
Renders 11 product labels (1178×594 px) using PIL + numpy.
All text is exact from labels_text.md. Logo from 'food festival logo.png'.
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

BASE       = os.path.dirname(__file__)
LOGO_PATH  = os.path.join(BASE, "food festival logo.png")
OUTPUT_DIR = os.path.join(BASE, "output_labels")

FONT_BOLD    = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
FONT_MEDIUM  = "/usr/share/fonts/truetype/ubuntu/Ubuntu-M.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"

W, H = 1178, 594

# Layout constants
LEFT_X      = 14
LEFT_WRAP   = 490
LEFT_CX     = (LEFT_X + 502) // 2   # centre of left panel  ≈ 258
NUTRI_LX    = 514
NUTRI_RX    = 712
NUTRI_CX    = (514 + 712) // 2       # centre of nutrition panel = 613
SEP_X       = 722
RIGHT_CX    = 947
LOGO_H      = 255
LOGO_TOP    = 75
# Barcode box — bottom-left corner of label
BC_X1, BC_X2 = 14,  175
BC_Y1, BC_Y2 = 494, 580

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
        "key": "03_mayo_67", "category": "МАЙОНЕЗ", "name": "67% жиру ПРЕМІУМ",
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
        "weight": "5000", "accent": (227, 38, 54), "accent2": (0, 146, 70), "accent3": (0, 146, 70), "bg_icons": "tomato",
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
        "weight": "830", "accent": (215, 205, 0), "accent2": (255, 255, 0),
        "nutrition": {"energy_kj": "1587", "energy_kcal": "385", "fat": "40,0",
                      "sat_fat": "5,2", "carbs": "6,3", "sugars": "3,8",
                      "protein": "0,03", "salt": "1,4"},
        "ingredients": (
            "ВОДА ПИТНА, ОЛІЯ СОНЯШНИКОВА РАФІНОВАНА ДЕЗОДОРОВАНА, ЦУКОР БІЛИЙ, "
            "ЗАГУЩУВАЧ - МОДИФІКОВАНИЙ КУКУРУДЗЯНИЙ АБО КАРТОПЛЯНИЙ КРОХМАЛЬ, "
            "СІЛЬ КУХОННА, ЕМУЛЬГАТОР - МОДИФІКОВАНИЙ КУКУРУДЗЯНИЙ АБО "
            "КАРТОПЛЯНИЙ КРОХМАЛЬ, СИРНИЙ ПОРОШОК (0,5%)(МОЛОКО, СІЛЬ, ФЕРМЕНТ "
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


def load_logo_white(logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    arr = np.array(logo)
    white_mask = (arr[:, :, 0] > 230) & (arr[:, :, 1] > 230) & (arr[:, :, 2] > 230)
    arr[white_mask, 3] = 0       # transparent background
    arr[~white_mask, :3] = 255   # white content
    return Image.fromarray(arr, "RGBA")


def resize_logo(logo_white, target_h=LOGO_H):
    ow, oh = logo_white.size
    ratio = target_h / oh
    return logo_white.resize((round(ow * ratio), target_h), Image.LANCZOS)


def recolor_logo(logo_white, color):
    """Recolor white pixels of the logo to the given RGB color."""
    arr = np.array(logo_white).copy()
    visible = arr[:, :, 3] > 10
    arr[visible, 0] = color[0]
    arr[visible, 1] = color[1]
    arr[visible, 2] = color[2]
    return Image.fromarray(arr, "RGBA")


def make_background(accent, accent2, accent3=None, bg_split=None, border=None, bg_dark=None):
    if bg_split:
        # Solid horizontal split: top color / bottom color
        top_c, bot_c = bg_split
        arr = np.zeros((H, W, 4), dtype=np.uint8)
        arr[:H//2, :, :3] = top_c
        arr[:H//2, :,  3] = 255
        arr[H//2:, :, :3] = bot_c
        arr[H//2:, :,  3] = 255
        base = Image.fromarray(arr, "RGBA")
    else:
        dark = bg_dark if bg_dark else tuple(int(c * 0.25) for c in accent)
        base = Image.new("RGBA", (W, H), (*dark, 255))
        alphas = np.linspace(200, 0, W).astype(np.uint8) if bg_dark else np.linspace(150, 20, W).astype(np.uint8)
        grad = np.zeros((H, W, 4), dtype=np.uint8)
        grad[:, :, 0] = accent[0]
        grad[:, :, 1] = accent[1]
        grad[:, :, 2] = accent[2]
        grad[:, :, 3] = alphas
        base = Image.alpha_composite(base, Image.fromarray(grad, "RGBA"))

    # Decorative elements
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(deco)
    bar_c      = border   if border   else (accent3 if accent3 else accent)
    inner_line = (255, 255, 255) if accent3 else accent2
    dd.rectangle([0, 0, 5, H],       fill=(*bar_c, 255))       # left stripe
    dd.rectangle([0, 0, W, 8],       fill=(*bar_c, 255))       # top bar
    dd.rectangle([0, H - 8, W, H],   fill=(*bar_c, 255))       # bottom bar
    dd.rectangle([5, 15, W, 17],     fill=(*inner_line, 150))  # thin accent line
    if bg_split:
        # Gold split line at the horizontal boundary
        dd.line([(0, H//2), (W, H//2)], fill=(*bar_c, 255), width=3)
    dd.polygon(                                                 # subtle diagonal
        [(549, 0), (629, 0), (579, H), (499, H)],
        fill=(*accent2, 12),
    )
    dd.line([(SEP_X, 12), (SEP_X, H - 12)],                    # vertical separator
            fill=(*accent2, 102), width=1)
    return Image.alpha_composite(base, deco)


def draw_tomato_icons(base, accent):
    import random, math
    tc = tuple((c + 255) // 2 for c in accent)          # 2x lighter than accent
    lc = (max(0, tc[0]-70), min(255, tc[1]+80), max(0, tc[2]-70))  # greenish calyx
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(layer)
    rng = random.Random(42)
    for _ in range(30):
        cx = rng.randint(-40, W + 40)
        cy = rng.randint(-40, H + 40)
        r  = rng.randint(14, 55)
        alpha = rng.randint(28, 52)
        # Body
        sd.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(*tc, alpha))
        # Calyx leaves at top of tomato
        lw = max(4, r // 3)
        lh = max(5, r // 2)
        top_y = cy - r + lh // 2
        sd.ellipse([(cx - lw // 2, top_y - lh // 2), (cx + lw // 2, top_y + lh // 2)], fill=(*lc, alpha))
        sd.ellipse([(cx - lw * 2, top_y - 2), (cx,          top_y + lh // 3)], fill=(*lc, alpha))
        sd.ellipse([(cx,          top_y - 2), (cx + lw * 2, top_y + lh // 3)], fill=(*lc, alpha))
    base.alpha_composite(layer)


def draw_product_shadows(base):
    """Subtle bottle/jar silhouettes layered into the background."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(layer)

    def bottle(cx, cy, bw, bh, alpha=32):
        c = (255, 255, 255, alpha)
        body_h = int(bh * 0.67)
        by = cy - bh // 2
        # Body
        sd.rounded_rectangle([(cx - bw//2, by), (cx + bw//2, by + body_h)],
                              radius=bw // 4, fill=c)
        # Shoulder
        sw, sh = int(bw * 0.58), int(bh * 0.11)
        sy = by - sh + 5
        sd.rounded_rectangle([(cx - sw//2, sy), (cx + sw//2, sy + sh + int(bh * 0.05))],
                              radius=sw // 4, fill=c)
        # Neck
        nw, nh = int(bw * 0.38), int(bh * 0.14)
        ny = sy - nh + 3
        sd.rounded_rectangle([(cx - nw//2, ny), (cx + nw//2, ny + nh)],
                              radius=nw // 3, fill=c)
        # Cap
        cw, ch = int(bw * 0.50), int(bh * 0.08)
        sd.rounded_rectangle([(cx - cw//2, ny - ch), (cx + cw//2, ny)],
                              radius=cw // 4, fill=c)

    def jar(cx, cy, jw, jh, alpha=28):
        c = (255, 255, 255, alpha)
        sd.rounded_rectangle([(cx - jw//2, cy - jh//2), (cx + jw//2, cy + jh//2)],
                              radius=jw // 8, fill=c)
        lw, lh = int(jw * 1.06), int(jh * 0.18)
        sd.rounded_rectangle([(cx - lw//2, cy - jh//2 - lh + 4),
                               (cx + lw//2, cy - jh//2 + 8)],
                              radius=lw // 8, fill=c)

    # Far-right tall bottle (brand panel)
    bottle(1108, 300, 115, 580, alpha=18)
    # Mid-right bottle (near separator)
    bottle(735, 340, 70,  460, alpha=12)
    # Left panel wide jar
    jar(185, 430, 190, 220, alpha=12)
    # Far-left bottle, partially cropped
    bottle(-10, 310, 88, 530, alpha=10)
    # Small jar in nutrition zone
    jar(620, 490, 95, 120, alpha=8)

    base.alpha_composite(layer)


def wrap_text(text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if font.getlength(test) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def fit_name_font(name, max_width=420):
    for size in range(90, 41, -6):
        font = ImageFont.truetype(FONT_BOLD, size)
        if font.getlength(name) <= max_width:
            return font
    return ImageFont.truetype(FONT_BOLD, 42)


def draw_left_panel(draw, p, fonts, accent2):
    cx = LEFT_CX
    y = 22
    col_body  = (255, 255, 255)
    col_small = (255, 255, 255)

    def ctext(text, font, color):
        tw = int(font.getlength(text))
        draw.text((cx - tw // 2, y), text, font=font, fill=color)

    def section(header, text, body_font, line_h, gap_after=8):
        nonlocal y
        ctext(header, fonts["header"], accent2)
        y += 20
        for line in wrap_text(text, body_font, LEFT_WRAP):
            ctext(line, body_font, col_body)
            y += line_h
        y += gap_after

    section("СКЛАД:", p["ingredients"], fonts["body"], 20)
    section("УМОВИ ЗБЕРІГАННЯ:", p["storage"], fonts["small"], 17)

    ctext("АДРЕСА ВИРОБНИЧИХ ПОТУЖНОСТЕЙ:", fonts["small_b"], accent2)
    y += 17
    for line in wrap_text(p["address"], fonts["small"], LEFT_WRAP):
        ctext(line, fonts["small"], col_small)
        y += 17
    y += 4

    ctext("ВИРОБНИК:", fonts["small_b"], accent2)
    y += 17
    for line in wrap_text(p["manufacturer"], fonts["small"], LEFT_WRAP):
        ctext(line, fonts["small"], col_small)
        y += 17

    ctext("ВИГОТОВЛЕНО НА ЗАМОВЛЕННЯ:", fonts["small_b"], accent2)
    y += 17
    for line in wrap_text(p["commission"], fonts["small"], LEFT_WRAP):
        ctext(line, fonts["small"], col_small)
        y += 17
    date_phrase = "Дата «Краще спожити до» та номер партії (L) вказані на етикетці."
    for line in wrap_text(date_phrase, fonts["small"], LEFT_WRAP):
        ctext(line, fonts["small"], col_small)
        y += 17


def draw_nutrition_panel(base, draw, p, fonts, accent, accent2):
    n = p["nutrition"]
    x_label = NUTRI_LX
    x_val   = NUTRI_RX
    y = 24

    # Header — centred in nutrition column
    hdr = "Поживна цінність на 100 g(г) продукту"
    hw = int(fonts["small"].getlength(hdr))
    draw.text((NUTRI_CX - hw // 2, y), hdr, font=fonts["small"], fill=accent2)
    y += 14
    draw.line([(x_label, y), (x_val, y)], fill=(*accent2, 200), width=1)
    y += 5

    rows = [
        ("Енергетична цінність (калорійність)", f"{n['energy_kj']} kJ(кДж)/{n['energy_kcal']} kcal(ккал)", False),
        ("Жири",              f"{n['fat']} g(г)",      False),
        ("з них насичені",    f"{n['sat_fat']} g(г)",  True),
        ("Вуглеводи",         f"{n['carbs']} g(г)",    False),
        ("з них цукри",       f"{n['sugars']} g(г)",   True),
        ("Білки",             f"{n['protein']} g(г)",  False),
        ("Сіль",              f"{n['salt']} g(г)",     False),
    ]

    # Stacked rows: label on line 1, value right-aligned on line 2.
    # Every row is the same height — no text ever overlaps.
    row_h   = 30   # total row height
    line2   = 15   # vertical offset to the value line inside each row

    # Alternating row shading
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shade_d = ImageDraw.Draw(shade)
    for i in range(len(rows)):
        if i % 2 == 0:
            shade_d.rectangle(
                [(x_label - 2, y + i * row_h),
                 (x_val + 2,   y + i * row_h + row_h)],
                fill=(255, 255, 255, 25),
            )
    base.alpha_composite(shade)

    # Row text
    for i, (label, value, indent) in enumerate(rows):
        row_y = y + i * row_h
        lx = x_label + (8 if indent else 0)
        draw.text((lx, row_y), label, font=fonts["small"], fill=(255, 255, 255))
        vw = int(fonts["small_b"].getlength(value))
        draw.text((x_val - vw, row_y + line2), value, font=fonts["small_b"], fill=(255, 255, 255))

    # Icons — centred in nutrition column, prominent boxes
    icon_y = y + len(rows) * row_h + 10
    icon_labels = ["БЕЗ ГМО", "РР 05"]
    icon_pad_x, icon_pad_y, gap = 10, 5, 8
    icon_h = int(fonts["icon"].getbbox("A")[3]) + icon_pad_y * 2
    widths = [int(fonts["icon"].getlength(lbl)) + icon_pad_x * 2 for lbl in icon_labels]
    total_w = sum(widths) + gap * (len(icon_labels) - 1)
    ix = NUTRI_CX - total_w // 2
    for label, bw in zip(icon_labels, widths):
        draw.rounded_rectangle(
            [(ix, icon_y), (ix + bw, icon_y + icon_h)],
            radius=4, outline=(255, 255, 255), width=2,
        )
        tw = int(fonts["icon"].getlength(label))
        draw.text((ix + (bw - tw) // 2, icon_y + icon_pad_y), label,
                  font=fonts["icon"], fill=(255, 255, 255))
        ix += bw + gap


def draw_barcode_area(draw, fonts):
    mid_y = BC_Y1 + (BC_Y2 - BC_Y1) // 2 - 7
    draw.rectangle([(BC_X1, BC_Y1), (BC_X2, BC_Y2)],
                   outline=(255, 255, 255), width=1)
    bc_cx = (BC_X1 + BC_X2) // 2
    tw = int(fonts["bc"].getlength("ШТРИХКОД"))
    draw.text((bc_cx - tw // 2, mid_y), "ШТРИХКОД", font=fonts["bc"], fill=(255, 255, 255))


def draw_right_panel(base, draw, logo_resized, p, fonts):
    accent  = p["accent"]
    accent2 = p["accent2"]
    cx = RIGHT_CX

    # Logo
    lw = logo_resized.width
    lx = cx - lw // 2
    base.paste(logo_resized, (lx, LOGO_TOP), logo_resized)

    # Category
    cat_y = LOGO_TOP + LOGO_H + 10
    cw = int(fonts["cat"].getlength(p["category"]))
    draw.text((cx - cw // 2, cat_y), p["category"], font=fonts["cat"], fill=(255, 255, 255))

    # Accent separator line
    line_y = cat_y + 28
    draw.line([(cx - 55, line_y), (cx + 55, line_y)], fill=(*accent2, 220), width=2)

    # Product name (auto-sized, vertically centred in right panel below line)
    name_font = fit_name_font(p["name"], max_width=420)
    bbox = name_font.getbbox(p["name"])
    nw = bbox[2] - bbox[0]
    nh = bbox[3] - bbox[1]
    # Place name centred between line and МАСА НЕТТО (~y=540)
    flag_reserve     = 34 if p.get("flag") == "italy" else 0
    name_area_top    = line_y + 14
    name_area_bottom = 536 - flag_reserve
    ny = name_area_top + (name_area_bottom - name_area_top - nh) // 2
    nx = cx - nw // 2
    # Shadow
    draw.text((nx + 2, ny + 2), p["name"], font=name_font, fill=(0, 0, 0, 140))
    name_col = p.get("name_color", (255, 255, 255))
    draw.text((nx, ny), p["name"], font=name_font, fill=name_col)

    # Italian flag (optional)
    if p.get("flag") == "italy":
        flag_w, flag_h = 96, 20
        flag_x = cx - flag_w // 2
        flag_y = ny + nh + 8
        s = flag_w // 3
        draw.rectangle([(flag_x,       flag_y), (flag_x + s,     flag_y + flag_h)], fill=(0, 146, 70))
        draw.rectangle([(flag_x + s,   flag_y), (flag_x + s * 2, flag_y + flag_h)], fill=(255, 255, 255))
        draw.rectangle([(flag_x+s*2,   flag_y), (flag_x + flag_w,flag_y + flag_h)], fill=(230, 149, 155))

    # МАСА НЕТТО
    mn_text = f"МАСА НЕТТО {p['weight']} g(г) е"
    mw = int(fonts["weight"].getlength(mn_text))
    draw.text((cx - mw // 2, 548), mn_text, font=fonts["weight"], fill=(255, 255, 255))


def draw_date_strip(base, fonts):
    """White vertical strip on the right edge with rotated date text."""
    strip_x = W - 38
    strip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(strip)
    sd.rectangle([(strip_x, 9), (W - 1, H - 9)], fill=(255, 255, 255, 230))
    base.alpha_composite(strip)

    text = "Дата «Краще спожити до» та номер партії (L)"
    font = fonts["bc"]
    tw = int(font.getlength(text))
    txt_img = Image.new("RGBA", (tw + 4, 22), (0, 0, 0, 0))
    ImageDraw.Draw(txt_img).text((2, 3), text, font=font, fill=(30, 30, 30))
    rotated = txt_img.rotate(90, expand=True)
    rx = strip_x + (38 - rotated.width) // 2
    ry = (H - rotated.height) // 2
    base.paste(rotated, (rx, ry), rotated)


def generate_label(p, logo_white):
    accent  = p["accent"]
    accent2 = p["accent2"]

    # Phase 1 — background
    base = make_background(accent, accent2, p.get("accent3"), p.get("bg_split"), p.get("border"), p.get("bg_dark"))
    # draw_product_shadows(base)  # removed
    if p.get("bg_icons") == "tomato":
        draw_tomato_icons(base, accent)

    # Phase 2 — fonts
    fonts = {
        "body":    ImageFont.truetype(FONT_REGULAR, 16),
        "header":  ImageFont.truetype(FONT_BOLD,    16),
        "small":   ImageFont.truetype(FONT_REGULAR, 13),
        "small_b": ImageFont.truetype(FONT_BOLD,    13),
        "cat":     ImageFont.truetype(FONT_MEDIUM,  22),
        "icon":    ImageFont.truetype(FONT_BOLD,     12),
        "weight":  ImageFont.truetype(FONT_MEDIUM,  15),
        "bc":      ImageFont.truetype(FONT_REGULAR, 11),
    }

    # Phase 3 — logo
    logo_tinted = recolor_logo(logo_white, p["logo_color"]) if p.get("logo_color") else logo_white
    logo_resized = resize_logo(logo_tinted, LOGO_H)

    # Phase 4 — text layers
    draw = ImageDraw.Draw(base)
    draw_left_panel(draw, p, fonts, accent2)
    draw_nutrition_panel(base, draw, p, fonts, accent, accent2)
    draw_barcode_area(draw, fonts)
    draw_right_panel(base, draw, logo_resized, p, fonts)
    draw_date_strip(base, fonts)

    # Phase 5 — save
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

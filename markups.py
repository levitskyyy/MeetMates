from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

## кнопки


# основное
back = InlineKeyboardButton(text="Назад", callback_data="back")

# старт меню
mainMenu = InlineKeyboardMarkup(row_width=2)
search = InlineKeyboardButton(text="🔍 Искать", callback_data="search")
settings = InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
rating = InlineKeyboardButton(text="🔷 Рейтинг", callback_data="rating")
other = InlineKeyboardButton(text="🧰 Другое", callback_data="other")
profile = InlineKeyboardButton(text="👤 Профиль", callback_data="profile")

# search меню
searchMenu = InlineKeyboardMarkup(row_width=3)
minecraft = InlineKeyboardButton(text="⚒ Minecraft", callback_data="minecraft")
csgo = InlineKeyboardButton(text="🔫 CS:GO", callback_data="csgo")
dota = InlineKeyboardButton(text="⚔️ Dota 2", callback_data="dota")
rust = InlineKeyboardButton(text="🪚 RUST", callback_data="rust")
wot = InlineKeyboardButton(text="💣 WOT", callback_data="wot")
valorant = InlineKeyboardButton(text="🏹 Valorant", callback_data="valorant")
pubg = InlineKeyboardButton(text="🪖 PUBG", callback_data="pubg")
done = InlineKeyboardButton(text="Готово", callback_data="done")

# кнопки под текстом сообщений
messageMenu = InlineKeyboardMarkup(row_width=1)
stop = InlineKeyboardButton(text="❌ Остановить", callback_data="stop")
share = InlineKeyboardButton(text="🌐 Поделиться ником", callback_data="share")

# endMenu
endMenu = InlineKeyboardMarkup(row_width=1)
next = InlineKeyboardButton(text="➡️ Следующий диалог", callback_data="next")

# other меню
otherMenu = InlineKeyboardMarkup(row_width=2)
info = InlineKeyboardButton(text="ℹ️ Инфо", callback_data="info")
donate = InlineKeyboardButton(text="💎 Пожертвовать", callback_data="donate")

# settings меню
settingsMenu = InlineKeyboardMarkup(row_width=2)
eprofile = InlineKeyboardButton(text="📝 Редактировать профиль", callback_data="eprofile")
refka = InlineKeyboardButton(text="💠 Реферальная система", callback_data="refka")

# меню для быстрого выхода
backMenu = InlineKeyboardMarkup(row_width=1)


# Создание менюшек


# старт
mainMenu.insert(search)
mainMenu.insert(settings)
mainMenu.insert(rating)
mainMenu.insert(other)
mainMenu.insert(profile)

# сёрч
searchMenu.insert(minecraft)
searchMenu.insert(csgo)
searchMenu.insert(dota)
searchMenu.insert(rust)
searchMenu.insert(wot)
searchMenu.insert(valorant)
searchMenu.insert(pubg)
searchMenu.insert(back)
searchMenu.insert(done)

# other
otherMenu.insert(info)
otherMenu.insert(donate)
otherMenu.insert(back)

# настройки
settingsMenu.insert(eprofile)
settingsMenu.insert(refka)
settingsMenu.insert(back)

# Сообщения
messageMenu.insert(stop)
messageMenu.insert(share)

# end
endMenu.insert(next)
endMenu.insert(back)

# быстрый выход
backMenu.insert(back)
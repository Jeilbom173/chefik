

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
import bluda
from bluda import recipes

TOKEN = '6294565852:AAGGEhH_BxzuwXiuHjcd2oufN6w1jSzUB_0'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())

MAIN_PHOTO_URL = 'https://sun9-78.userapi.com/impg/7TQCsSA5sd-p01oj6rSMCgLe1PM9zbKNDCnRyg/IZaeCiLDNPg.jpg?size=1080x1080&quality=95&sign=53736b84c350bbe69f405ba549d85e3d&type=album'

user_choices = {}
current_page = 0


def get_possible_recipes(chosen_products):
  possible_recipes = []
  for recipe, ingredients in recipes.items():
    if all(product in chosen_products for product in ingredients):
      possible_recipes.append((recipe, ingredients))
  return possible_recipes


def create_product_keyboard(user_id, page):
  products = [
      'Яйцо',
      'Молоко',
      'Зелень',
      'Картофель',
      'Масло',
      'Курица',
      'Лук',
      'Капуста',
      'Морковь',
      'Свекла',
      'Рыба',
      'Рис',
      'Горошек',
      'Кукуруза',
      'Макароны',
      'Фарш',
      'Мясо',
      'Лимон',
      'Гречка',
      'Специи',
      'Болгарский перец',
      'Мука',
      'Творог',
      'Яблоко',
      'Сахар',
      'Огурцы соленые',
      'Колбаса',
      'Майонез',
      'Томат',
      'Грибы',
      'Брокколи',
      'Огурец свежий',
      'Сыр',
      'Спагетти',
      'Баклажан',
      'Тыква',
      'Кабачок',
      'Фрикадельки',
      'Квас',
      'Сметана',
  ]

  products_per_page = 4

  start_index = page * products_per_page
  end_index = (page + 1) * products_per_page

  current_products = products[start_index:end_index]

  keyboard = InlineKeyboardMarkup(row_width=2)

  for product in current_products:
    is_chosen = user_choices.get(user_id, {}).get(product, False)
    button_text = f"✅ {product}" if is_chosen else product
    keyboard.insert(
        InlineKeyboardButton(button_text, callback_data=f'choose_{product}'))

  nav_buttons = []

  if start_index > 0:
    nav_buttons.append(InlineKeyboardButton("👈", callback_data='prev_page'))

  if end_index < len(products):
    nav_buttons.append(InlineKeyboardButton("👉", callback_data='next_page'))

  keyboard.add(*nav_buttons)
  keyboard.add(InlineKeyboardButton("Готово", callback_data='done_choosing'))

  return keyboard


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
  chat_id = message.chat.id

  keyboard = InlineKeyboardMarkup()
  button = InlineKeyboardButton("Проголодался?", callback_data='start_eating')
  keyboard.add(button)

  await bot.send_photo(
      chat_id=chat_id,
      photo=MAIN_PHOTO_URL,
      caption=
      "✋ Привет, ты проголодался?\n❓ *Кто-же я такой?*\n🍴 *Я* - бот для помощи голодным людям. Нажми на кнопку ниже, чтобы начать работу со мной!",
      reply_markup=keyboard,
      parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(lambda callback_query: True)
async def button_pressed(callback_query: types.CallbackQuery):
  chat_id = callback_query.message.chat.id
  user_id = callback_query.from_user.id

  global current_page

  action = callback_query.data

  if action == 'start_eating':
    keyboard = create_product_keyboard(user_id, current_page)
    await bot.send_message(
        chat_id=chat_id,
        text="Приступим! \nВыбери продукты, которые у тебя есть в наличии:",
        reply_markup=keyboard)
  elif action.startswith('choose_'):
    product = action.split('_')[1]
    if user_choices.get(user_id) is None:
      user_choices[user_id] = {}
    user_choices[user_id][product] = not user_choices[user_id].get(
        product, False)

    keyboard = create_product_keyboard(user_id, current_page)
    await bot.edit_message_text(chat_id=chat_id,
                                message_id=callback_query.message.message_id,
                                text="Выберите продукты:",
                                reply_markup=keyboard)
  elif action == 'done_choosing':
    chosen_products = [
        product for product, chosen in user_choices[user_id].items() if chosen
    ]
    possible_recipes = get_possible_recipes(chosen_products)

    if not possible_recipes:
      await bot.send_message(
          chat_id=chat_id,
          text=
          "К сожалению, невозможно приготовить ничего из выбранных продуктов 😔 Попробуйте добавить больше продуктов."
      )
    else:
      for recipe, ingredients in possible_recipes:
        response_text = f"{recipe} - требуемые ингредиенты: {', '.join(ingredients)}"
        await bot.send_message(chat_id=chat_id, text=response_text)
  elif action == 'prev_page':
    current_page -= 1
    keyboard = create_product_keyboard(user_id, current_page)
    await bot.edit_message_text(chat_id=chat_id,
                                message_id=callback_query.message.message_id,
                                text="Выберите продукты:",
                                reply_markup=keyboard)
  elif action == 'next_page':
    current_page += 1
    keyboard = create_product_keyboard(user_id, current_page)
    await bot.edit_message_text(chat_id=chat_id,
                                message_id=callback_query.message.message_id,
                                text="Выберите продукты:",
                                reply_markup=keyboard)


if __name__ == '__main__':
  from aiogram import executor
  executor.start_polling(dp, skip_updates=True)

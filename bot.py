from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from aiogram.types import ForceReply
import asyncio
from db import fetch_all, fetch_by_type
from maxima_parse import parser
from API_KEY import API_KEY

API_TOKEN = API_KEY

product_types = ["Vaisiai ir daržovės", "Mėsa ir mėsos gaminiai", "Pieno gaminiai ir kiaušiniai",
                 "Žuvis ir žuvies produktai", "Kulinarija", "Konditerija", "Duonos gaminiai", "Šaldytas maistas",
                 "Saldumynai", "Bakalėja", "Konservuotas maistas", "Kava, kakava, arbata",
                 "Gėrimai", "Kūdikių ir vaikų prekės", "Prekės gyvūnams", "Kosmetika ir higiena",
                 "Buitinė chemija", "Pramonės prekė"]

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


def generate_keyboard():
    buttons = [[KeyboardButton(text=product_type)] for product_type in product_types]

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Choose the category"
    )
    return keyboard


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.reply("Hey... \n I'm here, to help you save money. "
                        "\n I will find you discounts at Maxima shop in Lithuania",
                        reply_markup=generate_keyboard())


@dp.message()
async def process_product_type(message: types.Message):
    product_type = message.text

    if product_type not in product_types:
        await message.reply("Please select a valid category from the list.")
        return

    products = fetch_by_type(product_type)

    if products.empty:
        await message.reply(f"No discounts available for {product_type}.")
        return

    response = f"Here are some discounts for {product_type}:\n\n"
    for _, row in products.iterrows():
        response += (
            f'🛒 {row["product"]}\n'
            f'💵 {row["price_no_discount"]}\n'
            f'({row["discount"]})\n'
            f'💵 {row["price_with_discount"]}\n'
            f'⏳ {row["discount_to"]}\n\n'
        )

    if len(response) > 4000:
        for chunk in [response[i:i + 4000] for i in range(0, len(response), 4000)]:
            await message.reply(chunk)
    else:
        await message.reply(response)


@dp.callback_query()
async def debug_callback(callback_query: types.CallbackQuery):
    print(f"Unhandled callback: {callback_query.data}")  # Лог для всех callback-запросов
    await callback_query.answer("Callback received, but no handler matched.", show_alert=True)


async def data_update():
    while True:
        parser()
        await asyncio.sleep(36000)


if __name__ == "__main__":
    async def main():
        await asyncio.gather(dp.start_polling(bot), data_update())


    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stoped by user")

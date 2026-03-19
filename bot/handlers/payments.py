from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.crud import orm_get_user_products
from bot.keyboards.inline import MenuCallback
from bot.logging_config import logger

router = Router()


@router.callback_query(MenuCallback.filter(F.menu_name == 'order'))
async def order_pay(callback: CallbackQuery, bot: Bot, payment_token: str, session: AsyncSession):
    products = await orm_get_user_products(session, callback.from_user.id)
    logger.debug(products)
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title='Оплата заказа',
        description='Описание заказа',
        payload='order_id_1',
        provider_token=payment_token,
        currency='RUB',
        prices=[LabeledPrice(label='label', amount=60000)],
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def congrats(message: Message):
    await message.answer(
        text='Поздравляем с покупкой!',
        message_effect_id='5104841245755180586',
    )

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.crud import orm_clear_cart, orm_get_user_products
from bot.keyboards.inline import MenuCallback

router = Router()


@router.callback_query(MenuCallback.filter(F.menu_name == 'order'))
async def order_pay(
    callback: CallbackQuery,
    bot: Bot,
    payment_token: str,
    session: AsyncSession,
    state: FSMContext,
):
    products = await orm_get_user_products(session, callback.from_user.id)
    if not products:
        await callback.message.answer(text='Ваша корзина пуста')
    else:
        total = int(sum(p.quantity * p.product.price for p in products) * 100)
        invoice_msg = await bot.send_invoice(
            chat_id=callback.message.chat.id,
            title='Оплата заказа',
            description='Описание заказа',
            payload='order_id_1',
            provider_token=payment_token,
            currency='RUB',
            prices=[LabeledPrice(label='Ваш заказ', amount=total)],
        )
        await state.set_data({'msg_id': invoice_msg.message_id})
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery, session: AsyncSession):
    await query.answer(ok=True)
    await orm_clear_cart(session, query.from_user.id)


@router.message(F.successful_payment)
async def congrats(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=data.get('msg_id'),
    )
    await message.answer(
        text='Поздравляем с покупкой!',
        message_effect_id='5104841245755180586',
    )

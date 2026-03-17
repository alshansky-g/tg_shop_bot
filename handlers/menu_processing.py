"""Module contains all functions for navigation via inline menu."""

from aiogram.types import BufferedInputFile, CallbackQuery, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from database import crud
from database.models import Product
from keyboards import inline
from utils.paginator import Paginator
from utils.placeholder import create_placeholder_png

PLACEHOLDER = 'placeholder'


def _media(image: str | None, caption: str, gradient_key: str = '') -> InputMediaPhoto:
    """Return InputMediaPhoto with a generated gradient if no real image is set."""
    if image and image != PLACEHOLDER:
        return InputMediaPhoto(media=image, caption=caption)
    png = create_placeholder_png(banner_name=gradient_key)
    return InputMediaPhoto(
        media=BufferedInputFile(png, filename='banner.png'),
        caption=caption,
    )


async def main_menu(session: AsyncSession, menu_name: str):
    """Forms 0 level of inline menu (main menu)."""
    banner = await crud.orm_get_banner(session, menu_name)
    return _media(banner.image, banner.description or '', menu_name), inline.main_menu_kb


async def catalog(session: AsyncSession, level: int, menu_name: str):
    """Forms 1 level of inline menu to show products categories."""
    banner = await crud.orm_get_banner(session, menu_name)
    categories = await crud.orm_get_categories(session)
    keyboard = inline.get_user_catalog_btns(level=level, categories=categories)
    return _media(banner.image, banner.description or '', menu_name), keyboard


async def products(session: AsyncSession, level: int, category: int, page: int):
    """Forms 2 level of inline menu with all products inside a category."""
    all_products = await crud.orm_get_products(session, category)
    paginator = Paginator(all_products, page=page)
    product: Product = paginator.get_page()[0]
    caption = (
        f'<b>{product.name}</b>\n{product.description}\n'
        f'Стоимость: {round(product.price, 2)}\n'
        f'<b>Товар {paginator.page} из {paginator.pages}</b>'
    )
    keyboard = inline.get_products_btns(
        level=level,
        category=category,
        page=page,
        pagination_btns=paginator.get_buttons(),
        product_id=product.id,
    )
    return _media(product.image, caption), keyboard


async def cart(session: AsyncSession, level: int, user_id: int, page: int):
    """Forms 3 level of inline menu to show user cart."""
    user_cart = await crud.orm_get_user_products(session, user_id)
    if not user_cart:
        banner = await crud.orm_get_banner(session, name='Корзина')
        return _media(banner.image, 'Корзина пуста', 'Корзина'), inline.empty_cart_kb

    cart_items: list[tuple[Product, int]] = [(pos.product, pos.quantity) for pos in user_cart]
    total_cost = sum(p.price * q for p, q in cart_items)
    paginator = Paginator(cart_items, page=page)
    product, quantity = paginator.get_page()[0]
    caption = (
        f'<b>{product.name}: {quantity} x {product.price} = {product.price * quantity}</b>\n'
        f'Позиций в корзине: <b>{len(cart_items)}</b>\n'
        f'Общая стоимость заказа: <b>{total_cost}</b>'
    )
    keyboard = inline.get_cart_buttons(
        level=level,
        pagination_btns=paginator.get_buttons(),
        page=page,
        product_id=product.id,
    )
    return _media(product.image, caption), keyboard


async def process_cart_actions(
    callback: CallbackQuery,
    callback_data: inline.MenuCallback,
    session: AsyncSession,
    quantity: int = 1,
) -> int:
    """Handles all increase/decrease/delete operations in user cart."""
    menu_name = callback_data.menu_name
    product_id = callback_data.product_id
    user_id = callback.from_user.id
    if menu_name == 'add_to_cart':
        quantity = await add_to_cart(callback, callback_data, session)
        await callback.answer(f'В корзине: {quantity}')
    elif menu_name == 'decrease' and product_id is not None:
        quantity = await crud.decrease_items_in_cart(session, user_id, product_id)
        await callback.answer(f'В корзине: {quantity}')
    elif menu_name == 'delete' and product_id is not None:
        quantity = await crud.orm_delete_from_cart(session, user_id, product_id)
        await callback.answer('Позиция удалена')
    return quantity


async def add_to_cart(
    callback: CallbackQuery, callback_data: inline.MenuCallback, session: AsyncSession
) -> int:
    """Creates user if not in DB, adds product to his cart."""
    await crud.orm_add_user(
        session=session,
        user_id=callback.from_user.id,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )
    amount = await crud.orm_add_to_cart(
        session,
        callback.from_user.id,
        callback_data.product_id,  # type: ignore[arg-type]
    )
    await session.commit()
    return amount


async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    category: int | None = None,
    page: int | None = None,
    user_id: int | None = None,
):
    """Mediator func for managing inline menu levels."""
    if level == 0:
        return await main_menu(session, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await products(session, level, category, page)  # type: ignore[arg-type]
    elif level == 3:
        return await cart(session, level, user_id, page)  # type: ignore[arg-type]

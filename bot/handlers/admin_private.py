from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.crud import (
    orm_add_product,
    orm_change_banner_image,
    orm_delete_product,
    orm_get_categories,
    orm_get_info_pages,
    orm_get_product,
    orm_get_products,
    orm_update_product,
)
from bot.filters.custom import ChatTypeFilter, IsAdmin
from bot.keyboards.inline import get_inline_kbd
from bot.keyboards.reply import get_keyboard
from bot.utils.logging_config import logger

router = Router()
router.message.filter(ChatTypeFilter(chat_types=['private']), IsAdmin())


ADMIN_KB = get_keyboard(
    'Добавить товар',
    'Ассортимент',
    'Добавить/изменить баннер',
    placeholder='Выберите действие',
    adjust_values=(2, 1),
)


class AddProduct(StatesGroup):
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()

    texts = {
        'AddProduct:name': 'Введите название:',
        'AddProduct:description': 'Введите описание:',
        'AddProduct:category': 'Выберите категорию',
        'AddProduct:price': 'Введите стоимость:',
        'AddProduct:image': 'Добавьте изображение:',
    }


class AddBanner(StatesGroup):
    image = State()


@router.message(StateFilter(None), F.text == 'Добавить/изменить баннер')
async def add_banner_image(message: types.Message, state: FSMContext, session: AsyncSession):
    page_names = [page.name for page in await orm_get_info_pages(session)]
    await message.answer(
        'Отправьте изображение баннера.\nВ описании укажите, для какой страницы:'
        f'\n{", ".join(page_names)}'
    )
    await state.set_state(AddBanner.image)


@router.message(AddBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip().capitalize()
    page_names = [page.name for page in await orm_get_info_pages(session)]
    logger.debug('Page names: {}', page_names)
    if for_page not in page_names:
        await message.answer(
            'Отправьте изображение снова и введите <b>корректное</b> название из списка:'
            f'\n{", ".join(page_names)}'
        )
        return
    await orm_change_banner_image(session, for_page, image_id)
    await message.answer('Баннер добавлен/изменен.')
    await state.clear()


@router.message(AddBanner.image, ~(F.text.lower() == 'отмена'))
async def add_banner_fallback(message: types.Message):
    await message.answer('Попробуйте отправить изображение снова')


@router.message(Command('admin'))
async def add_product(message: types.Message):
    await message.answer('Что хотите сделать?', reply_markup=ADMIN_KB)


@router.message(F.text == 'Ассортимент')
async def choose_category(message: types.Message, session: AsyncSession):
    categories = await orm_get_categories(session)
    buttons = {category.name: f'category_{category.id}' for category in categories}
    await message.answer('Выберите категорию', reply_markup=get_inline_kbd(buttons=buttons))


@router.callback_query(F.data.startswith('category_'))
async def get_products(callback: types.CallbackQuery, session: AsyncSession):
    category_id = int(callback.data.split('_')[-1])
    await callback.message.answer(text='Список товаров:')
    for product in await orm_get_products(session, category_id):
        await callback.message.answer_photo(
            product.image,
            caption=f'<strong>{product.name}</strong>\n'
            f'{product.description}\nСтоимость: {product.price}',
            reply_markup=get_inline_kbd(
                buttons={
                    'Изменить': f'update_{product.id}',
                    'Удалить': f'delete_{product.id}',
                }
            ),
        )


@router.callback_query(StateFilter(None), F.data.startswith('update_'))
async def update_product(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    product_id = int(callback.data.split('_')[-1])
    product_to_change = await orm_get_product(session, product_id)
    await state.update_data(**product_to_change.as_dict())
    await callback.message.answer('Введите название товара:')
    await callback.answer()
    await state.set_state(AddProduct.name)


@router.callback_query(F.data.startswith('delete_'))
async def delete_product(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split('_')[-1]
    await orm_delete_product(session, int(product_id))
    await callback.message.answer('Товар удалён')
    await callback.answer()


@router.message(StateFilter(None), F.text == 'Добавить товар')
async def create_product(message: types.Message, state: FSMContext):
    await message.answer('Введите название товара', reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)


@router.message(StateFilter('*'), Command('отмена'))
@router.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer('Действия отменены', reply_markup=ADMIN_KB)


@router.message(StateFilter('*'), Command('назад'))
@router.message(StateFilter('*'), F.text.casefold() == 'назад')
async def back_handler(message: types.Message, state: FSMContext, session: AsyncSession):
    current_state = await state.get_state()
    if current_state == AddProduct.name:
        await message.answer('Предыдущего шага нет. Введите название товара или напишите "отмена"')
        return
    elif current_state == AddProduct.price:
        await state.set_state(AddProduct.category)
        categories = await orm_get_categories(session)
        buttons = {category.name: str(category.id) for category in categories}
        await message.answer(
            f'Вы вернулись к предыдущему шагу\n{AddProduct.texts[AddProduct.category.state]}',
            reply_markup=get_inline_kbd(buttons=buttons),
        )
        return
    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            logger.debug('Предыдущее состояние: {}', previous.state)
            await state.set_state(previous)
            await message.answer(
                f'Вы вернулись к предыдущему шагу\n{AddProduct.texts[previous.state]}'
            )
            return
        previous = step


@router.message(AddProduct.name, or_f(F.text, F.text == '.'))
async def add_name(message: types.Message, state: FSMContext):
    if message.text != '.':
        await state.update_data(name=message.text)
    await message.answer('Введите описание товара:')
    await state.set_state(AddProduct.description)


@router.message(AddProduct.name)
async def add_name_fallback(message: types.Message, state: FSMContext):
    await message.answer('Вы ввели недопустимые данные. Введите название товара:')


@router.message(AddProduct.description, or_f(F.text, F.text == '.'))
async def add_description(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text != '.':
        await state.update_data(description=message.text)
    categories = await orm_get_categories(session)
    buttons = {category.name: str(category.id) for category in categories}
    await message.answer('Введите категорию товара:', reply_markup=get_inline_kbd(buttons=buttons))
    await state.set_state(AddProduct.category)


@router.message(AddProduct.description)
async def add_description_fallback(message: types.Message):
    await message.answer('Вы ввели недопустимые данные. Введите описание товара:')


@router.callback_query(AddProduct.category)
async def category_choice(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    if int(callback.data) in [category.id for category in await orm_get_categories(session)]:
        await callback.answer()
        await state.update_data(category_id=int(callback.data))
        await callback.message.answer('Введите стоимость товара:')
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer('Выберите категорию из кнопок')
        await callback.answer()


@router.message(AddProduct.price, or_f(F.text, F.text == '.'))
async def add_price(message: types.Message, state: FSMContext):
    if message.text != '.':
        try:
            price = float(message.text)
            await state.update_data(price=price)
        except ValueError:
            await message.answer('Введите корректную стоимость')
            return
    await message.answer('Загрузите изображение товара:')
    await state.set_state(AddProduct.image)


@router.message(AddProduct.price)
async def add_price_fallback(message: types.Message):
    await message.answer('Вы ввели недопустимые данные. Введите стоимость товара:')


@router.message(AddProduct.image, or_f(F.photo, F.text == '.'))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    product = await state.get_data()

    if (product_id := product.get('id')) is not None:
        await orm_update_product(session, product_id, product)
        await message.answer('Товар обновлён', reply_markup=ADMIN_KB)
    else:
        await orm_add_product(session, product)
        logger.debug('Добавленный товар: {}', product)
        await message.answer('Товар добавлен', reply_markup=ADMIN_KB)
    await state.clear()


@router.message(AddProduct.image)
async def add_image_fallback(message: types.Message):
    await message.answer('Вы ввели недопустимые данные. Загрузите изображение товара:')

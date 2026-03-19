from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.crud import (
    decrease_items_in_cart,
    orm_add_category,
    orm_add_product,
    orm_add_to_cart,
    orm_add_user,
    orm_clear_cart,
    orm_create_categories,
    orm_delete_category,
    orm_delete_from_cart,
    orm_delete_product,
    orm_get_categories,
    orm_get_product,
    orm_get_products,
    orm_get_user_products,
    orm_update_product,
)

# --- Вспомогательные функции ---


async def create_category(session: AsyncSession, name: str = 'Тестовая') -> int:
    await orm_add_category(session, name)
    categories = await orm_get_categories(session)
    return next(c.id for c in categories if c.name == name)


async def create_product(session: AsyncSession, category_id: int, name: str = 'Товар') -> int:
    await orm_add_product(session, {
        'name': name,
        'description': 'Описание',
        'price': 100.0,
        'image': 'img.jpg',
        'category_id': category_id,
    })
    products = await orm_get_products(session, category_id)
    return next(p.id for p in products if p.name == name)


async def create_user(session: AsyncSession, user_id: int = 1):
    await orm_add_user(session, user_id, first_name='Тест')
    await session.commit()


# --- Категории ---

async def test_create_categories_once(session):
    await orm_create_categories(session, ['А', 'Б'])
    await orm_create_categories(session, ['В'])
    categories = await orm_get_categories(session)
    assert len(categories) == 2


async def test_add_new_category(session):
    await orm_add_category(session, 'Новая')
    categories = await orm_get_categories(session)
    assert any(c.name == 'Новая' for c in categories)


async def test_add_category_reactivates_inactive(session):
    category_id = await create_category(session, 'Реактивируемая')
    await orm_delete_category(session, category_id)

    active = await orm_get_categories(session)
    assert not any(c.name == 'Реактивируемая' for c in active)

    await orm_add_category(session, 'Реактивируемая')
    active = await orm_get_categories(session)
    assert any(c.name == 'Реактивируемая' for c in active)


async def test_delete_category_soft(session):
    category_id = await create_category(session, 'Удаляемая')
    await orm_delete_category(session, category_id)
    categories = await orm_get_categories(session)
    assert not any(c.name == 'Удаляемая' for c in categories)


async def test_get_only_active_categories(session):
    id1 = await create_category(session, 'Активная')
    await create_category(session, 'Неактивная')
    await orm_delete_category(session, id1)

    active = await orm_get_categories(session)
    names = [c.name for c in active]
    assert 'Неактивная' in names
    assert 'Активная' not in names


# --- Товары ---

async def test_add_and_get_product(session):
    cat_id = await create_category(session)
    product_id = await create_product(session, cat_id, 'Тестовый товар')
    product = await orm_get_product(session, product_id)
    assert product.name == 'Тестовый товар'
    assert product.price == 100.0


async def test_get_products_by_category(session):
    cat1 = await create_category(session, 'Кат 1')
    cat2 = await create_category(session, 'Кат 2')
    await create_product(session, cat1, 'Товар А')
    await create_product(session, cat1, 'Товар Б')
    await create_product(session, cat2, 'Товар В')

    products = await orm_get_products(session, cat1)
    assert len(products) == 2
    assert all(p.category_id == cat1 for p in products)


async def test_update_product(session):
    cat_id = await create_category(session)
    product_id = await create_product(session, cat_id)

    await orm_update_product(session, product_id, {
        'name': 'Обновлённый',
        'description': 'Новое описание',
        'price': 250.0,
        'image': 'new.jpg',
    })
    product = await orm_get_product(session, product_id)
    assert product.name == 'Обновлённый'
    assert float(product.price) == 250.0


async def test_delete_product(session):
    cat_id = await create_category(session)
    product_id = await create_product(session, cat_id)

    await orm_delete_product(session, product_id)
    assert await orm_get_product(session, product_id) is None


# --- Пользователь ---

async def test_add_user_creates_cart(session):
    await create_user(session, user_id=42)
    # проверяем через корзину — если пользователь создан, корзина тоже должна быть
    items = await orm_get_user_products(session, 42)
    assert items == []


async def test_add_user_idempotent(session):
    await create_user(session, user_id=5)
    await create_user(session, user_id=5)  # повторный вызов не должен упасть
    items = await orm_get_user_products(session, 5)
    assert items == []


# --- Корзина ---

async def test_add_to_cart_new_item(session):
    cat_id = await create_category(session)
    product_id = await create_product(session, cat_id)
    await create_user(session)

    amount = await orm_add_to_cart(session, user_id=1, product_id=product_id)
    assert amount == 1

    items = await orm_get_user_products(session, 1)
    assert len(items) == 1
    assert items[0].product_id == product_id


async def test_add_to_cart_increments_quantity(session):
    cat_id = await create_category(session)
    product_id = await create_product(session, cat_id)
    await create_user(session)

    await orm_add_to_cart(session, user_id=1, product_id=product_id)
    amount = await orm_add_to_cart(session, user_id=1, product_id=product_id)
    assert amount == 2

    items = await orm_get_user_products(session, 1)
    assert len(items) == 1
    assert items[0].quantity == 2


async def test_delete_from_cart(session):
    cat_id = await create_category(session)
    product_id = await create_product(session, cat_id)
    await create_user(session)
    await orm_add_to_cart(session, user_id=1, product_id=product_id)

    await orm_delete_from_cart(session, user_id=1, product_id=product_id)
    items = await orm_get_user_products(session, 1)
    assert items == []


async def test_clear_cart(session):
    cat_id = await create_category(session)
    p1 = await create_product(session, cat_id, 'П1')
    p2 = await create_product(session, cat_id, 'П2')
    await create_user(session)
    await orm_add_to_cart(session, user_id=1, product_id=p1)
    await orm_add_to_cart(session, user_id=1, product_id=p2)

    await orm_clear_cart(session, user_id=1)
    items = await orm_get_user_products(session, 1)
    assert items == []


async def test_decrease_items_reduces_quantity(session):
    cat_id = await create_category(session)
    product_id = await create_product(session, cat_id)
    await create_user(session)
    await orm_add_to_cart(session, user_id=1, product_id=product_id)
    await orm_add_to_cart(session, user_id=1, product_id=product_id)

    quantity = await decrease_items_in_cart(session, user_id=1, product_id=product_id)
    assert quantity == 1


async def test_decrease_items_removes_when_one_left(session):
    cat_id = await create_category(session)
    product_id = await create_product(session, cat_id)
    await create_user(session)
    await orm_add_to_cart(session, user_id=1, product_id=product_id)

    await decrease_items_in_cart(session, user_id=1, product_id=product_id)
    items = await orm_get_user_products(session, 1)
    assert items == []


async def test_decrease_items_nonexistent_product(session):
    await create_user(session)
    result = await decrease_items_in_cart(session, user_id=1, product_id=999)
    assert result is None

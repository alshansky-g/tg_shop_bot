from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from bot.database.models import Banner, Cart, CartProduct, Category, Product, User


# Баннеры
async def orm_add_banner_description(session: AsyncSession, data: dict):
    banner = await session.scalar(select(Banner))
    if banner is None:
        session.add_all(
            [Banner(name=name, description=description) for name, description in data.items()]
        )
        await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    await session.execute(update(Banner).where(Banner.name == name).values(image=image))
    await session.commit()


async def orm_get_banner(session: AsyncSession, name: str):
    banner = await session.scalar(select(Banner).where(Banner.name == name))
    return banner


async def orm_get_info_pages(session: AsyncSession):
    pages_info = await session.scalars(select(Banner))
    return pages_info.all()


# Категории
async def orm_create_categories(session: AsyncSession, categories: list):
    category = await session.scalar(select(Category))
    if category is None:
        session.add_all([Category(name=name) for name in categories])
        await session.commit()


async def orm_get_categories(session: AsyncSession):
    categories = await session.scalars(select(Category))
    return categories.all()


async def orm_add_category(session: AsyncSession, category_name: str):
    session.add(Category(name=category_name))
    await session.commit()


async def orm_seed_products(
    session: AsyncSession,
    products: list[tuple[str, str, float, str]],
    placeholder_image: str,
):
    existing = await session.scalar(select(Product))
    if existing is not None:
        return
    category_map = {c.name: c.id for c in (await session.scalars(select(Category))).all()}
    session.add_all(
        [
            Product(
                name=name,
                description=description,
                price=price,
                image=placeholder_image,
                category_id=category_map[category_name],
            )
            for name, description, price, category_name in products
            if category_name in category_map
        ]
    )
    await session.commit()


# Админка Товары
async def orm_add_product(session: AsyncSession, product_fields: dict):
    product = Product(**product_fields)
    session.add(product)
    await session.commit()


async def orm_get_products(session: AsyncSession, category_id: int):
    products = await session.scalars(select(Product).where(Product.category_id == category_id))
    return products.all()


async def orm_get_product(session: AsyncSession, product_id: int):
    product = await session.get(Product, product_id)
    return product


async def orm_update_product(session: AsyncSession, product_id: int, data: dict):
    await session.execute(
        update(Product)
        .where(Product.id == product_id)
        .values(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            image=data['image'],
        )
    )
    await session.commit()


async def orm_delete_product(session: AsyncSession, product_id: int):
    await session.execute(delete(Product).where(Product.id == product_id))
    await session.commit()


# Создание пользователя
async def orm_add_user(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
):
    user = await session.get(User, user_id)
    if user is None:
        user = User(id=user_id, first_name=first_name, last_name=last_name, phone=phone)
        user.cart = Cart(id=user_id)
        session.add(user)


# Работа с корзиной
async def orm_add_to_cart(session: AsyncSession, user_id: int, product_id: int):
    cart = await session.get(CartProduct, (product_id, user_id))
    amount = 1
    if cart:
        cart.quantity += 1
        amount = cart.quantity
    else:
        session.add(CartProduct(cart_id=user_id, product_id=product_id, quantity=1))
    return amount


async def orm_get_user_products(session: AsyncSession, user_id: int):
    query = (
        select(CartProduct)
        .options(joinedload(CartProduct.product))
        .where(CartProduct.cart_id == user_id)
    )
    cart = await session.scalars(query)
    return cart.all()


async def orm_delete_from_cart(session: AsyncSession, user_id: int, product_id: int):
    await session.execute(
        delete(CartProduct).where(
            CartProduct.cart_id == user_id, CartProduct.product_id == product_id
        )
    )
    await session.commit()
    return 0


async def decrease_items_in_cart(session: AsyncSession, user_id: int, product_id: int):
    product = await session.scalar(
        select(CartProduct).where(
            CartProduct.cart_id == user_id, CartProduct.product_id == product_id
        )
    )
    if product is None:
        return
    quantity = product.quantity - 1
    if product.quantity > 1:
        product.quantity -= 1
    else:
        await orm_delete_from_cart(session, user_id, product_id)
    await session.commit()
    return quantity

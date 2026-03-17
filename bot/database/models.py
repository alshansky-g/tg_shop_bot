from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        fields = ', '.join(
            [
                f'{k}={v}'
                for k, v in self.__dict__.items()
                if not any(k.startswith(prefix) for prefix in ['_', 'cr', 'up'])
            ]
        )
        return f'<{type(self).__name__}: {fields}>'


class Banner(Base):
    __tablename__ = 'banners'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=True)
    phone: Mapped[str] = mapped_column(String(13), nullable=True)

    cart: Mapped['Cart'] = relationship(back_populates='user', uselist=False)


class Cart(Base):
    __tablename__ = 'carts'

    id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)

    user: Mapped['User'] = relationship(back_populates='cart')
    products_assoc: Mapped[list['CartProduct']] = relationship(
        back_populates='cart', cascade='all, delete-orphan'
    )
    products: Mapped[list['Product']] = association_proxy('products_assoc', 'product')


class CartProduct(Base):
    __tablename__ = 'cart_product'

    product_id: Mapped[int] = mapped_column(
        ForeignKey('products.id', ondelete='CASCADE'), primary_key=True
    )
    cart_id: Mapped[int] = mapped_column(
        ForeignKey('carts.id', ondelete='CASCADE'), primary_key=True
    )
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)

    cart: Mapped['Cart'] = relationship(back_populates='products_assoc')
    product: Mapped['Product'] = relationship(back_populates='carts')


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    image: Mapped[str] = mapped_column(String(150))
    category_id: Mapped[int] = mapped_column(
        ForeignKey('categories.id', ondelete='CASCADE'), nullable=False
    )

    category: Mapped['Category'] = relationship(backref='products')

    carts: Mapped[list['CartProduct']] = relationship(back_populates='product')

    def as_dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

from aiogram.utils.formatting import Bold, as_list, as_marked_section

categories = ['Еда', 'Напитки']

info_pages_description = {
    'Главная': 'Добро пожаловать',
    'О нас': "Онлайн-шоп 'Buy From Us'\nРежим работы - 24/7",
    'Оплата': as_marked_section(
        Bold('Варианты оплаты:'),
        'Картой в боте',
        'При получении: карта/наличные',
        'В заведении',
        marker='✅ ',
    ).as_html(),
    'Доставка': as_list(
        as_marked_section(Bold('Варианты доставки^'), 'Курьер', 'Самовывоз', marker='✅ '),
        as_marked_section(Bold('Нельзя:'), 'Почта', 'Голуби', marker='❌ '),
        sep='\n-------------------------------\n',
    ).as_html(),
    'Категории': 'Категории:',
    'Корзина': 'Корзина пуста.',
}

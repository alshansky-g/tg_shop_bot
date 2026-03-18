from aiogram.types import BotCommand

user_commands = [
    BotCommand(command='menu', description='Посмотреть меню'),
    BotCommand(command='about', description='О нас'),
    BotCommand(command='payment', description='Варианты оплаты'),
    BotCommand(command='shipping', description='Варианты доставки'),
]

admin_commands = [
    BotCommand(command='admin', description='Админ команды'),
]

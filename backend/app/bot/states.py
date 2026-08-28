from aiogram.fsm.state import State, StatesGroup

class ProductRegistrationFSM(StatesGroup):
    title = State()
    cost_price = State()
    units_per_pack = State()
    barcode_value = State()
    consumer_price = State()
    confirm = State()
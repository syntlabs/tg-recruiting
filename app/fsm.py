from aiogram.fsm.state import StatesGroup, State


# FSMs for clients
class FSMResumeForm(StatesGroup):
    in_process = State()


class FSMDialogueWithStaff(StatesGroup):
    in_process = State()


# FSMs for staff
class FSMAddVacancy(StatesGroup):
    in_process = State()


class FSMEditVacancy(StatesGroup):
    in_process = State()


class FSMDialogueWithUser(StatesGroup):
    in_process = State()

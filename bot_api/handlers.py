import os.path
from typing import Union, Optional

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram_calendar.simple_calendar import SimpleCalendar, SimpleCalendarCallback

from changed_calendar.simple_calendar import SimpleCalendar, SimpleCalendarCallback
from bot_api.states import Statements
from bot_api.server_requests import Request
from bot_api.menu_items import (Customer, EmployeeMenu, AdminMenu, CustomersMenu, AllCustomers, AddCustomer,
                                DeleteCustomer, EditCustomer)
from google_drive_api import google_drive

router = Router()


# Кнопка старта. Нужна только для того, чтобы не появлялась огромная кнопка НАЧАТЬ в телеграмме
@router.message(CommandStart())
async def start_command(message_or_callback: Union[Message, CallbackQuery], state: FSMContext) -> Message:
    return await message_or_callback.answer(text='Введите команду /employee для старта работы:)')


# Меню для сотрудников
@router.message(Command('employee'))
@router.callback_query(F.data == 'employee_menu', Statements.EMPLOYEE_MENU)
async def employee_menu(message_or_callback: Union[Message, CallbackQuery], state: FSMContext) -> Message:
    await state.set_state(Statements.EMPLOYEE_MENU)
    await state.set_data({})
    if isinstance(message_or_callback, CallbackQuery):
        message: Message = message_or_callback.message
    else:
        message: Message = message_or_callback
        if not EmployeeMenu.is_employee(telegram_id=message.from_user.id):
            return await message.answer(text=EmployeeMenu.employee_menu_restriction)
        else:
            await state.set_state(Statements.EMPLOYEE_MENU)
    return await message.answer(
        text=EmployeeMenu.employee_menu_header,
        reply_markup=EmployeeMenu.create_inline_keyboard(
            buttons=EmployeeMenu.employee_menu_buttons,
            callbacks=EmployeeMenu.employee_menu_callbacks
        )
    )


@router.callback_query(F.data == 'customers_menu', Statements.EMPLOYEE_MENU)
async def customers_menu(callback_query: CallbackQuery, state: FSMContext) -> Message:
    return await callback_query.message.answer(
        text=CustomersMenu.customer_menu_header,
        reply_markup=CustomersMenu.create_inline_keyboard(
            buttons=CustomersMenu.customer_menu_buttons,
            callbacks=CustomersMenu.customer_menu_callbacks
        )
    )


@router.callback_query(F.data == 'all_customers')
async def all_customers(callback_query: CallbackQuery, state: FSMContext) -> Message:
    await state.set_state(Statements.WAITING_CUSTOMER_CHOICE)
    return await callback_query.message.answer(
        text=AllCustomers.all_customers_header,
        reply_markup=AllCustomers.create_inline_keyboard(
            buttons=AllCustomers.update_buttons(),
            callbacks=AllCustomers.update_callbacks()
        )
    )


@router.callback_query(Statements.WAITING_CUSTOMER_CHOICE)
@router.callback_query(F.data == Customer.customer_menu_returning)
async def customer_menu(callback_query: CallbackQuery, state: FSMContext) -> Message:
    if callback_query.data == Customer.customer_menu_returning:
        current_customer = (await state.get_data()).get('current_customer')
    elif callback_query.data != AllCustomers.back_customers_menu_callback:
        current_customer = Customer(callback_query.data)
        await state.set_data({'current_customer': current_customer})
    else:
        current_customer = None
    if current_customer:
        await state.set_state(Statements.WAITING_CUSTOMER_MENU_CHOICE)
        return await callback_query.message.answer(
            text=current_customer.header_customer(main=True),
            reply_markup=current_customer.create_inline_keyboard_with_urls()
        )
    else:
        await state.set_state(Statements.EMPLOYEE_MENU)
        return await customers_menu(callback_query, state)


@router.callback_query(F.data == 'autoload', Statements.WAITING_CUSTOMER_MENU_CHOICE)
async def autoload(callback_query: CallbackQuery, state: FSMContext) -> Message:
    current_customer: Customer = (await state.get_data()).get('current_customer')
    return await callback_query.message.answer(
        text=current_customer.header_customer(autoload=True),
        reply_markup=current_customer.create_inline_keyboard(
            buttons=current_customer.autoload_menu_buttons,
            callbacks=current_customer.autoload_menu_callbacks
        )
    )


@router.callback_query(F.data == 'get_link', Statements.WAITING_CUSTOMER_MENU_CHOICE)
async def get_link(callback_query: CallbackQuery, state: FSMContext) -> Message:
    current_customer: Customer = (await state.get_data()).get('current_customer')
    return await callback_query.message.answer(
        text=current_customer.autoload_menu_get_link.format(
            title=current_customer.title,
            url=current_customer.get_autoload_link()
        ),
        reply_markup=current_customer.create_inline_keyboard(
            buttons=[current_customer.back_button],
            callbacks=[current_customer.autoload_menu_back_button]
        )
    )


@router.callback_query(F.data == 'delete_link', Statements.WAITING_CUSTOMER_MENU_CHOICE)
async def delete_link(callback_query: CallbackQuery, state: FSMContext) -> Message:
    current_customer: Customer = (await state.get_data()).get('current_customer')
    return await callback_query.message.answer(
        text=current_customer.delete_autoload_link(),
        reply_markup=current_customer.create_inline_keyboard(
            buttons=[current_customer.back_button],
            callbacks=[current_customer.autoload_menu_back_button]
        )
    )


@router.callback_query(F.data == 'update_feed', Statements.WAITING_CUSTOMER_MENU_CHOICE)
async def update_feed(callback_query: CallbackQuery, state: FSMContext) -> Optional[Message]:
    current_customer: Customer = (await state.get_data()).get('current_customer')
    message_to_delete = await callback_query.message.answer(text='Подождите...')
    data = google_drive.run_file_updating(file_name=current_customer.title)

    if data:
        updating = Request.update_feed(company_name=current_customer.title, data=data)
        await message_to_delete.delete()
        return await callback_query.message.answer(
            text=updating,
            reply_markup=current_customer.create_inline_keyboard(
                buttons=[current_customer.back_button],
                callbacks=[current_customer.autoload_menu_back_button]
            )
        )
    else:
        await message_to_delete.delete()
        return await callback_query.message.answer(
            text=current_customer.autoload_menu_no_file_in_google_doc.format(
                file_name=current_customer.title
            ),
            reply_markup=current_customer.create_inline_keyboard(
                buttons=[current_customer.back_button],
                callbacks=[current_customer.autoload_menu_back_button]
            )
        )


@router.callback_query(F.data == 'get_autoload_report', Statements.WAITING_CUSTOMER_MENU_CHOICE)
async def update_feed(callback_query: CallbackQuery, state: FSMContext) -> Optional[Message]:
    current_customer: Customer = (await state.get_data()).get('current_customer')
    report = current_customer.get_autoload_report()
    return await callback_query.message.answer(
        text=report,
        reply_markup=current_customer.create_inline_keyboard(
            buttons=[current_customer.back_button],
            callbacks=[current_customer.autoload_menu_back_button]
        )
    )


@router.callback_query(F.data == 'statistic', Statements.WAITING_CUSTOMER_MENU_CHOICE)
async def statistic(callback_query: CallbackQuery, state: FSMContext) -> Message:
    current_customer: Customer = (await state.get_data()).get('current_customer')
    await state.set_state(Statements.WAITING_STATISTIC_PERIOD)
    return await callback_query.message.answer(
        text=current_customer.statistic_header,
        reply_markup=current_customer.create_inline_keyboard(
            buttons=current_customer.statistic_menu_buttons,
            callbacks=current_customer.statistic_menu_callbacks
        )
    )


@router.callback_query(Statements.WAITING_STATISTIC_PERIOD)
async def statistic_period(callback_query: CallbackQuery, state: FSMContext) -> None:
    current_customer: Customer = (await state.get_data()).get('current_customer')
    if callback_query.data != current_customer.customer_menu_returning:
        await state.set_state(Statements.WAITING_FOR_DATE_FROM)
        await nav_cal_handler(callback_query, state)
    else:
        await state.set_state(Statements.WAITING_CUSTOMER_MENU_CHOICE)
        await statistic(callback_query, state)


@router.message(lambda x: x.text in ['day', 'week', 'month'])
async def nav_cal_handler(callback_query: CallbackQuery, state: FSMContext) -> Message:
    if callback_query.data in ['day', 'week', 'month']:
        await state.update_data({'period': callback_query.data})
    current_state = await state.get_state()
    if current_state == Statements.WAITING_FOR_DATE_FROM:
        choice_of_day = Customer.statistic_date_from
    else:
        choice_of_day = Customer.statistic_date_to
    return await callback_query.message.answer(
        text=choice_of_day,
        reply_markup=await SimpleCalendar().start_calendar()
    )


@router.callback_query(SimpleCalendarCallback.filter())
async def calendar_handler(callback_query: CallbackQuery, callback_data: SimpleCalendarCallback,
                           state: FSMContext) -> Message:
    calendar = SimpleCalendar()
    calendar.set_dates_range(Customer.statistic_calendar_date_from,
                             Customer.statistic_calendar_date_to)
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        current_state = await state.get_state()
        if current_state == Statements.WAITING_FOR_DATE_FROM:
            await state.set_state(Statements.WAITING_FOR_DATE_TO)
            await state.update_data({'date_from': date.strftime(Customer.statistic_dates_format)})
            await nav_cal_handler(callback_query, state)
        else:
            current_customer: Customer = (await state.get_data()).get('current_customer')
            await state.set_state(Statements.THE_CHOICE_IS_MADE)
            await state.update_data({'date_to': date.strftime(Customer.statistic_dates_format)})
            return await callback_query.message.answer(
                text=Customer.statistic_dates_choice.format(
                    date_from=(await state.get_data()).get('date_from'),
                    date_to=(await state.get_data()).get('date_to')),
                reply_markup=current_customer.create_inline_keyboard(
                    buttons=current_customer.yes_no_buttons,
                    callbacks=current_customer.yes_no_callbacks
                )
            )


@router.callback_query(Statements.THE_CHOICE_IS_MADE)
async def validate_the_dates_choice(callback_query: CallbackQuery, state: FSMContext) -> Message:
    current_data = await state.get_data()
    current_customer: Customer = current_data.get('current_customer')
    new_data = {'current_customer': current_customer}
    if callback_query.data == 'yes':
        chosen_dates_statistic = current_customer.get_statistic(
            date_from=(await state.get_data()).get('date_from'),
            date_to=(await state.get_data()).get('date_to'),
            period=(await state.get_data()).get('period')
        )

        await state.set_state(Statements.WAITING_CUSTOMER_MENU_CHOICE)
        if chosen_dates_statistic is not None:
            file_to_send = current_customer.create_exel_file_from_statistic(data=chosen_dates_statistic)

            if file_to_send:
                path_to_file = os.path.abspath(file_to_send)
                message_to_delete = await callback_query.message.answer_document(
                    document=FSInputFile(path_to_file),
                    reply_markup=current_customer.create_inline_keyboard(
                        buttons=[current_customer.back_button],
                        callbacks=[current_customer.statistic_back_callback]
                    )
                )
                current_customer.delete_temp_exel_file(path_to_file)
                return message_to_delete
            else:
                return await callback_query.message.answer(
                    text=current_customer.statistic_empty_data,
                    reply_markup=current_customer.create_inline_keyboard(
                        buttons=[current_customer.back_button],
                        callbacks=[current_customer.statistic_back_callback]
                    )
                )
        else:
            return await callback_query.message.answer(
                text=current_customer.statistic_access_problem,
                reply_markup=current_customer.create_inline_keyboard(
                    buttons=[current_customer.back_button],
                    callbacks=[current_customer.statistic_back_callback]
                )
            )
    else:
        await state.set_data(new_data)
        await state.set_state(Statements.WAITING_FOR_DATE_FROM)
        await nav_cal_handler(callback_query, state)


@router.callback_query(F.data == 'add_customer')
async def add_customer(callback_query: CallbackQuery, state: FSMContext) -> Message:
    await state.set_state(Statements.WAITING_FOR_TITLE)
    return await callback_query.message.answer(
        text=AddCustomer.common_header.format(item=AddCustomer.title_item),
        reply_markup=AddCustomer.create_inline_keyboard(
            buttons=[AddCustomer.back_button],
            callbacks=[AddCustomer.back_customers_menu_callback]
        )
    )


@router.callback_query(F.data == AddCustomer.back_customers_menu_callback, Statements.WAITING_FOR_TITLE)
@router.message(Statements.WAITING_FOR_TITLE)
async def add_customer_title(
        message_or_callback: Union[Message, CallbackQuery], state: FSMContext
) -> Message:
    if isinstance(message_or_callback, CallbackQuery):
        callback_query: CallbackQuery = message_or_callback
        await state.set_state(Statements.EMPLOYEE_MENU)
        return await customers_menu(callback_query, state)
    else:
        current_state = await state.get_state()
        message: Message = message_or_callback
        if current_state == Statements.WAITING_FOR_TITLE:
            add_customer_instance = AddCustomer(title=message.text)
            await state.set_data({'add_customer_instance': add_customer_instance})
        await state.set_state(Statements.WAITING_FOR_AVITO_ID)
        return await message.answer(
            text=AddCustomer.common_header.format(
                item=AddCustomer.avito_id_item
            )
        )


@router.message(Statements.WAITING_FOR_AVITO_ID)
async def add_customer_avito_id(message: Message, state: FSMContext) -> Message:
    add_customer_instance: AddCustomer = (await state.get_data()).get('add_customer_instance')
    is_valid_avito_id = add_customer_instance.set_avito_id(message.text)
    if is_valid_avito_id is None:
        message_to_delete = await message.answer(text=AddCustomer.not_valid_avito_id)
        return message_to_delete
    else:
        await state.set_state(Statements.WAITING_FOR_CLIENT_ID)
        return await message.answer(
            text=AddCustomer.common_header.format(
                item=AddCustomer.client_id_item
            )
        )


@router.message(Statements.WAITING_FOR_CLIENT_ID)
async def add_customer_client_id(message: Message, state: FSMContext) -> Message:
    add_customer_instance: AddCustomer = (await state.get_data()).get('add_customer_instance')
    add_customer_instance.set_client_id(message.text)
    await state.set_state(Statements.WAITING_FOR_CLIENT_SECRET)
    return await message.answer(text=AddCustomer.common_header.format(
        item=AddCustomer.client_secret_item
    ))


@router.message(Statements.WAITING_FOR_CLIENT_SECRET)
async def add_customer_client_secret(message: Message, state: FSMContext) -> Message:
    current_state = await state.get_state()
    if current_state == Statements.WAITING_FOR_CLIENT_SECRET:
        add_customer_instance: AddCustomer = (await state.get_data()).get('add_customer_instance')
        add_customer_instance.set_client_secret(message.text)
    await state.set_state(Statements.WAITING_FOR_CHAT_WITH_CLIENT)
    return await message.answer(text=AddCustomer.common_header.format(
        item=AddCustomer.chat_with_client_item
    ))


@router.message(Statements.WAITING_FOR_CHAT_WITH_CLIENT)
async def add_customer_chat_with_client_link(message: Message, state: FSMContext, is_redirect: bool = False) -> \
        Message:
    if not is_redirect:
        add_customer_instance: AddCustomer = (await state.get_data()).get('add_customer_instance')
        is_valid_link = add_customer_instance.set_chat_with_client_link(chat_with_client_link=message.text)
    else:
        is_valid_link = True
    if is_valid_link:
        await state.set_state(Statements.WAITING_FOR_CHAT_ABOUT_CLIENT)
        return await message.answer(text=AddCustomer.common_header.format(
            item=AddCustomer.chat_about_client_item
        ))
    else:
        return await message.answer(text=AddCustomer.not_valid_link)


@router.message(Statements.WAITING_FOR_CHAT_ABOUT_CLIENT)
async def add_customer_chat_about_client_link(message: Message, state: FSMContext) -> Message:
    add_customer_instance: AddCustomer = (await state.get_data()).get('add_customer_instance')
    is_valid_link = add_customer_instance.set_chat_about_client_link(chat_about_client_link=message.text)
    if is_valid_link:
        await state.set_state(Statements.WAITING_FOR_GOOGLE_DOC_LINK)
        return await message.answer(text=AddCustomer.common_header.format(
            item=AddCustomer.google_doc_link
        ))
    else:
        return await message.answer(text=AddCustomer.not_valid_link)


@router.message(Statements.WAITING_FOR_GOOGLE_DOC_LINK)
async def add_customer_google_doc_link(message: Message, state: FSMContext) -> Message:
    add_customer_instance: AddCustomer = (await state.get_data()).get('add_customer_instance')
    is_valid_link = add_customer_instance.set_google_doc_link(google_doc_link=message.text)
    if is_valid_link:
        await state.set_state(Statements.GOT_ALL_CLIENT_INFO)
        return await message.answer(
            text=add_customer_instance.check_data_items(),
            reply_markup=AddCustomer.create_inline_keyboard(
                buttons=AddCustomer.yes_no_buttons,
                callbacks=AddCustomer.yes_no_callbacks
            )
        )
    else:
        return await message.answer(text=AddCustomer.not_valid_link)


@router.callback_query(Statements.GOT_ALL_CLIENT_INFO)
async def add_customer_confirmation(callback_query: CallbackQuery, state: FSMContext) -> Message:
    if callback_query.data == 'yes':
        add_customer_instance: AddCustomer = (await state.get_data()).get('add_customer_instance')
        result = add_customer_instance.add_customer_to_db()
        message_to_delete = await callback_query.message.answer(
            text=result,
            reply_markup=AddCustomer.create_inline_keyboard(
                buttons=[AddCustomer.back_button],
                callbacks=[AddCustomer.back_customers_menu_callback]
            )
        )
        await state.set_state(Statements.EMPLOYEE_MENU)
        await state.set_data({})

        return message_to_delete
    else:
        await state.set_data({})
        return await add_customer(callback_query, state)


@router.callback_query(F.data == 'delete_customer')
async def delete_customer(callback_query: CallbackQuery, state: FSMContext) -> Message:
    await state.set_state(Statements.WAITING_FOR_CLIENT_TO_DELETE)
    return await callback_query.message.answer(
        text=DeleteCustomer.delete_customer_header,
        reply_markup=DeleteCustomer.create_inline_keyboard(
            buttons=DeleteCustomer.update_buttons(),
            callbacks=DeleteCustomer.update_callbacks()
        )
    )


@router.callback_query(Statements.WAITING_FOR_CLIENT_TO_DELETE)
async def deleting_customer(callback_query: CallbackQuery, state: FSMContext) -> Message:
    if callback_query.data == 'customers_menu':
        await state.set_state(Statements.EMPLOYEE_MENU)
        return await customers_menu(callback_query, state)
    else:
        message_to_delete = await callback_query.message.answer(
            text=DeleteCustomer.delete_customer(
                title=callback_query.data
            ),
            reply_markup=DeleteCustomer.create_inline_keyboard(
                buttons=[DeleteCustomer.back_button],
                callbacks=[DeleteCustomer.back_customers_menu_callback]
            )
        )

        return message_to_delete


@router.callback_query(F.data == 'edit_customer')
async def edit_customer(callback_query: CallbackQuery, state: FSMContext) -> Message:
    await state.set_state(Statements.WAITING_FOR_CLIENT_TO_EDIT)
    return await callback_query.message.answer(
        text=EditCustomer.edit_customer_header,
        reply_markup=EditCustomer.create_inline_keyboard(
            buttons=EditCustomer.update_buttons(),
            callbacks=EditCustomer.update_callbacks()
        )
    )


@router.callback_query(Statements.WAITING_FOR_CLIENT_TO_EDIT)
async def editing_customer(callback_query: CallbackQuery, state: FSMContext) -> Message:
    if callback_query.data == 'customers_menu':
        await state.set_state(Statements.EMPLOYEE_MENU)
        return await customers_menu(callback_query, state)
    else:
        edit_customer_instance: EditCustomer = EditCustomer(callback_query.data)
        await state.set_data({'edit_customer_instance': edit_customer_instance})
        await state.set_state(Statements.WAITING_FOR_FIELD_TO_EDIT)
        return await callback_query.message.answer(
            text=edit_customer_instance.represent_current_data(),
            reply_markup=edit_customer_instance.create_inline_keyboard(
                buttons=EditCustomer.edit_customer_fields_buttons,
                callbacks=EditCustomer.edit_customer_fields_callbacks
            )
        )


@router.callback_query(Statements.WAITING_FOR_FIELD_TO_EDIT)
async def editing_customer_field(callback_query: CallbackQuery, state: FSMContext) -> Message:
    if callback_query.data == 'customers_menu':
        await state.set_state(Statements.EMPLOYEE_MENU)
        return await customers_menu(callback_query, state)
    else:
        await state.set_state(Statements.WAITING_FOR_ATTRIBUTE_TO_EDIT)
        await state.update_data({'attribute_to_edit': callback_query.data})
        return await callback_query.message.answer(
            text=EditCustomer.edit_attribute_header.format(
                attribute=EditCustomer.callback_data_to_field_name(
                    attribute=callback_query.data
                )
            ),
            reply_markup=EditCustomer.create_inline_keyboard(
                buttons=[EditCustomer.back_button],
                callbacks=[EditCustomer.back_edit_customer_callback]
            )
        )


@router.message(Statements.WAITING_FOR_ATTRIBUTE_TO_EDIT)
async def editing_customer_field(message: Message, state: FSMContext) -> Message:
    edit_customer_instance: EditCustomer = (await state.get_data()).get('edit_customer_instance')
    attribute_to_edit = (await state.get_data()).get('attribute_to_edit')
    is_not_valid = edit_customer_instance.set_chosen_attribute(
        attribute=attribute_to_edit,
        value=message.text
    )
    if is_not_valid:
        return await message.answer(text=is_not_valid)
    else:
        is_success = edit_customer_instance.change_customer_in_db()
        return await message.answer(
            text=edit_customer_instance.represent_current_data(
                already_changed=True, is_success=is_success
            ),
            reply_markup=EditCustomer.create_inline_keyboard(
                buttons=[EditCustomer.back_button],
                callbacks=[EditCustomer.back_edit_customer_callback]
            )
        )


@router.callback_query(F.data == 'admin_menu', Statements.EMPLOYEE_MENU)
@router.callback_query(F.data == 'admin_menu', Statements.WAITING_FOR_NEW_ADMIN_NAME)
@router.callback_query(F.data == 'admin_menu', Statements.WAITING_FOR_ADMIN_TO_DELETE)
async def admin_menu(callback_query: CallbackQuery, state: FSMContext) -> Message:
    if AdminMenu.is_admin(telegram_id=callback_query.from_user.id):
        await state.set_state(Statements.WAITING_FOR_ADMIN_ACTION)
        return await callback_query.message.answer(
            text=AdminMenu.admin_menu_header,
            reply_markup=AdminMenu.create_inline_keyboard(
                buttons=AdminMenu.admin_menu_buttons,
                callbacks=AdminMenu.admin_menu_callbacks
            )
        )

    else:
        return await callback_query.message.answer(
            text=AdminMenu.admin_menu_restriction
        )


@router.callback_query(Statements.WAITING_FOR_ADMIN_ACTION)
async def admin_menu_action(callback_query: CallbackQuery, state: FSMContext) -> Message:
    if callback_query.data == 'employee_menu':
        await state.set_state(Statements.EMPLOYEE_MENU)
        return await employee_menu(callback_query, state)
    elif callback_query.data == 'add_employee':
        await state.set_state(Statements.WAITING_FOR_NEW_ADMIN_NAME)
        return await callback_query.message.answer(
            text=AdminMenu.adding_new_admin_name,
            reply_markup=AdminMenu.create_inline_keyboard(
                buttons=[AdminMenu.back_button],
                callbacks=[AdminMenu.back_to_admin_menu_callback]
            )
        )
    else:
        await state.set_state(Statements.WAITING_FOR_ADMIN_TO_DELETE)
        return await callback_query.message.answer(
            text=AdminMenu.admin_name_to_delete,
            reply_markup=AdminMenu.create_inline_keyboard(
                buttons=AdminMenu.update_buttons(),
                callbacks=AdminMenu.update_callbacks()
            )
        )


@router.message(Statements.WAITING_FOR_NEW_ADMIN_NAME)
@router.callback_query(Statements.WAITING_FOR_NEW_ADMIN_NAME)
async def adding_admin_name(message_or_callback: Union[Message, CallbackQuery], state: FSMContext) -> Message:
    if isinstance(message_or_callback, CallbackQuery):
        callback_query: CallbackQuery = message_or_callback
        await state.set_state(Statements.WAITING_FOR_ADMIN_ACTION)
        return await admin_menu_action(callback_query, state)
    else:
        message: Message = message_or_callback
        new_admin_instance: AdminMenu = AdminMenu(admin_name=message.text)
        await state.set_data({'new_admin_instance': new_admin_instance})
        await state.set_state(Statements.WAITING_FOR_NEW_ADMIN_TG_ID)
        return await message.answer(text=AdminMenu.adding_new_admin_id)


@router.message(Statements.WAITING_FOR_NEW_ADMIN_TG_ID)
async def admin_menu_tg_id(message: Message, state: FSMContext) -> Message:
    if AdminMenu.validate_tg_id(tg_id=message.text):
        new_admin_instance: AdminMenu = (await state.get_data()).get('new_admin_instance')
        new_admin_instance.set_admin_id(message.text)
        await state.set_data({})
        await state.set_state(Statements.EMPLOYEE_MENU)
        return await message.answer(
            text=new_admin_instance.add_new_admin_to_db(),
            reply_markup=new_admin_instance.create_inline_keyboard(
                buttons=[new_admin_instance.back_button],
                callbacks=[new_admin_instance.back_to_admin_menu_callback]
            )
        )
    else:
        return await message.answer(text=AdminMenu.not_valid_tg_id)


@router.callback_query(Statements.WAITING_FOR_ADMIN_TO_DELETE)
async def admin_menu_delete(callback_query: CallbackQuery, state: FSMContext) -> Message:
    message_to_delete = await callback_query.message.answer(
        text=AdminMenu.delete_admin_if_not_in_charge(
            admin_name=callback_query.data
        ),
        reply_markup=AdminMenu.create_inline_keyboard(
            buttons=[AdminMenu.back_button],
            callbacks=[AdminMenu.back_to_admin_menu_callback]
        )
    )
    await state.set_state(Statements.WAITING_FOR_ADMIN_ACTION)
    return message_to_delete


@router.callback_query(F.data == 'close_menu')
async def close_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()


if __name__ == '__main__':
    pass

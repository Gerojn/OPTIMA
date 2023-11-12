from Address_book import AddressBook, Record, DuplicatedPhoneError
import shlex
import sys
from pathlib import Path
import shutil
import re

from Address_book import AddressBook, Record, DuplicatedPhoneError
import shlex

from sorting import sort_folders_and_return_result

records = None

def input_error(*expected_args):
    def input_error_wrapper(func):
        def inner(*args):
            try:
                return func(*args)
            except IndexError:
                return f"Please enter {' and '.join(expected_args)}"
            except KeyError:
                return f"The record for contact {args[0]} not found. Try another contact or use help."
            except ValueError as error:
                if error.args:
                    return error.args[0]
                return f"Phone format '{args[1]}' is incorrect. Use digits only for phone number."
            except DuplicatedPhoneError as phone_error:
                return f"Phone number {phone_error.args[1]} already exists for contact {phone_error.args[0]}."
            # except AttributeError:
            #     return f"Contact {args[0]} doesn't have birthday yet."
        return inner
    return input_error_wrapper

def capitalize_user_name(func):
    def inner(*args):
        new_args = list(args)
        new_args[0] = new_args[0].title()
        return func(*new_args)
    return inner

def unknown_handler(*args):
    return f"Unknown command. Use <help>"

def help_handler():
    help_txt = ""
    def inner(*args):
        nonlocal help_txt
        if not help_txt:
            with open("help.txt") as file:            
                help_txt = "".join(file.readlines())
        return help_txt
    return inner

@capitalize_user_name
@input_error("name", "phone")
def add_handler(*args):
    user_name = args[0]
    user_phones = args[1:]
    record = records.find(user_name, True)
    if not record:
        record = Record(user_name)
        for user_phone in user_phones:
            record.add_phone(user_phone)
        records.add_record(record)
        if user_phones:
            return f"New record added for {user_name} with phone number{'s' if len(user_phones) > 1 else ''}: {'; '.join(user_phones)}."
        return f"New record added for {user_name}."
    else:
        response = []
        for user_phone in user_phones:
            record.add_phone(user_phone)
            response.append(f"New phone number {user_phone} for contact {user_name} added.")
        return "\n".join(response)

@capitalize_user_name
@input_error("name", "old_phone", "new_phone")
def change_handler(*args):
    user_name = args[0]
    old_phone = args[1]
    new_phone = args[2]
    record = records.find(user_name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Phone number for {user_name} changed from {old_phone} to {new_phone}."

@capitalize_user_name    
@input_error("name")
def birthday_handler(*args):
    user_name = args[0]
    user_birthday = args[1] if len(args) > 1 else None
    record = records.find(user_name)
    if record:
        if user_birthday:
            record.add_birthday(user_birthday)
            return f"Birthday {user_birthday} for contact {user_name} added."
        else:
            return f"{record.days_to_birthday()} days to the next {user_name}'s birthday ({record.birthday})."

@capitalize_user_name    
@input_error("name")        
def address_handler(*args):
    user_name = args[0]
    user_address = args[1] if len(args) > 1 else None
    record = records.find(user_name)
    if record:
        if user_address:
            record.add_address(user_address)
            return f"Address '{user_address}' for contact {user_name} added."
        else:
            return f"Address for contact {user_name}: {record.address}."

@capitalize_user_name    
@input_error("name")        
def email_handler(*args):
    user_name = args[0]
    user_email = args[1] if len(args) > 1 else None
    record = records.find(user_name)
    if record:
        if user_email:
            record.add_email(user_email)
            return f"Email '{user_email}' for contact {user_name} added."
        else:
            return f"Email for contact {user_name}: {record.email}."

@capitalize_user_name    
@input_error("name")
def delete_handler(*args):
    user_name = args[0]
    user_phones = args[1:]
    if len(user_phones) >= 1:
        record = records.find(user_name)
        if record:
            response = []
            for user_phone in user_phones:
                record.remove_phone(user_phone)
                response.append(f"Phone number {user_phone} for contact {user_name} removed.")
            return "\n".join(response)
    else:
        if records.delete(user_name):
            return f"Record for contact {user_name} deleted."
        return f"Record for contact {user_name} not found."


@input_error([])
def greeting_handler(*args):
    greeting = "How can I help you?"
    return greeting

@capitalize_user_name
@input_error("name")
def phone_handler(*args):
    user_name = args[0]
    record = records.find(user_name)
    if record:
        return "; ".join(p.value for p in record.phones)

@input_error("term")
def search_handler(*args):
    term: str = args[0]
    contacts = records.search_contacts(term)
    if contacts:
        return "\n".join(str(contact) for contact in contacts)
    return f"No contacts found for '{term}'."

@input_error("days")
def show_birthdays_handler(*args):
    days = int(args[0])
    contacts = records.contacts_upcoming_birthdays(days)
    if contacts:
        return "\n".join(str(contact) for contact in contacts)
    return f"No contacts have birthdays within following {days} days."

@input_error([])
def show_all_handler(*args):
    return records.iterator()

@input_error("path")
def sort_files_handler(*args):
    try:
        folder_path = Path(args[0])
    except IndexError:
        return "Please provide the path to the folder you want to sort."

    if not folder_path.exists():
        return "The specified folder does not exist."

    result = sort_folders_and_return_result(folder_path)
    return result

COMMANDS = {
            help_handler(): "help",
            greeting_handler: "hello",
            address_handler: "address",
            add_handler: "add",
            change_handler: "change",
            phone_handler: "phone",
            search_handler: "search",
            birthday_handler: "birthday",
            email_handler: "email",
            show_all_handler: "show all",
            show_birthdays_handler: "show birthdays",
            delete_handler: "delete",
            sort_files_handler: "sort files",
            }
EXIT_COMMANDS = {"good bye", "close", "exit", "stop", "g"}

def parser(text: str):
    for func, kw in COMMANDS.items():
        if text.startswith(kw):
            return func, shlex.split(text[len(kw):], posix=False) # .strip().split()
    return unknown_handler, []

def main():
    global records
    with AddressBook("address_book.pkl") as book:
        records = book
        while True:
            user_input = input(">>> ").lower()
            if user_input in EXIT_COMMANDS:
                print("Good bye!")
                break
            
            func, data = parser(user_input)
            
            if func == sort_files_handler:
                result = func(*data)
                print(result)
                continue
            
            result = func(*data)
            
            if isinstance(result, str):
                print(result)
            else:
                for i in result:                
                    print("\n".join(i))
                    input("Press enter to show more records")


if __name__ == "__main__":
    main()
from collections import UserDict
from datetime import datetime
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Імʼя - обовʼязкове поле")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Телефон повинен містити 10 цифр")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Неправиьний формат дати. Використовуй DD.MM.YYYY")
    
    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = birthday

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
            raise ValueError("Номер телефону не знайдено")

    def edit_phone(self, old_phone_number, new_phone_number):
        phone_to_edit = self.find_phone(old_phone_number)
        if phone_to_edit:
            self.remove_phone(old_phone_number)
            self.add_phone(new_phone_number)
        else:
            raise ValueError("Номер телефону не знайдено")

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    
    def __str__(self):
        phones_str = "; ".join(phone.value for phone in self.phones)
        birthday_str = str(self.birthday) if self.birthday else "Немає"
        return f"Імʼя: {self.name.value}, телефон(и): {phones_str}, день народження: {birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Запис не знайдено")

    def get_upcoming_birthdays(self):
        today = datetime.now().date()  # Отримуємо сьогоднішню дату без часу
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                next_birthday = record.birthday.value.date().replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)
                    
                days_until_birthday = (next_birthday - today).days
                if 0 <= days_until_birthday <= 7:
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": next_birthday.strftime("%d.%m.%Y")
                    })
        return upcoming_birthdays
    
    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError) as e:
            return f"[Помилка]: {e}"
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Контакт оновлено."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Контакт додано."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Номер телефону оновлено."
    return "Контакт не знайдено."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return str(record)
    return "Контакт не знайдено."

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "День народження додано."
    return "Контакт не знайдено."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name} має День народження {record.birthday}."
    return "День народження або контакт не знайдено."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        return "\n".join([f"{item['name']}: {item['birthday']}" for item in upcoming])
    return "Немає інформації про дні народження."

def parse_input(user_input):
    return user_input.split(" ")

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    book = load_data()
    print("Вітаю у боті-помічнику!")
    
    while True:
        user_input = input("Введіть команду: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)  
            print("До побачення!")
            break

        elif command == "hello":
            print("Чим можу допомогти?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(book)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Невідома команда.")

if __name__ == "__main__":
    main()
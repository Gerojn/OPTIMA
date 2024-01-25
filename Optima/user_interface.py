from abc import ABC, abstractmethod


class UserInterface(ABC):

    @abstractmethod
    def display_contacts(self, contacts):
        pass

    @abstractmethod
    def display_notes(self, notes):
        pass

    @abstractmethod
    def display_commands(self, commands):
        pass


class ConsoleInterface(UserInterface):

    def display_contacts(self, contacts):
        for contact in contacts:
            print(f"Contact: {contact}")

    def display_notes(self, notes):
        for note in notes:
            print(f"Note: {note}")

    def display_commands(self, commands):
        print("Available Commands:")
        for command in commands:
            print(f"- {command}")
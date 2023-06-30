from commandControl import CommandControl, Command

def print_message(message):
    print(message)

commander = CommandControl()

commander.add_command(Command(500, print_message, "Hello, world!"))
commander.add_command(Command(1000, print_message, "Hello, world!"))

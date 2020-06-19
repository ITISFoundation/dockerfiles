import sys


def assemble_header(message, default_length=80):
    total_message_length = 4 + len(message)
    computed_length = max(default_length, total_message_length)

    spaces_length = default_length - len(message) - 4
    print("-" * computed_length)
    print("| " + message + " " * spaces_length + " |")
    print("-" * computed_length)

def main():
    input_message = " ".join(sys.argv[1:])
    assemble_header(input_message)
    

if __name__ == '__main__':
    main()
import pyLon_db
import pyLon_crypt
import os
import sys
from time import sleep
from base64 import b64decode
from getpass import getpass
from hashlib import sha3_512

script_path = os.path.dirname(sys.argv[0])
home = os.path.expanduser("~")
db_file = f"{home}/pyLon.db"
banner_file = f"{script_path}/banner.b64"
banner = str(b64decode(open(banner_file, "r").read()), "utf8")  # the all important magic


def print_banner():

    """ Clears the screen, makes magical faeries appear. """

    clear_screen()
    print(banner)


def clear_screen():

    """ Function to clear the screen. works in linux and windows"""

    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def quit_program(immediate=False):

    """ Does what it says on the tin. """

    def bye():
        print_banner()
        db.db_close()
        sleep(1)
        quit()
    if immediate:
        bye()
    print_banner()
    if user_prompt_bool("[*] Quitting, are you sure?"):
        bye()


def user_prompt_bool(question: str):

    """ Get a yes / no answer from user """

    accept = list("yn")
    print(question)
    while True:
        get_input = input("(Y)es or (N)o: ").lower()
        if get_input in accept:
            break
    return True if get_input == "y" else False


def user_multiple_choice(choices, term):

    """ Gets a menu option from user """

    while True:
        choice = input(f"\nSelect a{term}: ").lower()
        if choice in choices:
            return choice
        else:
            if choice.lower() == "c":
                main_menu()
            continue


def list_passwords(choose=False, search=None):

    """ Lists passwords and optionally choose a password can also issue a search query.
    may be vulnerable to sqli, but since its a authenticated, im not overly concerned"""

    if search:
        rows = db.select_rows(table="pwMan", column="rowid,*",
                              where_like=("site", search), or_like=("user", search))
    else:
        rows = db.select_rows(table="pwMan", column="rowid,*")

    entries = [f"{x}" for x in range(1, len(rows) + 1)]  # make a list of rows returned

    if entries:  # execute if at least 1 row was returned
        print_banner()
        box_number = lambda x: f"[{x}]"  # put the box around the number this was a PITA
        print(" " * 9 + "SITE" + " " * 24 + "USERNAME")
        for c, i in enumerate(rows):
            print(f" {box_number(entries[c]):<6}  {i[1]:<28}{i[2]:<28}")
        if choose:  # this seemed like the logical place to put this.
            choice = user_multiple_choice(entries, " password [C] to cancel")
            return choice, rows[int(choice) - 1]
        else:
            getpass("\nPress ENTER to continue.")
    else:  # no rows were returned
        print_banner()
        print("[*] No entries found.")
        sleep(2)  # short delay so user can read message.


def decrypt_password(row_data=None):

    """ Call the decryption method from pyLon_crypt """

    if not row_data:
        row_data = list_passwords(choose=True)[1]
    plain_password = crypt.decrypt_password(row_data[3])
    print_banner()
    print(f"""\
    Password for {row_data[1]}

        Username = {row_data[2]}
        Password = {plain_password}\
            """)
    # copy_to_clipboard(plain_password)
    getpass("\nPress ENTER to continue.")


def delete_password():

    """ function to delete a password"""

    rowid = list_passwords(choose=True)[1][0]
    if user_prompt_bool("Are you sure?"):  # try to prevent accidental deletion
        db.delete_rowid("pwMan", rowid)
        sleep(2)


def create_password():

    """ Creates a new entry in the database """

    print_banner()
    site = input("Enter the site name for this password: ")
    user = input("Enter the username for this site: ")
    if user_prompt_bool("Do you wish to generate a random password?"):
        password = crypt.generate_password()
    else:
        users_password = input("Please enter your password: ")
        password = users_password, crypt.encrypt_password(users_password)
    print_banner()
    print(f"[*] Password for {site}\n")
    print(f"        Username = {user}")
    print(f"        Password = {password[0]}\n")
    if user_prompt_bool("Do you wish to commit this to the database?"):
        db.insert_row("pwMan", {"site": site, "user": user, "passwd": password[1]})
        # copy_to_clipboard(password[0])
        sleep(2)
    else:
        print_banner()
        print("[*] Returning to main menu.")
        sleep(1)


def search_password():
    """ searches the database """
    print_banner()
    search_term = input("Please enter search term: ")
    choice = list_passwords(search=search_term, choose=True)
    decrypt_password(choice[1])


def main_menu():

    """ the centre of attention """

    while True:
        print_banner()
        print("""  
        [1] Decrypt a password.
        [2] Create new password.
        [3] Delete a password.
        [4] Search passwords.
        """)
        user_input = user_multiple_choice(list("1234q"), "n option [Q] to Quit")
        try:
            if user_input.lower() == "q":
                quit_program()
            elif user_input == "1":
                decrypt_password()
            elif user_input == "2":
                create_password()
            elif user_input == "3":
                delete_password()
            elif user_input == "4":
                search_password()
        except TypeError:
            continue


def initialize():

    """
     Here we setup some variables etc for the program,
     we put sha3_512 hash of passphrase into file, storing this is probably a weak point!
     if the passphrase is easy enough, it can be easily brute forced, an alternative would be to
     ask the user to manually verify decryption by decrypting a string known only to the user.
     This however is more convenient, for the purposes of this assessment,
     I'm sure it's sufficient, it all depends on the user choosing a strong passphrase.
    """

    print_banner()  # read the docstring
    pw_hash = db.select_rows(table="pwCheck", column="pwHash")  # get the users hash from the db
    if pw_hash:  # ok so columns were returned, that's handy
        print("[*] Encryption key exists in database.")
        encryption_key = getpass("\nEnter your encryption key: ", stream=None).encode()
        if sha3_512(encryption_key).hexdigest() == pw_hash[0][0]:
            print_banner()
            crypt.set_passphrase(encryption_key)
            print("[*] Encryption key correct.")
            print("[*] Initialization complete.")
            sleep(1)
            main_menu()
        else:
            print_banner()
            print("[!] Invalid encryption key.")
            sleep(1)
            if user_prompt_bool("Try again?"):
                initialize()  # try initialize again
            else:
                return
    else:
        if user_prompt_bool("[!] Encryption key doesnt exist, want to create one?"):
            while True:
                print_banner()
                encryption_key = getpass("Create your encryption key: ", stream=None).encode()
                confirm = getpass("Confirm your encryption key: ", stream=None).encode()
                if encryption_key != confirm:
                    print("[!] Keys didn't match.")
                    if user_prompt_bool("Try again?"):
                        continue
                    else:
                        quit_program(immediate=True)
                break
            print_banner()
            key_type = "VARCHAR NOT NULL"
            db.create_table("pwCheck", {"pwhash": key_type})
            db.create_table("pwMan", {"site": key_type, "user": key_type, "passwd": key_type})
            db.insert_row("pwCheck", {"pwHash": sha3_512(encryption_key).hexdigest()})
            crypt.set_passphrase(encryption_key)
            print("[*] Initialization complete.")
            sleep(3)
            main_menu()


# create instances of the classes used in this program.
db = pyLon_db.Database(db_file)  # if it doesnt exist it will be created
crypt = pyLon_crypt.ChaCha20Crypt()


if __name__ == '__main__':  # entry into main program
    try:
        initialize()
    except KeyboardInterrupt:  # close gracefully without error message when ctl-c used.
        quit_program(immediate=True)

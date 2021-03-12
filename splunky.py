import os
import user
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# this disables the warnings in requests
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

res = requests.get(f'https://{user.HOST}', verify=False)
status = res.status_code


# function to clear_screen
def clear_screen():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')


# check if server is online
if status == 200:
    print('Server is online!')
else:
    print('An error has occurred. Might be the server is offline.')

print("\nWhich would you like to do?\n"
      "1 - add user\n"
      "2 - delete user\n"
      "3 - modify roles for user\n"
      "4 - reset user password\n"
      "5 - quit\n")

# menu screen
while True:
    menu = input("Enter the number > ")

    if menu == '5':
        break

    if menu == "1":
        clear_screen()
        add_user_from_csv = input("Do you want to add a user from a csv? (\'yes\' or \'no\') ").lower()

        if add_user_from_csv == 'yes':
            print("Which user you want to add? (Enter the ID): \nID - Name")
            print(user.print_users())

            input_user_id = input('> ')

            name = user.find_user(input_user_id)
            user.add_user(name)
        elif add_user_from_csv == 'no':
            input_name = input("What's the user's full name? ")
            user.add_user(input_name)
        else:
            print("Please answer \'yes\' or \'no\'")
    elif menu == "2":
        clear_screen()
        user.delete_user()
    elif menu == '3':
        clear_screen()
        user.modify_user()
    elif menu == '4':
        clear_screen()
        user.reset_password()
    else:
        print('Please enter the right number')

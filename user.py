from csv import DictReader, writer, reader
import splunklib
import splunklib.client as client
# module to access the password and username generator function
from generator import usernameGenerator, passwordGenerator
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from time import sleep  # use to add delays to code
import os
import keyring

HOST = "18.237.149.90"
PORT = 8089
USERNAME = os.environ.get('SPLUNK_USERNAME')
PASSWORD = keyring.get_password('splunk', 'splunk_admin')

# Create a Service instance and log in
service = client.connect(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD)

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# Oauth credentials
creds = ServiceAccountCredentials.from_json_keyfile_name(".creds.json", scope)
client = gspread.authorize(creds)

# Open a sheet from a spreadsheet in one go
spreadsheet = client.open("UserCredentials").sheet1

all_users = list()


# prompt the user to input some list of numbers
def prompt_roles():
    print("What role(s) you want this user to be?\n"
          "(use commas(\",\") to separate values)\n"
          "1 - admin\n"
          "2 - power\n"
          "3 - user\n"
          "4 - can_delete\n"
          "5 - splunk-system-role")

    valid_nums = ['1', '2', '3', '4', '5']

    input_roles = [f"{number}" for number in input("Enter the numbers > ").split(",")]
    result = [ele for ele in input_roles if (ele in valid_nums)]

    return list(set(result))  # this removes duplicates


# function to add roles
def add_roles():
    results = prompt_roles()

    isValid = True

    while isValid:
        if results:
            isValid = False
        else:
            print('\nPlease enter valid numbers 1 - 5\n')
            results = prompt_roles()

    for index, num in enumerate(results):
        if num == '1':
            results[index] = 'admin'
        elif num == '2':
            results[index] = 'power'
        elif num == '3':
            results[index] = 'user'
        elif num == '4':
            results[index] = 'can_delete'
        elif num == '5':
            results[index] = 'splunk-system-role'

    return results


# function to print users from a csv
def print_users():
    sleep(3)
    names = ""
    with open("data_characters.csv") as file:
        csv_reader = DictReader(file, delimiter=";")
        for row in csv_reader:
            # Each row is an OrderedDict!
            names += row['Id'] + " - " + row['Name'] + "\n"  # Use keys to access data
    return names


# function to find user from a csv
def find_user(input_user_id):
    with open("data_characters.csv") as file:
        csv_reader = DictReader(file, delimiter=";")
        for (index, row) in enumerate(csv_reader):
            if row['Id'] == input_user_id:
                return row['Name']
    print(f"{input_user_id} not found.")


# function to add user
def add_user(name):
    # check if user already exists
    for user in service.users:
        if user.realname == name:
            print(f"{name} already exists. Username: {user.name}")
            return
    # generate username
    username = usernameGenerator(name)
    # check if username already exists
    for user in service.users:
        if user.name == username:
            username = usernameGenerator(name)
    # generate password
    password = passwordGenerator()

    input_roles = add_roles()

    # create a new user in Splunk Enterprise
    new_user = service.users.create(realname=name,
                                    username=username,
                                    password=password,
                                    roles=input_roles)
    new_user.refresh()
    print('... user created in splunk')

    # add credentials to text file
    content = open('user_credentials.txt', 'a')
    content.write(f"{username}\t\t{password}")
    content.write("\n")
    print('... user created in text')

    # add credentials to csv file
    with open("user_credentials.csv", "a") as csv_file:
        csv_writer = writer(csv_file)
        csv_writer.writerow([username, password])
    print('... user created in csv')

    # add credentials to google sheets
    # everytime a new user is created it adds into google sheets too
    spreadsheet.append_row([username, password])

    print("\nUser created!\n"
          f"Name: {name}\n"
          f"Role(s): {input_roles}")


# function to delete user
def delete_user():
    print("\nWhich username you want to delete?")
    sleep(1)
    all_users = [user.name for user in service.users]
    for user in all_users:
        print(user)

    # delete user in splunk
    # add try/except block if user is not in splunk
    while True:
        try:
            name = input("Enter the username > ")
            service.users.delete(name)
        except splunklib.binding.HTTPError:
            print('please enter a valid username')
        else:
            print('...user deleted in splunk')
            break

    lines = list()
    # delete user in csv
    with open('user_credentials.csv', 'r') as readFile:
        csv_reader = reader(readFile)
        for row in csv_reader:
            lines.append(row)
            print(lines, row)
            for field in row:
                if field == name:
                    lines.remove(row)
                    print("...user deleted in csv")
    with open('user_credentials.csv', 'w') as writeFile:
        csv_writer = writer(writeFile)
        csv_writer.writerows(lines)
    # delete user in txt
    with open('user_credentials.txt', 'r') as file:
        lines = file.readlines()
    with open('user_credentials.txt', 'w') as file:
        for line in lines:
            if line.split('\t')[0] != name:
                file.write(line)
            else:
                print('...user deleted in txt')

    # delete user in Google Sheets
    spreadsheet_records = spreadsheet.get_all_records()
    for (index, record) in enumerate(spreadsheet_records):
        if record['Username'] == name:
            spreadsheet.delete_rows(index + 2)
            print('...user deleted in google sheets')

    print("Username deleted")


# function to modify user roles
def modify_user():
    print("\nWhich user you want to modify?\n"
          "ID - User")
    # sleep(1)

    all_users = [{"id": index,
                  "user": user,
                  "name": user.name,
                  "role": [role.name for role in user.role_entities]}
                 for index, user in enumerate(service.users)]

    for user in all_users:
        print(f"{user['id']} - {user['name']}: {user['role']}")

    while True:
        try:
            input_id = int(input('Enter ID > '))
        except ValueError:
            print('please enter an ID number')
        else:
            if int(input_id) > len(all_users)-1 or int(input_id) < 0:
                print(f'please enter numbers 0 - {len(all_users)-1}')
            else:
                break

    input_roles = add_roles()

    # modify user role property in Splunk
    kwargs = {"roles": input_roles}

    # do binary search instead linear
    find_user = binarySearch(all_users, input_id)
    # update roles in splunk
    find_user['user'].update(**kwargs).refresh()

    print(f"\n{find_user['user'].realname}\'s role updated to: {kwargs['roles']}")


def binarySearch(list_of_users, id):
    first = 0
    last = len(list_of_users) - 1
    index = -1

    while (first <= last) and (index == -1):
        mid = (first + last) // 2

        if list_of_users[mid]['id'] == id:
            index = mid
        else:
            if id < list_of_users[mid]['id']:
                last = mid - 1
            else:
                first = mid + 1

    return list_of_users[index]


def reset_password():
    print("\nWhich username you want to reset password?")
    sleep(1)

    all_users = [{'user': user, 'name': user.name} for user in service.users]

    for user in all_users:
        print(user['name'])

    while True:
            input_user = input("Enter the username > ")

            if any(d['name'] == input_user for d in all_users):
                kwargs = {"password": passwordGenerator()}
                for user in all_users:
                    if user['name'] == input_user:
                        user['user'].update(**kwargs).refresh()
                print('...user reset password in splunk')
                break
            else:
                print('username invalid')

    lines = list()
    # delete user in csv
    with open('user_credentials.csv', 'r') as readFile:
        csv_reader = reader(readFile)
        for row in csv_reader:
            lines.append(row)
            for field in row:
                if field == input_user:
                    lines.remove(row)
                    print("...user reset password in csv")
    with open('user_credentials.csv', 'w') as writeFile:
        csv_writer = writer(writeFile)
        csv_writer.writerows(lines)
        csv_writer.writerow([input_user, kwargs['password']])
    # delete user in txt
    with open('user_credentials.txt', 'r') as file:
        lines = file.readlines()
    with open('user_credentials.txt', 'w') as file:
        for line in lines:
            if line.split('\t')[0] != input_user:
                file.write(line)

        file.write(f"{input_user}\t\t{kwargs['password']}")
        print('...user reset password in txt')

    # delete user in Google Sheets
    spreadsheet_records = spreadsheet.get_all_records()
    for (index, record) in enumerate(spreadsheet_records):
        if record['Username'] == input_user:
            spreadsheet.delete_rows(index + 2)
            print('...user deleted in google sheets')
    spreadsheet.append_row([input_user, kwargs['password']])

    print(f"\nReset password for username: {input_user} DONE!")

import random
import string


# function to generate password
def passwordGenerator():
    # concatenate three imported strings
    password_characters = string.ascii_letters + string.digits + string.punctuation
    # blank list to store the random characters
    passwordList = []

    # loop 12 times to create 12 random characters
    for x in range(12):
        # add characters to the list
        passwordList.append(random.choice(password_characters))

    # merge the list into a single string
    password = ''.join(passwordList)

    return password


# function to generate username
def usernameGenerator(name):
    name = name.split(' ')
    # get user's first and last names
    first = name[0].lower()
    last = name[-1].lower()
    number = '{:02d}'.format(random.randrange(1, 99))
    # concatenate first initial with 7 chars of the last name.
    username = first[0] + last[:7] + number
    # output username
    return username
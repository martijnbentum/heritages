from django.contrib.auth.models import User, Group
from django.utils.crypto import get_random_string

def create_user_account(username, password, first_name, 
    last_name, email=None):
    '''Creates a new Django user account with the given username and password.
    username (str): The username for the new user.
    password (str): The password for the new user.
    email (str, optional): The email for the new user.
    first_name (str, optional): The first name for the new user.
    last_name (str, optional): The last name for the new user.

    Returns: User: The created user object.
    '''
    if User.objects.filter(username=username).exists():
        raise ValueError(f"Username '{username}' is already taken.")
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name
    )
    return user

def delete_user_by_username(username):
    '''Deletes a user with the given username if they exist.
    username (str): The username of the user to delete.
    
    Returns: bool: True if the user was successfully deleted, 
        False if the user doesn't exist.
    '''
    try: user = User.objects.get(username=username)
    except User.DoesNotExist:return False
    user.delete()  
    return True

def make_password(length = 9):
    '''
    Generate a random password with the given length.
        length (int): The length of the password to generate.
    Returns: str: The generated password.
    '''
    password = get_random_string(length)
    return password

def make_accounts(n = 10, base_name = 'user', add_view_group = True,
	start_number = 1):
    '''Create multiple user accounts with random usernames and passwords.
    '''
    users = []
    name_passwords = []
    for i in range(start_number,n+start_number):
        username = f"{base_name}-{i}"
        password = make_password()
        first_name = f"First-{i}"
        last_name = f"Last-{i}"
        user = create_user_account(username, password, first_name, last_name)
        if add_view_group:add_view_group_to_user(user)
        users.append(user)
        name_passwords.append(username + '\t' + password)
        print(username,'\t',password)
    return users, name_passwords

def delete_accounts(n = 10, base_name = 'user'):
    '''Delete multiple user accounts with random usernames and passwords.
    '''
    for i in range(1,n+1):
        username = f"{base_name}-{i}"
        print(username,delete_user_by_username(username))

def get_view_group():
    '''view group give basic view access to the users
    '''
    return Group.objects.get(name='view')

def add_view_group_to_user(user):
    '''adds to view group to a user to give basic view access
    '''
    view_group = get_view_group()
    user.groups.add(view_group)

def add_view_group_to_users(users):
    for user in users:
        add_view_group_to_user(user)



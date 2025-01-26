import json
import requests
import subprocess
import os
import sys
import getpass


VPN_FILE_PATH = 'config.ovpn'
CONFIG_FILE_PATH = 'config.json'
SAVE_USERNAME = False
SAVE_PASSWORD = False
VERBOSE = True


def handle_args():
    if("--save-username" in sys.argv):
        global SAVE_USERNAME
        SAVE_USERNAME = True

    if("--save-password" in sys.argv):
        global SAVE_PASSWORD
        SAVE_PASSWORD = True

    if("--save-credentials" in sys.argv):
        SAVE_USERNAME = True
        SAVE_PASSWORD = True

    if("--delete-credentials" in sys.argv):
        if(os.path.exists(CONFIG_FILE_PATH)):
            with open(CONFIG_FILE_PATH, 'r') as f:
                config = json.load(f)
                if 'username' in config:
                    del config['username']
                if 'password' in config:
                    del config['password']
                save_config(config)
                print("Credentials deleted.")

    if("--delete-domain" in sys.argv):
        if(os.path.exists(CONFIG_FILE_PATH)):
            with open(CONFIG_FILE_PATH, 'r') as f:
                config = json.load(f)
                if 'domain' in config:
                    del config['domain']
                    save_config(config)
                    print("Domain deleted.")
                else:
                    print("No domain saved.")

    if("--no-verbose" in sys.argv):
        global VERBOSE
        VERBOSE = False

    if("--help" in sys.argv):
        print("Usage: python3 main.py [--save-username] [--save-password] [--save-credentials] [--no-save-credentials] [--no-verbose]")
        print("--save-username: Save the username in the config file.")
        print("--save-password: Save the password in the config file.")
        print("--save-credentials: Save both the username and the password in the config file.")
        print("--delete-credentials: Delete the saved credentials.")
        print("--delete-domain: Reset the saved domain.")
        print("--no-verbose: Disable verbose mode.")


def log(message):
    if(VERBOSE):
        print(message)


def save_config(config):
    with open(CONFIG_FILE_PATH, 'w') as f:
        json.dump(config, f)


def save_vpn_config(vpn_config, path):
    log('Saving new VPN configuration...')
    with open(path, 'w') as f:
        f.write(vpn_config)


def get_credentials():
    config = {}
    if(os.path.exists(CONFIG_FILE_PATH)):
        with open(CONFIG_FILE_PATH, 'r') as f:
            config = json.load(f)

    if 'domain' in config:
        domain = config['domain']
        log('Using saved domain.')
    else:
        domain = None
        while domain is None:
            domain = input('Please enter the domain of your VPN (https://eduvpn.example.org): ')
        config['domain'] = domain
        save_config(config)
        log('Domain saved in the configuration file.')

    if 'username' in config:
        username = config['username']
        log('Using saved username.')
    else:
        username = None
        while username is None:
            username = input('Please enter your username: ')
        if SAVE_USERNAME:
            config['username'] = username
            save_config(config)
        else:
            print("You can save your username with the --save-username or --save-credentials option.")
    
    if 'password' in config:
        password = config['password']
        log('Using saved password.')
    else:
        password = None
        while password is None:
            password = getpass.getpass('Please enter your password: ')
        if SAVE_PASSWORD:
            config['password'] = password
            save_config(config)
        else:
            print("You can save your password with the --save-password or save-credentials option.")

    return username, password, domain


def get_vpn_config():
    username, password, domain = get_credentials()
    displayName = "VPN Configuration"

    session = requests.Session()

    login_url = f'{domain}/vpn-user-portal/_user_pass_auth/verify'
    protected_url = f'{domain}/vpn-user-portal/home'

    login_data = {
        'userName': username,
        'userPass': password,
        'authRedirectTo': f"{domain}/vpn-user-portal/home"
    }

    headers = {
        'Referer': f'{domain}/vpn-user-portal/home'
    }

    response = session.post(login_url, data=login_data, headers=headers)

    if response.ok:
        log('Successfully logged in.')

        downloadBody = {
            "action": "add_config",
            "profileId": "default_openvpn+tcp",
            "displayName": displayName
        }


        response = session.post(protected_url, data=downloadBody, headers=headers)
        if response.ok:
            log('Successfully downloaded OpenVPN config.')
            return response.text
        else:
            raise Exception("Error while downloading OpenVPN config.")

    else:
        raise Exception('Failed to login.')


def connect_to_vpn(vpn_config_path):
    log('Launched VPN instance...')

    with open(os.devnull, 'w') as devnull:
        result = subprocess.run(['sudo', 'openvpn', '--config', vpn_config_path], stdout=devnull, stderr=devnull)

    if result.returncode != 0:
        raise Exception('Failed to connect to VPN.')


def get_config_and_connect():
    log("Getting a new VPN configuration...")
    try:
        vpn_config = get_vpn_config()
        save_vpn_config(vpn_config, VPN_FILE_PATH)

        log("Successfully downloaded new VPN configuration.")

        try:    
            connect_to_vpn(VPN_FILE_PATH)
        except Exception as e:
            log(e)
            log("Failed to connect to VPN. Verify your openvpn installation.")
    except Exception as e:
        log(e)
        log("Unable to get a new VPN configuration, check your credentials. It may also be caused by too much VPN configurations on your account (you can fix it by deleting some of them on your vpn portal).")




def main():

    handle_args()

    if(os.path.exists(VPN_FILE_PATH)):
        try:
            connect_to_vpn(VPN_FILE_PATH)
        except Exception as e:
            log(e)
            get_config_and_connect()
    else:
        get_config_and_connect()


    log("\nExiting...")



#MAIN CALL
if __name__ == '__main__':
    main()
# AutoEduVPN

This program allows you to connect to your EduVPN Virtual Private Network (VPN) from your Linux command line.

It automatically retrieves (or updates when expired) your OpenVPN configuration from your organization's server and connects you to it.

## Disclaimer

This module was made for educational purposes and uses Web Scraping.

When using this module, you are solely responsible for ensuring that your usage complies with all applicable laws and regulations, and that your usage is authorized by your organization.

The author and contributors to this repository disclaim any responsibility for any damages or legal repercussions arising from the use of this program.

By using this module, you acknowledge and agree to the terms of this disclaimer.

## Installation

OpenVPN needs to be installed in order to use this program.

```bash
git clone https://github.com/killianmarty/AutoEduVPN
cd AutoEduVPN
pip install -r requirements.txt
```

## Usage

This program requires sudo privileges to use OpenVPN.

```bash
sudo python3 main.py [--save-username] [--save-password] [--save-credentials] [--delete-credentials] [--delete-domain] [--no-verbose]
```

**--save-username**: Save the username in the config file.

**--save-password**: Save the password in the config file.

**--save-credentials**: Save both the username and the password in the config file.

**--delete-credentials**: Delete the saved credentials.

**--delete-domain**: Reset the saved domain.

**--no-verbose**: Disable verbose mode.


## Author

This program was originally created by Killian Marty.
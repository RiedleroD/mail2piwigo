## Usage

Just edit the config file, install the necessary python3 modules with `pip3 install piwigo` and run the script - you don't have to do anything else.

## Configuration

### Mail config

Edit the config file values for your email inbox - you can look them up in your preferred email client.
Only imap is currently supported, and there are no plans to implement pop3 support.
`serv` is the base address to the server
`port` is the imap port
`usr` is the username or email address you login with in the email server
`pass` is the password for your email account

### Piwigo config

Edit the config file values for your piwigo server

`serv` is the base address to the server
`usr` is the username or email address you login with in the email server
`pass` is the password for your email account
`categoryid` is the id of the category the script should upload the photos to - you can look them up in the piwigo server.

### Miscellanious config

`wait` is the amount of minutes the script should wait between checking - only whole numbers from 0 upwards are valid.

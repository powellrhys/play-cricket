# play-cricket

The following repository retrieves cricket data from the play cricket website.

## Prerequisites

To access individual player stats a play cricket account is required. It is therefore a requirement that both an email and password be passed into main.py through the use of environment variables (`email` and `password`).

A third environment variables (`club`) is required which specifies which cricket club's data you would like to scrape. 

## Execution 

To trigger the script, execute the main.py file found in the root directory. Upon completion, you'll find various csv's stored in your root directory.

Additional functionality has been written which supports the transfer of this data to a person via email. For this to work a functioning google mail email address is required. Once aquired, the following environmental variables are required:

- `email_sender`
- `email_password`
- `email_reciever`

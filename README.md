# Whatsapp Bookings Chatbot

A chatbot demo I made for Nigel. It's a simple chatbot that allows you to book a date and time at a restaurant or hotel 
(or anywhere really).

It uses Twilio's API to send and receive messages and Flask to host the bot.
The bot also uses a Firebase database to store the booking data.

## How to use
Add your Firebase credentials in the `__init__` method of the firebaseDB class.

Run the app.py file and add your server's IP address as the forwarding address in the
Twilio Whatsapp Sandbox Settings of your account.

Make sure to add the '/sms' route to the end of your url/IP address.

## Installation
Clone the repository and install the requirements using pip.

    pip install -r requirements.txt

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

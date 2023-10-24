from ClientInfo import ClientInfo
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime


def send_confirmation_email(date: str | datetime, time: str | datetime, client: ClientInfo):
    """
    Email the client with the booking details. Using sendgrid.

    :param date: The date of the booking
    :param time: The time of the booking
    :param client: The client's details
    :return: True if the email was sent successfully, False otherwise
    """

    if isinstance(date, datetime):
        date = date.strftime("%A %d %B %Y")
    if isinstance(time, datetime):
        time = time.strftime("%H:%M")

    SENDGRID_API_KEY = 'YOUR_SENDGRID_API_KEY_HERE'
    message = Mail(from_email="your_email@address.com", to_emails=client.email, subject="Your booking has been confirmed!",
                   html_content=f'''
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Booking Confirmation</title>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                background-color: #f2f2f2;
                            }}
                            .container {{
                                margin: 0 auto;
                                max-width: 600px;
                                padding: 20px;
                                background-color: #fff;
                                border-radius: 10px;
                                box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
                            }}
                            h1 {{
                                color: #0072c6;
                                font-size: 36px;
                                margin-bottom: 20px;
                            }}
                            img {{
                                max-width: 100%;
                                height: auto;
                                margin-bottom: 20px;
                            }}
                            .centre {{
                                max-width: 100%;
                                height: auto;
                                margin-bottom: 20px;
                                display: block;
                                margin: 0 auto;
                            }}
                            p {{
                                font-size: 18px;
                                line-height: 1.5;
                                margin-bottom: 20px;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <img src="https://f.hubspotusercontent20.net/hubfs/3390327/WordPress-Table-Reservation-plugin-1000x562-1.jpg" 
                                 class="centre" alt="reserved table">
                            <h1>Hi {client.name}!</h1>
                            <p>Your booking has been confirmed for {date} at {time}.</p>
                            <p>You can cancel your booking anytime through the chatbot.</p>
                            <p>Can't wait to see you!</p>
                        </div>
                    </body>
                    </html>
    ''')

    try:
        mailMan = SendGridAPIClient(SENDGRID_API_KEY)
        mailMan.send(message)
        return True
    except Exception as e:
        print(e)
        return False


# cancellation email
def send_cancellation_email(date: str | datetime, time: str | datetime, client: ClientInfo):
    """
    Email the client with the booking details. Using sendgrid.

    :param date: The date of the booking
    :param time: The time of the booking
    :param client: The client's details
    :return: True if the email was sent successfully, False otherwise
    """

    if isinstance(date, datetime):
        date = date.strftime("%A %d %B %Y")
    if isinstance(time, datetime):
        time = time.strftime("%H:%M")

    SENDGRID_API_KEY = 'YOUR_SENDGRID_API_KEY_HERE'
    message = Mail(from_email="your_email@address.com", to_emails=client.email, subject="Your booking has been cancelled",
                   html_content=f'''
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Reservation has been cancelled</title>
                    </head>
                    <body>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                background-color: #f2f2f2;
                            }}
                            .container {{
                                margin: 0 auto;
                                max-width: 600px;
                                padding: 20px;
                                background-color: #fff;
                                border-radius: 10px;
                                box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
                            }}
                            img {{
                                max-width: 100%;
                                height: auto;
                                margin-bottom: 20px;
                            }}
                            p {{
                                font-size: 18px;
                                line-height: 1.5;
                                margin-bottom: 20px;
                            }}
                        </style>
                    
                        <div class="container">
                            <p>Hi {client.name},</p>
                            <p>Please note that your booking for {date} at {time} has been cancelled.</p>
                            <p>You can make a new booking whenever you like through the chatbot</p>
                            <p>Thank you for using our service.</p>
                        </div>
                    
                    </body>
                    </html>
    ''')

    try:
        mailMan = SendGridAPIClient(SENDGRID_API_KEY)
        mailMan.send(message)
        return True
    except Exception as e:
        print(e)
        return False

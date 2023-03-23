from Emails import send_confirmation_email, send_cancellation_email
from datetime import datetime
from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from firebaseDB import FirebaseDatabase
from ClientInfo import ClientInfo

# http://kuda.pythonanywhere.com/sms
app = Flask(__name__)
# you can generate a key with this command on the terminal: python -c 'import os; print(os.urandom(16))'
app.secret_key = b'\x8e\x95\x8fw5\xb5\xd5\xd9\x18+\xff\xc77\xf4\x15\x80'
fireDB = FirebaseDatabase()


# c++ style enum for the stages values
class STAGES:
    WELCOME_AVAILABLE_DATES = 0
    AVAILABLE_TIMES = 1
    GET_NAME = 2
    GET_EMAIL = 3
    GET_NUMBER = 4
    CONFIRM_CHECK = 5
    CANCELLATION = 6


class PATH:
    NEW_BOOKING = 0
    EXISTING_BOOKING = 1


def new_session_vars():
    # initialize session variables if not set
    if 'stage' not in session:
        session['stage'] = STAGES.WELCOME_AVAILABLE_DATES
    if 'dialogue_path' not in session:
        session['dialogue_path'] = PATH.NEW_BOOKING
    if 'booked_date' not in session:
        session['booked_date'] = ""
    if 'booked_time' not in session:
        session['booked_time'] = ""
    if 'reservation_name' not in session:
        session['reservation_name'] = ""
    if 'reservation_email' not in session:
        session['reservation_email'] = ""
    if 'reservation_phone_number' not in session:
        session['reservation_phone_number'] = ""


@app.route("/sms", methods=['POST'])
def sms_reply():
    new_session_vars()

    today = datetime.today()

    # Fetch the message
    msg = request.form.get('Body')
    app.logger.info(msg)

    # response object
    resp = MessagingResponse()
    app.logger.info(session['stage'])

    # determine the phase of the day
    phase = "morning"
    if 12 <= today.hour < 18:
        phase = "afternoon"
    elif today.hour > 18:
        phase = "evening"
    # set the default message
    default_msg = f"Good {phase}. Would you like to: "\
                  f"\n1. Make a Booking, or \n2. Manage existing booking?"

    # start of the dialogue
    if (not msg.isnumeric() and session['stage'] == STAGES.WELCOME_AVAILABLE_DATES) or msg.lower().find("hi") != -1:
        session.clear()
        new_session_vars()
        resp.message(default_msg)
        return str(resp)

    if msg.isnumeric() and session['stage'] == STAGES.WELCOME_AVAILABLE_DATES and session['dialogue_path'] == PATH.NEW_BOOKING:
        selected_path = int(msg) - 1
        if selected_path not in [PATH.NEW_BOOKING, PATH.EXISTING_BOOKING]:
            resp.message("Invalid choice. Please select option 1 or 2.")
            return str(resp)

        session['dialogue_path'] = PATH.NEW_BOOKING if selected_path == 0 else PATH.EXISTING_BOOKING
        print(session['dialogue_path'])

        # skip to stage 4 if user wants to manage booking
        if session['dialogue_path'] == PATH.EXISTING_BOOKING:
            session['stage'] = STAGES.CONFIRM_CHECK
            resp.message("Please enter your email address:")
            return str(resp)

        elif session['dialogue_path'] == PATH.NEW_BOOKING:
            session['stage'] = STAGES.AVAILABLE_TIMES
            available_dates = ""

            for index, dte in enumerate(fireDB.get_available_dates()):
                dte = datetime.strptime(dte, "%m-%d-%Y")
                available_dates += f"\n{index + 1}. {dte.strftime('%A %d %B %Y')}"

            resp.message(f"Here are the available booking dates:\n"
                         f"{available_dates}")
            return str(resp)

    if msg.isnumeric() and session['stage'] == STAGES.AVAILABLE_TIMES:
        session['stage'] = STAGES.GET_NAME
        select_date = int(msg) - 1
        available_dates = fireDB.get_available_dates()
        session['booked_date'] = available_dates[select_date]

        if select_date in range(len(available_dates)):
            selected_date = available_dates[select_date]
            available_times = ""

            for index, tme in enumerate(fireDB.get_available_times(selected_date)):
                available_times += f"\n{index + 1}. {tme}"

            selected_date = datetime.strptime(selected_date, "%m-%d-%Y")
            selected_date = selected_date.strftime('%A %d %B %Y')

            resp.message(f"Here are the available times for {selected_date}:{available_times}")
        else:
            resp.message("Invalid option. Please select an available date.")
        return str(resp)

    elif msg.isnumeric() and session['stage'] == STAGES.GET_NAME:
        select_time = int(msg) - 1
        selected_date = session['booked_date']
        available_times = fireDB.get_available_times(selected_date)

        if select_time in range(len(available_times)):
            session['booked_time'] = available_times[select_time]
            session['stage'] = STAGES.GET_EMAIL
            resp.message("Please enter your name:")
        else:
            resp.message("Invalid option. Please select an available time.")
        return str(resp)

    elif session['stage'] == STAGES.GET_EMAIL:
        session['stage'] = STAGES.GET_NUMBER

        if not session['dialogue_path'] == PATH.EXISTING_BOOKING:
            session['reservation_name'] = msg

        resp.message("Please enter your email address:")
        return str(resp)

    elif session['stage'] == STAGES.GET_NUMBER:
        session['stage'] = STAGES.CONFIRM_CHECK
        session['reservation_email'] = msg

        resp.message("Please enter your contact number:")
        return str(resp)

    # elif session['stage'] == 5:
    #     session['stage'] = 6
    #     resp.message("Creating your booking...")

    elif session['stage'] == STAGES.CONFIRM_CHECK:
        if session['dialogue_path'] == PATH.NEW_BOOKING:
            session['reservation_phone_number'] = msg

            # create client
            client = ClientInfo(session['reservation_name'], session['reservation_email'],
                                session['reservation_phone_number'])

            result, message = fireDB.book_time(session['booked_date'], session['booked_time'], client)

            if not result:
                resp.message(message)
                return str(resp)

            message_date = datetime.strptime(session['booked_date'], "%m-%d-%Y")
            message_date = message_date.strftime('%A %d %B %Y')
            resp.message(f"{session['reservation_name']}, your booking has been confirmed for "
                         f"{message_date} at {session['booked_time']}.\nThank you!")

            # send confirmation email
            if send_confirmation_email(message_date, session['booked_time'], client):
                app.logger.info("Email sent successfully")
            else:
                app.logger.info("Email failed to send")
            # clear session variables
            session.clear()

        elif session['dialogue_path'] == PATH.EXISTING_BOOKING:
            # check if booking exists using only the client's email
            session['reservation_email'] = msg
            found, date, time, client = fireDB.find_booking_from_email(session['reservation_email'])
            if found:
                session['stage'] = STAGES.CANCELLATION
                msg = f"Booking reserved for {client.name} on " \
                      f"{date.strftime('%A %d %B')} at {time}\n" \
                      f"Would you like to remove this reservation?\n" \
                      f"1. Yes,\n" \
                      f"2. No."
            else:
                msg = f"No booking found for {client.name}"

            msg += ""
            resp.message(msg)

        return str(resp)

    elif session['stage'] == STAGES.CANCELLATION:
        option = int(msg)
        if option == 1:
            # use the client's email to get the booking details
            _, date, time, client = fireDB.find_booking_from_email(session['reservation_email'])

            # delete the booking
            delete_result = fireDB.delete_booking(client)
            if delete_result:
                resp.message("Successfully removed your reservation")
                # send confirmation email
                if send_cancellation_email(date, time, client):
                    app.logger.info("Email sent successfully")
                else:
                    app.logger.info("Email failed to send")
                # clear session variables
                session.clear()
            else:
                resp.message("Failed to remove the reservation. Try again?\n"
                             "1. Yes,\n"
                             "2. No.")
        else:
            # print(session.values())
            session.clear()
        return str(resp)

    else:
        resp.message(default_msg)
        session.clear()
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)

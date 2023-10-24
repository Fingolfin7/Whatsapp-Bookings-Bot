import firebase_admin
from firebase_admin import db
from ClientInfo import ClientInfo
from datetime import datetime, timedelta

class FirebaseDatabase:
    def __init__(self, certificate_path="YOUR_JSON_PATH_HERE.json"):
        self.creds = firebase_admin.credentials.Certificate(certificate_path)
        self.default_app = firebase_admin.initialize_app(self.creds, {
            'databaseURL': "YOUR_FIREBASE_DB_LINK_HERE"})
        self.ref = db.reference("/")
        self.create_dates_for_week()

    def empty_database(self):
        """
        Don't think this needs much explanation.
        """
        self.ref.set({})

    def get_available_dates(self):
        """
        Get the available dates from the database. The dates are formatted as '03-12-2021'.
        New dates are created for every week. The dates range from the current week day to Friday.
        :return: A list of available dates retrieved from the database
        """
        self.create_dates_for_week()
        try:
            query = self.ref.order_by_child('available').equal_to(True)
            return list(query.get())
        except Exception as e:
            print(f'An error occurred: {e}')

    def get_available_times(self, available_date: str):
        """
        Get the available times for a given date.
        :param available_date: The date formatted as '03-12-2021'
        :return: A list of available times retrieved from the database
        """
        query = self.ref.order_by_child('available').equal_to(True)
        vals = query.get()[available_date].items()
        slots = [time for time, status in vals if status == 'unbooked']

        return slots

    def book_time(self, date: str, time: str, client: ClientInfo):
        """
        Book a time slot for a client.
        :param date: The date of the booking formatted as '03-12-2021'
        :param time: The time of the booking formatted as '12:00'
        :param client: The client's details
        :return: A tuple of (success, message)
        """
        try:
            date_ref = self.ref.child(date)
            time_ref = date_ref.child(time)

            # found, rst_date, _ = self.find_booking(client)
            found, rst_date, _, _ = self.find_booking_from_email(client.email)
            if found and rst_date == date:  # if client already has a booking on this date
                rst_date = rst_date.strftime('%A %d %B')
                message = f'Sorry, {client.name}, you already have a reservation on {rst_date}.'
                return False, message

            def update_status(current_status):
                if current_status == 'unbooked':
                    return 'booked'
                else:
                    return current_status

            new_status = time_ref.transaction(update_status)

            if new_status == 'booked':
                message = f'{client.name}, your booking has been confirmed for {date} at {time}.'
                print(message)
                time_ref.update({'info': vars(client)})

                date_ref.update({'available': False})

                for time in date_ref.get():
                    if date_ref.child(time).get() == 'unbooked':
                        date_ref.update({'available': True})
                        break

                return True, message
            else:
                message = f'Sorry, {time} on {date} is not available.'
                print(message)
                return True, message
        except Exception as e:
            message = f'An error occurred: {e}'
            print(message)
            return True, message

    def get_bookings(self):
        """
        Get all the bookings from the database.
        :return: A dictionary of bookings
        """
        result = self.ref.get()
        slots = {}
        for key, val in result.items():
            for time, status in val.items():
                if status != 'unbooked' and time != 'available':
                    try:
                        slots[key][time] = status
                    except KeyError:
                        slots[key] = {time: status}
        return slots

    def find_booking(self, client: ClientInfo):
        """
        Check if a client has a booking.
        :param client: The client's details
        :return: A tuple of (found, date, time) or (False, False, False) if not found
        """
        bookings = self.get_bookings()

        for date, booking in bookings.items():
            for time, info in booking.items():
                for key, val in info.items():
                    check_info = ClientInfo(val['name'], val['email'], val['number'])
                    if check_info == client:
                        date = datetime.strptime(date, "%m-%d-%Y")
                        return True, date, time
        return False, False, False

    def find_booking_from_email(self, email: str):
        """ same as find_booking but with email instead of client object
        :return: A tuple of (found, date, time, client) or (False, False, False, False) if not found
        """
        bookings = self.get_bookings()

        for date, booking in bookings.items():
            for time, info in booking.items():
                for key, val in info.items():
                    check_info = ClientInfo(val['name'], val['email'], val['number'])
                    if check_info.email == email:
                        date = datetime.strptime(date, "%m-%d-%Y")
                        return True, date, time, check_info
        return False, False, False, False

    def check_booking(self, client: ClientInfo):
        """
        Uses the find_booking method to check if a client has a booking.
        :param client: The client's details
        :return: A string with the booking details or a message saying no booking was found
        """
        found, date, time = self.find_booking(client)
        if found:
            return f"Booking reserved for {client.name} on " \
                   f"{date.strftime('%A %d %B')} at {time}"
        return f"No booking found for {client.name}"

    def delete_booking(self, client: ClientInfo):
        """
        Delete a booking for a client.
        :param client: The client's details
        return: True if the booking was deleted, False if not
        """
        found, date, time = self.find_booking(client)
        date_ref = self.ref.child(date.strftime('%m-%d-%Y'))
        # time_ref = date_ref.child(time)
        if found:
            date_ref.update({time: 'unbooked'})
            return True
        return False

    def create_dates_for_week(self):
        """This script updates the list of dates in a Firebase database based on today's date."""
        # Get the dates from the Firebase reference object as a list of datetime objects
        today = datetime.today()
        weekday = today.weekday()

        dates = self.ref.get()
        dates = sorted([datetime.strptime(date, "%m-%d-%Y") for date in dates]) if dates else []

        # Remove the older dates from the database
        for date in dates:
            if date.date() < today.date():
                self.ref.child(date.strftime("%m-%d-%Y")).delete()
            else:
                break

        if dates and today <= dates[-1]:  # only create a new list if today is past the latest date in the database
            return
        else:  # empty old data before creating the new list of dates
            self.empty_database()

        # Check if today is Saturday or Sunday
        if weekday >= 5:
            # Skip to the next Monday
            start_date = today + timedelta(days=7 - weekday)
            # Create a list of dates from start date to Friday
            daterange = [start_date + timedelta(days=x) for x in range(5)]
        else:
            # Use today as the start date
            start_date = today
            # Create a list of dates from start date to Friday
            daterange = [start_date + timedelta(days=x) for x in range(0, 5 - weekday)]

        # Create a dictionary of time slots with unbooked status as values
        times = {
            "08:00": "unbooked",
            "09:00": "unbooked",
            "10:00": "unbooked",
            "11:00": "unbooked",
            "12:00": "unbooked",
            "14:00": "unbooked",
            "15:00": "unbooked"
        }
        for date in daterange:
            # Convert the date object to a string with mm-dd-yyyy format
            date_str = date.strftime("%m-%d-%Y")

            # Create a new node with this date as key and available status as True
            self.ref.child(date_str).set({
                **times,
                'available': True,
            })

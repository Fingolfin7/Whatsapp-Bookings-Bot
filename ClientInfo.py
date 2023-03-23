
class ClientInfo:
    def __init__(self, name: str, email: str, number: str):
        self.name = name
        self.email = email
        self.number = number

    def __eq__(self, other):
        """
           Compare two ClientInfo objects for equality based on their attributes.

           >>> c1 = ClientInfo("Alice", "alice@example.com", "1234567890")
           >>> c2 = ClientInfo("Bob", "bob@example.com", "0987654321")
           >>> c3 = ClientInfo("Alice", "alice@example.com", "1234567890")
           >>> c4 = ClientInfo("Kuda", "mushunjek@gmail.com", "0780640552")
           >>> dict1 = {'email': 'mushunjek@gmail.com', 'name': 'Kuda', 'number': '0780640552'}
           >>> c1 == c2
           False
           >>> c1 == c3
           True
           >>> c4 == dict1
           True
           >>> c2 == dict1
           False
        """
        if isinstance(other, self.__class__):
            return vars(self) == vars(other)
            # return self.email == other.email and self.number == other.number
        elif isinstance(other, dict):
            return self.name == other['name'] and\
                   self.email == other['email'] and\
                   self.number == other['number']

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str(vars(self))


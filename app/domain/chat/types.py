import enum

MESSAGE_HEADER = int(6)


class RequestType(enum.Enum):
    IDENTITY = int(0)
    JOIN_GROUP = int(1)
    DIRECT_MESSAGE = int(2)
    LEAVE_GROUP = int(3)
    FETCH_GROUPS = int(4)
    SEARCH_FOR_GROUP = int(5)
    DISCONNECT = int(6)
    MATCH_CONTACTS = int(7)


class ResponseType(enum.Enum):
    REQUEST_IDENTITY = int(0)
    IDENTITY_REJECTION = int(1)
    IDENTITY_ACCEPTED = int(2)
    DISCONNECTION_ACCEPTED = int(3)
    CONTACT_BATCH = int(4)
    RECEIVE_DIRECT_MESSAGE = int(5)
    DELIVERY_STATE = int(6)

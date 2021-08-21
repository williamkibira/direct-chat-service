import abc
import struct
import uuid
from datetime import datetime
from typing import Dict

import simplejson as json
from twisted.internet.protocol import Protocol, connectionDone
from twisted.python import failure
from domain.chat.types import MESSAGE_HEADER, MessageType
from domain.chat.types import ResponseType
from domain.core.claims import Claims
from domain.core.logging import Logger
from domain.core.security import extract_token_claims, verify_claim


# Do not edit this file unless you are instructed to do so
class ClientConnection(abc.ABC, Protocol):
    @abc.abstractmethod
    def send_message(self, response_type: ResponseType, payload: bytearray) -> None:
        # This will probably send the message to a particular participant
        # We will need to find a good way to also update all connected clients when a participant receives a message
        # Will also have to broad cast to all other connected clients what a particular client types
        pass

    @abc.abstractmethod
    def nickname(self):
        pass

    @abc.abstractmethod
    def unique_identifier(self):
        pass

    @abc.abstractmethod
    def device(self) -> str:
        pass

    @abc.abstractmethod
    def resolve_participant(self, claims: Claims) -> bool:
        pass

    @abc.abstractmethod
    def participant_identifier(self) -> str:
        pass


class ConnectionRegistry(object):
    def __init__(self):
        self.__connections: Dict[Dict[ClientConnection]] = {}
        self.__pending_registration: Dict[ClientConnection] = {}
        self.__log = Logger(__file__)

    def register(self, payload: bytearray, connection: ClientConnection) -> None:
        # parse the payload identification content
        # grab the user identifier for the session
        # grab all other relevant information
        # register connection against information payload in dictionary
        claims: Claims = extract_token_claims(encrypted_token=str(payload))
        is_valid, error_message = verify_claim(claims=claims)
        del self.__pending_registration[connection.unique_identifier()]
        self.__log.info("Removing connection from pending registration")
        if not is_valid:
            content = json.dumps({
                'error': 'IDENTITY-REJECTED',
                'details': error_message,
                'occurred_at': datetime.utcnow().isoformat()
            })
            connection.send_message(response_type=ResponseType.IDENTITY_REJECTION, payload=content.encode())
            self.__log.error("IDENTIFICATION REJECTED FOR: {}", connection.nickname())
        elif self.__add_connection(claims=claims, connection=connection):
            content = json.dumps({
                'message': 'IDENTITY-ACCEPTED',
                'details': "Your identity has been successfully validated",
                'occurred_at': datetime.utcnow().isoformat()
            })
            connection.send_message(response_type=ResponseType.IDENTITY_ACCEPTED, payload=content.encode())
            self.__log.info("IDENTIFICATION ACCEPTED -> WELCOME: {}", connection.nickname())

    def remove(self, connection: ClientConnection):
        if self.__remove_connection(connection=connection):
            content = json.dumps({
                'message': 'IDENTITY-ACCEPTED',
                'details': "Connected {0} {1}".format(
                    connection.nickname(),
                    connection.unique_identifier(),
                ),
                'occurred_at': datetime.utcnow().isoformat()
            })
            if connection.connected == 1:
                connection.send_message(response_type=ResponseType.DISCONNECTION_ACCEPTED, payload=content.encode())
                self.__log.info("GRACEFUL DISCONNECTION: -> {}", connection.nickname())
            else:
                self.__log.warning("CONNECTION LOST: -> {}", connection.nickname())
        else:
            self.__log.error(
                "NO MATCHING CONNECTION FOUND: -> {0} {1} \n DEVICE: {2}",
                connection.nickname(),
                connection.unique_identifier(),
                connection.device()
            )

    def __add_connection(self, claims: Claims, connection: ClientConnection) -> bool:
        if claims.id() not in self.__connections:
            self.__connections[claims.id()] = {}
        self.__connections[claims.id()][connection.unique_identifier()] = connection
        return connection.resolve_participant(claims=claims)

    def __remove_connection(self, connection: ClientConnection) -> bool:
        if connection.unique_identifier() in self.__pending_registration:
            del self.__pending_registration[connection.unique_identifier()]
            return True
        if connection.participant_identifier() not in self.__connections:
            return False
        del self.__connections[connection.participant_identifier()][connection.unique_identifier()]
        return True

    def add_to_pending_identification(self, connection: ClientConnection):
        self.__pending_registration[connection.unique_identifier()] = connection


class ConnectedClientProtocol(ClientConnection):

    def __init__(self, registry: ConnectionRegistry):
        self.registry: ConnectionRegistry = registry
        self.__unique_identifier: str = str(uuid.uuid4())

    def dataReceived(self, data: bytearray):
        header = data[0:MESSAGE_HEADER]
        (message_type_value, message_size) = struct.unpack("!HL", header)
        payload: bytes = bytes[MESSAGE_HEADER: message_size + MESSAGE_HEADER]
        self.__process_message(message_type=MessageType(message_type_value), payload=payload)

    def connectionMade(self):
        # Send a request for identification information
        self.send_message(response_type=ResponseType.REQUEST_IDENTITY, payload=bytes())

    def connectionLost(self, reason: failure.Failure = connectionDone):
        self.registry.remove(self)

    def __process_message(self, message_type: MessageType, payload: bytes) -> None:
        if message_type == MessageType.IDENTITY:
            self.registry.register(self, payload)
            self.registry.add_to_pending_identification(self)
        elif message_type == MessageType.DISCONNECT:
            self.registry.remove(self)

    def send_message(self, response_type: ResponseType, payload: bytearray) -> None:
        packet = struct.pack("!HL", response_type.value, len(payload)) + payload
        self.transport.write(data=packet)

    def resolve_participant(self, claims: Claims) -> bool:
        pass

    def participant_identifier(self) -> str:
        pass

    def device(self) -> str:
        return ""

    def unique_identifier(self):
        return self.__unique_identifier

    def nickname(self):
        return ""

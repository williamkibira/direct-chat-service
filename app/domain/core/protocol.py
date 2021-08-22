import abc
from datetime import datetime
from typing import Dict, NamedTuple, Optional

import simplejson as json
from pymessagebus import CommandBus
from twisted.internet.protocol import Protocol

from app.domain.chat.types import ResponseType
from app.core.logging.loggers import LoggerMixin
from app.core.security.claims import Claims
from app.domain.core.identification_pb2 import Identification, Device
from app.core.security.restriction import Restrictions


class DeviceDetails(object):
    def __init__(self, name: str, operating_system: str, version: str, ip_address: str):
        self.__name = name
        self.__operating_system = operating_system
        self.__version = version
        self.__ip_address = ip_address

    @property
    def name(self):
        return self.__name

    @property
    def operating_system(self):
        return self.__operating_system

    @property
    def version(self):
        return self.__version

    @property
    def ip_address(self):
        return self.__ip_address


def parse_from_device_proto(device: Device) -> DeviceDetails:
    return DeviceDetails(
        name=device.name,
        operating_system=device.operating_system,
        version=device.version,
        ip_address=device.ip_address
    )


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
    def device(self) -> Optional[DeviceDetails]:
        pass

    @abc.abstractmethod
    def resolve_participant(self, identifier: str, device_information: DeviceDetails) -> None:
        pass

    @abc.abstractmethod
    def participant_identifier(self) -> Optional[str]:
        pass


class DeviceBroadcastCommand(NamedTuple):
    participant_identifier: str
    unique_identifier: str
    response_type: ResponseType
    payload: bytearray


class DeviceCollective(object):
    def __init__(self, participant_identifier: str):
        self.__participant_identifier = participant_identifier
        self.__connections: Dict[ClientConnection] = []

    def add_connection(self, connection: ClientConnection, device_information: DeviceDetails) -> bool:
        self.__connections[connection.unique_identifier()] = connection
        connection.resolve_participant(identifier=self.__participant_identifier, device_information=device_information)

    def remove_connection(self, connection: ClientConnection) -> bool:
        if connection.unique_identifier() in self.__connections:
            del self.__connections[connection.unique_identifier()]
            return True
        return False

    def send_to_other_devices(self, unique_identifier: str, response_type: ResponseType, payload: bytearray) -> bool:
        [connection.send_message(response_type=response_type, payload=payload)
         for identifier, connection in self.__connections if identifier is not unique_identifier]
        return True


class ConnectionRegistry(LoggerMixin):
    def __init__(self, command_bus: CommandBus, restrictions: Restrictions):
        self.__connections: Dict[DeviceCollective] = {}
        self.__pending_registration: Dict[ClientConnection] = {}
        self.__restrictions: Restrictions = restrictions
        command_bus.add_handler(DeviceBroadcastCommand, self.__handle_device_broadcast)

    def register(self, payload: bytearray, connection: ClientConnection) -> None:
        identification: Identification = Identification()
        identification.ParseFromString(payload)
        device_information = parse_from_device_proto(device=identification.device)
        claims: Claims = self.__restrictions.extract_token_claims(encrypted_token=str(identification.token))
        is_valid, error_message = Restrictions.verify_claim(claims=claims)
        del self.__pending_registration[connection.unique_identifier()]
        self._logger.info("Removing connection from pending registration")
        if not is_valid:
            content = json.dumps({
                'error': 'IDENTITY-REJECTED',
                'details': error_message,
                'occurred_at': datetime.utcnow().isoformat()
            })
            connection.send_message(response_type=ResponseType.IDENTITY_REJECTION, payload=content.encode())
            self._logger.error("IDENTIFICATION REJECTED FOR: {}", connection.nickname())
        elif self.__add_connection(claims=claims, connection=connection, device_information=device_information):
            content = json.dumps({
                'message': 'IDENTITY-ACCEPTED',
                'details': "Your identity has been successfully validated",
                'occurred_at': datetime.utcnow().isoformat()
            })
            connection.send_message(response_type=ResponseType.IDENTITY_ACCEPTED, payload=content.encode())
            self._logger.info("IDENTIFICATION ACCEPTED -> WELCOME: {}", connection.nickname())

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
                self._logger.info("GRACEFUL DISCONNECTION: -> {}", connection.nickname())
            else:
                self._logger.warning("CONNECTION LOST: -> {}", connection.nickname())
        else:
            self._logger.error(
                "NO MATCHING CONNECTION FOUND: -> {0} {1} \n DEVICE: {2}",
                connection.nickname(),
                connection.unique_identifier(),
                connection.device()
            )

    def __add_connection(self, claims: Claims, device_information: DeviceDetails, connection: ClientConnection) -> bool:
        if claims.id() not in self.__connections:
            self.__connections[claims.id()] = DeviceCollective(participant_identifier=claims.id())
        return self.__connections[claims.id()].add_connection(connection=connection,
                                                              device_information=device_information)

    def __remove_connection(self, connection: ClientConnection) -> bool:
        if connection.unique_identifier() in self.__pending_registration:
            del self.__pending_registration[connection.unique_identifier()]
            return True
        if connection.participant_identifier() not in self.__connections:
            return self.__connections[connection.participant_identifier()].remove_connection(connection=connection)

    def add_to_pending_identification(self, connection: ClientConnection):
        self.__pending_registration[connection.unique_identifier()] = connection

    def __handle_device_broadcast(self, command: DeviceBroadcastCommand) -> None:
        self._logger.info("Received a broad cast for the other devices that are connected")
        self.__connections[command.participant_identifier].send_to_other_devices(
            unique_identifier=command.unique_identifier,
            payload=command.payload,
            response_type=command.response_type
        )
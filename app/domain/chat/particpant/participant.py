import struct
import uuid
from typing import Optional

from twisted.internet.protocol import connectionDone
from twisted.python import failure

from app.domain.chat.messages.contract import Message
from app.domain.chat.types import MESSAGE_HEADER, MessageType, ResponseType
from app.domain.core.protocol import ClientConnection, ConnectionRegistry, DeviceDetails


class Participant(object):
    def __init__(self):
        self.__identifier = ""
        self.__nickname = ""

    def on_direct_message_data_received(self, data: bytes) -> None:
        # Persist the message, then send it off
        pass

    def on_group_message_received(self, identifier: str, message: Message) -> None:
        pass

    @property
    def nickname(self):
        return self.__nickname

    @property
    def identifier(self):
        return self.__identifier


class ParticipantService(object):

    def fetch(self, identifier) -> Participant:
        pass


class ConnectedClientProtocol(ClientConnection):

    def __init__(self, registry: ConnectionRegistry, participant_service: ParticipantService):
        self.registry: ConnectionRegistry = registry
        self.__participant_service = participant_service
        self.__unique_identifier: str = str(uuid.uuid4())
        self.__participant_identifier: Optional[str] = None
        self.__device_information: Optional[DeviceDetails] = None

    def dataReceived(self, data: bytearray):
        header = data[0:MESSAGE_HEADER]
        (message_type_value, message_size) = struct.unpack("!HL", header)
        payload: bytes = bytes[MESSAGE_HEADER: message_size + MESSAGE_HEADER]
        self.__process_message(message_type=MessageType(message_type_value), payload=payload)

    def connectionMade(self):
        # Send a request for identification information
        self.registry.add_to_pending_identification(self)
        self.send_message(response_type=ResponseType.REQUEST_IDENTITY, payload="".encode())

    def connectionLost(self, reason: failure.Failure = connectionDone):
        self.registry.remove(self)

    def __process_message(self, message_type: MessageType, payload: bytes) -> None:
        if message_type == MessageType.IDENTITY:
            self.registry.register(self, payload)
        elif message_type == MessageType.DISCONNECT:
            self.registry.remove(self)

    def send_message(self, response_type: ResponseType, payload: bytearray) -> None:
        packet = struct.pack("!HL", response_type.value, len(payload)) + payload
        self.transport.write(data=packet)

    def resolve_participant(self, identifier: str, device_information: DeviceDetails) -> bool:
        self.__participant_identifier = identifier
        self.__device_information = device_information

    def participant_identifier(self) -> Optional[str]:
        return self.__participant_identifier

    def device(self) -> Optional[DeviceDetails]:
        return self.__device_information

    def unique_identifier(self):
        return self.__unique_identifier

    def nickname(self):
        return ""
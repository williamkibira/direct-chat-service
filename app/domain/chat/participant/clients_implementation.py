import asyncio
from distutils.util import strtobool
from typing import Optional, Dict, Callable, List, Type, T

from nats.aio.client import Client
from nats.aio.errors import ErrTimeout, ErrConnectionClosed, ErrNoServers

import app.domain.chat.participant.clients
from app.configuration import Configuration
from app.core.logging.loggers import LoggerMixin
from app.core.utilities.helpers import SingletonMixin
from app.domain.chat.participant.clients import ParticipantClient
from app.domain.chat.participant.node_pb2 import ParticipantPassOver, LocationRequest, LocationResponse, \
    ParticipantJoined, Result

ADDRESS_SERVICE: str = "v1/registry-service/address-book"


class NATSConfiguration(object):
    def __init__(self, content_map: Dict):
        self.servers: List[str] = content_map["servers"]
        self.verbose = bool(strtobool(content_map["verbose"]))
        self.allow_reconnect = bool(strtobool(content_map["allow_reconnect"]))
        self.connect_timeout = int(content_map["connect_timeout"])
        self.reconnect_time_wait = int(content_map["reconnect_time_wait"])
        self.max_reconnect_attempts = int(content_map["max_reconnect_attempts"])


class FakeParticipantClient(ParticipantClient, LoggerMixin, SingletonMixin):

    def __init__(self):
        self.__calls: Dict = {}
        self._info("LOADED FAKE PARTICIPANT CLIENT")
        app.domain.chat.participant.clients.registry = self

    def shutdown(self):
        pass

    def start_up(self):
        self._info("STARTED FAKE")
        for i, k in self.__calls:
            self._info("SUBJECT : {}", i)

    async def register_subscription_handler(self, subject: str, handler_callback: Callable):
        self.__calls[subject] = handler_callback
        self._info("REGISTERED A CALLBACK HANDLER")

    def __register_all_subscriptions(self):
        # TODO
        # iterate through all call backs and have a lambda function inline with protocol buffer parsing
        # await nc.subscribe("help.>", cb=message_handler)
        pass

    def register_participant(self, routing_identifier: str):
        pass

    def fetch_last_known_node(self, target_identifier) -> Optional[str]:
        pass


class NATSParticipantClient(ParticipantClient, LoggerMixin, SingletonMixin):

    def __init__(self):

        self.__configuration = NATSConfiguration(content_map=Configuration.get_instance().nats_configuration())
        self.__client: Client = Client()

    def start_up(self):
        try:
            self._info("CONNECTING TO NATS CLUSTER")
            self._info("CLUSTER: {0}".format(self.__configuration.servers))
            loop = asyncio.get_running_loop()
            if loop.is_running():
                loop.create_task(name="start-nats.io", coro=self.__client.connect(
                    servers=self.__configuration.servers,
                    verbose=self.__configuration.verbose,
                    allow_reconnect=self.__configuration.allow_reconnect,
                    connect_timeout=self.__configuration.connect_timeout,
                    reconnect_time_wait=self.__configuration.reconnect_time_wait,
                    max_reconnect_attempts=self.__configuration.max_reconnect_attempts,
                    error_cb=self.__on_error_callback,
                    disconnected_cb=self.__on_disconnected_callback,
                    reconnected_cb=self.__on_reconnected_callback,
                    closed_cb=self.__on_closed_callback,
                    discovered_server_cb=self.__on_discovered_callback,
                    loop=loop
                ))
                self._info("NATS.IO CLIENT CONNECTED")
                loop.create_task(name="register-nats.io-subscribers", coro=self.__register_all_subscriptions())
        except ErrNoServers as e:
            self._error(e)

    def shutdown(self):
        try:
            self._info("SHUTTING DOWN NATS.IO CLIENT")
            loop = asyncio.get_running_loop()
            if loop.is_running() and self.__client.is_connected():
                loop.create_task(name="start-nats.io", coro=self.__client.close())
                self._info("SHUTDOWN NATS.IO CLIENT")
        except ErrNoServers as e:
            self._error(e)

    def fetch_last_known_node(self, target_identifier) -> Optional[str]:
        if not self.__client.is_connected:
            self._error("NATS.IO CLIENT NOT CONNECTED")
            return None
        try:
            request: LocationRequest = LocationRequest(identifier=target_identifier)
            response = self.__client.request(subject="{}/{}".format(ADDRESS_SERVICE, "/current-location"),
                                             payload=request.SerializeToString())
            location: LocationResponse = LocationResponse()
            location.ParseFromString(response.data)
            return location.node
        except ErrConnectionClosed as e:
            self._error("Connection closed prematurely. {}", e)
            return None

        except ErrTimeout as e:
            self._error("Timeout occurred when publishing msg :{}".format(e))
            return None

    def register_participant(self, routing_identifier: str) -> None:
        if not self.__client.is_connected:
            self._error("NATS.IO CLIENT NOT CONNECTED")
            return None
        try:
            node: str = Configuration.get_instance().node()
            request: ParticipantJoined = ParticipantJoined(
                identifier=routing_identifier,
                node=node
            )
            response = self.__client.request(subject="{}/{}".format(ADDRESS_SERVICE, "/register"),
                                             payload=request.SerializeToString())
            result: Result = Result()
            result.ParseFromString(response.data)
            if result.status == Result.Status.SUCCESS:
                self._info("REGISTERED TO NODE: {} TO NODE: {} \n {}".format(
                    routing_identifier,
                    node,
                    result.message
                ))
            elif result.status == Result.Status.SUCCESS:
                self._error("FAILED TO REGISTER :{} TO NODE: {} TO NONE: {} \n {}".format(
                    routing_identifier,
                    node,
                    result.message
                ))

        except ErrConnectionClosed as e:
            self._error("Connection closed prematurely. {}", e)
            return None

        except ErrTimeout as e:
            self._error("Timeout occurred when publishing msg :{}".format(e))
            return None

    def passover_direct_message_to(self, node: str, passover: ParticipantPassOver) -> None:
        if not self.__client.is_connected:
            self._error("NATS.IO CLIENT NOT CONNECTED")
            return None
        try:
            self.__client.request(subject="v1/node/{}/participants/pass-over".format(node),
                                  payload=passover.SerializeToString())
        except ErrConnectionClosed as e:
            self._error("Connection closed prematurely. {}", e)
            return None

        except ErrTimeout as e:
            self._error("Timeout occurred when publishing msg :{}".format(e))
            return None

    def register_subscription_handler(self, subject: str,
                                      event_type: Type[T],
                                      handler_callback: Callable,
                                      subscriber: str):
        self.subscription_events[subject] = event_type
        self.subscription_methods[subject] = handler_callback
        self.subscription_classes[handler_callback] = subscriber
        self._info("REGISTERED CALLS")

    async def __register_all_subscriptions(self):
        for subject, method in self.subscription_methods.items():
            await self.__client.subscribe(
                subject=subject,
                cb=lambda msg: method(
                    self=self.subscribers[self.subscription_classes[method]],
                    event=self.parse_information(subject=msg.subject, content=msg.data))
            )
        await self.test_subscription()

    def parse_information(self, subject: str, content: bytearray):
        event_type = self.subscription_events[subject]
        message = event_type()
        message.ParseFromString(content)
        return message

    async def test_subscription(self):
        payload = ParticipantPassOver()
        payload.sender_identifier = "XXXXXX"
        payload.target_identifier = "YYYYYY"
        payload.originating_node = "saber-fox"
        payload.payload = "guniowevw".encode()
        await self.__client.publish(
            subject="v1/node/{}/participants/pass-over".format(Configuration.get_instance().node()),
            payload=payload.SerializeToString())

    async def __on_error_callback(self, error: Exception):
        self._error("{}".format(error))

    async def __on_disconnected_callback(self):
        self._warning("Disconnect from NATS.IO cluster")

    async def __on_closed_callback(self):
        self._info("Closing NATS.IO connection")

    async def __on_reconnected_callback(self):
        self._warning("Reconnecting to NATS.IO cluster")

    async def __on_discovered_callback(self):
        self._info("Discovered on NATS.IO cluster")

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: contacts.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='contacts.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0e\x63ontacts.proto\"o\n\x0e\x43ontactRequest\x12\r\n\x05value\x18\x01 \x01(\t\x12)\n\x04type\x18\x02 \x01(\x0e\x32\x1b.ContactRequest.ContactType\"#\n\x0b\x43ontactType\x12\t\n\x05\x45MAIL\x10\x00\x12\t\n\x05PHONE\x10\x01\"=\n\x18\x42\x61tchContactMatchRequest\x12!\n\x08requests\x18\x01 \x03(\x0b\x32\x0f.ContactRequest\"L\n\x07\x43ontact\x12\x10\n\x08nickname\x18\x01 \x01(\t\x12\x12\n\nidentifier\x18\x02 \x01(\t\x12\x1b\n\x13profile_picture_url\x18\x03 \x01(\t\"7\n\x19\x42\x61tchContactMatchResponse\x12\x1a\n\x08\x63ontacts\x18\x02 \x03(\x0b\x32\x08.Contactb\x06proto3'
)



_CONTACTREQUEST_CONTACTTYPE = _descriptor.EnumDescriptor(
  name='ContactType',
  full_name='ContactRequest.ContactType',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='EMAIL', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='PHONE', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=94,
  serialized_end=129,
)
_sym_db.RegisterEnumDescriptor(_CONTACTREQUEST_CONTACTTYPE)


_CONTACTREQUEST = _descriptor.Descriptor(
  name='ContactRequest',
  full_name='ContactRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='ContactRequest.value', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='type', full_name='ContactRequest.type', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _CONTACTREQUEST_CONTACTTYPE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=18,
  serialized_end=129,
)


_BATCHCONTACTMATCHREQUEST = _descriptor.Descriptor(
  name='BatchContactMatchRequest',
  full_name='BatchContactMatchRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='requests', full_name='BatchContactMatchRequest.requests', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=131,
  serialized_end=192,
)


_CONTACT = _descriptor.Descriptor(
  name='Contact',
  full_name='Contact',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='nickname', full_name='Contact.nickname', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='identifier', full_name='Contact.identifier', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='profile_picture_url', full_name='Contact.profile_picture_url', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=194,
  serialized_end=270,
)


_BATCHCONTACTMATCHRESPONSE = _descriptor.Descriptor(
  name='BatchContactMatchResponse',
  full_name='BatchContactMatchResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='contacts', full_name='BatchContactMatchResponse.contacts', index=0,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=272,
  serialized_end=327,
)

_CONTACTREQUEST.fields_by_name['type'].enum_type = _CONTACTREQUEST_CONTACTTYPE
_CONTACTREQUEST_CONTACTTYPE.containing_type = _CONTACTREQUEST
_BATCHCONTACTMATCHREQUEST.fields_by_name['requests'].message_type = _CONTACTREQUEST
_BATCHCONTACTMATCHRESPONSE.fields_by_name['contacts'].message_type = _CONTACT
DESCRIPTOR.message_types_by_name['ContactRequest'] = _CONTACTREQUEST
DESCRIPTOR.message_types_by_name['BatchContactMatchRequest'] = _BATCHCONTACTMATCHREQUEST
DESCRIPTOR.message_types_by_name['Contact'] = _CONTACT
DESCRIPTOR.message_types_by_name['BatchContactMatchResponse'] = _BATCHCONTACTMATCHRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ContactRequest = _reflection.GeneratedProtocolMessageType('ContactRequest', (_message.Message,), {
  'DESCRIPTOR' : _CONTACTREQUEST,
  '__module__' : 'contacts_pb2'
  # @@protoc_insertion_point(class_scope:ContactRequest)
  })
_sym_db.RegisterMessage(ContactRequest)

BatchContactMatchRequest = _reflection.GeneratedProtocolMessageType('BatchContactMatchRequest', (_message.Message,), {
  'DESCRIPTOR' : _BATCHCONTACTMATCHREQUEST,
  '__module__' : 'contacts_pb2'
  # @@protoc_insertion_point(class_scope:BatchContactMatchRequest)
  })
_sym_db.RegisterMessage(BatchContactMatchRequest)

Contact = _reflection.GeneratedProtocolMessageType('Contact', (_message.Message,), {
  'DESCRIPTOR' : _CONTACT,
  '__module__' : 'contacts_pb2'
  # @@protoc_insertion_point(class_scope:Contact)
  })
_sym_db.RegisterMessage(Contact)

BatchContactMatchResponse = _reflection.GeneratedProtocolMessageType('BatchContactMatchResponse', (_message.Message,), {
  'DESCRIPTOR' : _BATCHCONTACTMATCHRESPONSE,
  '__module__' : 'contacts_pb2'
  # @@protoc_insertion_point(class_scope:BatchContactMatchResponse)
  })
_sym_db.RegisterMessage(BatchContactMatchResponse)


# @@protoc_insertion_point(module_scope)

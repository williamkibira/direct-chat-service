#!/usr/bin/env bash

protoc -I protos/ protos/identification.proto --python_out=app/domain/core
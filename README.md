# CURF

## CAN UDS for Robot Framework

### CAN BUS with ISO-14229 implementation RobotFramework Library

The goal of this Robotframework Library is testing CAN BUS with RobotFramework

## CAN, UDS and ISO-TP Reminder

They are a lot of CAN protocols and it can be confusing.

CAN (ISO-11898) was released in 1991 and the main limit is the size of payload (8 Bytes) by frame.

ISO-TP (ISO 15765-2) TP means 'Transport Layer' was introducted in 2016. The main goal is the transfer of longer messages over CAN into multiples frames, adding metadata that allows the interpretation of individual frames and reassembly into a complete message packet by the recipient. It can carry up to 4095 bytes of payload per message packet.

UDS (ISO 14229-1) Unified Diagnostic Services is a communication protocol, Unified means that is an international and not company specific standard. This standard use ISO-TP.

## Compatibility

This RobotFramework library is cross-platform (tested under Debian9, and Windows 10)

The library use [python-can](https://python-can.readthedocs.io/en/master/index.html) to support CAN interface the interfaces [linked here](https://python-can.readthedocs.io/en/master/interfaces.html) must be compatibles.

The library use [isotp](https://can-isotp.readthedocs.io/en/latest/index.html) to handle ISO-15765 protocol

The library use [cantools](https://cantools.readthedocs.io/en/latest/) to encoding/decoding CAN Database, see [here](https://cantools.readthedocs.io/en/latest/#functions-and-classes) to find compatible format

## Requirements

They are a few dependencies, the library must work in Linux and Windows

```shell
pip install robotframework
pip install python-can
pip install cantools
pip install can-isotp
```

## Use

See testsuite/test.robot

All test must start with

```shell
Set CAN Bus ${INTERFACE} ${CHANNEL} ${BITRATE} ${DB FILE}
```

So the best can be to instanciate it with 'Test Setup'

Before using ISO-TP/UDS specific keywords you must instanciate it as follow:

```shell
Set ISOTP Protocol ${SOURCE} ${DESTINATION} ${ADDRESSING MODE}
```


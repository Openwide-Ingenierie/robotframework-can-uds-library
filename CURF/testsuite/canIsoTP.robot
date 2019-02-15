*** Settings ***
Resource      ../keywords/curf.robot
Test Setup      Set CAN Bus ${INTERFACE} ${CHANNEL} ${BITRATE} ${DB FILE} 
Test Teardown   End Log Can 
Library    DateTime

*** Variables ***
${DB FILE}              dbc/Example.dbc
${INTERFACE}            socketcan
${CHANNEL}              can0
${BITRATE}              500000
${DEFAULT TIMEOUT}      3
${DEFAULT NODE}         DRIVER
${SOURCE}               F1
${DESTINATION}          04
${ADDRESSING MODE}      NormalFixed_29bits

*** Test Cases ***

Test session change
    Set ISOTP Protocol ${SOURCE} ${DESTINATION} ${ADDRESSING MODE}
    Send DIAG Request 1002
    Diag Response Must Start With 5002

Disable DTC records
    Set ISOTP Protocol ${SOURCE} ${DESTINATION} ${ADDRESSING MODE}
    Send DIAG Request 8502
    Diag Response Must Be C502

Log the next ISO-TP frame
    Set ISOTP Protocol ${SOURCE} ${DESTINATION} ${ADDRESSING MODE}
    ${RES} =     Get Next DIAG Frame
    Log     ${RES}

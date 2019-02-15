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


*** Test Cases ***
Log Next Raw Frame
    ${Next_Frame} =     Get Next Raw Can Frame
    Log       ${Next_Frame}
   
Check reception of message
    Check The Reception Of SENSOR_SONARS TimeOut ${DEFAULT TIMEOUT} Seconds

Check non reception of message
    Check Message MOTOR_CMD TimeOut ${DEFAULT TIMEOUT} Seconds Is Not Received

Check reception of message in a given node
    Check The Reception Of SENSOR_SONARS TimeOut ${DEFAULT TIMEOUT} Seconds In Node ${DEFAULT NODE}

Check non reception of message in a given node
    Check Message SENSOR_SONARS TimeOut ${DEFAULT TIMEOUT} Seconds Is Not Received In Node ${DEFAULT NODE}

Send a CAN frame
    Send Frame With ID 0x5D3 And DEADBEEF As Data

Send a given signal
    Send Signal SENSOR_SONARS_err_count With Value 0

Check reception of a frame
    Check The Frame Reception With ID 5D3 And 0x0 As Data Timeout ${DEFAULT TIMEOUT} Seconds

Check reception of a frame with given ID and any data
    Check The Frame Reception With ID 5D3 And ANY As Data Timeout ${DEFAULT TIMEOUT} Seconds

Send periodic message
    Start Transmission Of Message SENSOR_SONARS Without Data With 1 Seconds Period
    Waiting 5 Seconds
    Start Transmission Of Message MOTOR_STATUS And 2 As Data With 1 Seconds Period
    Waiting 5 Seconds
    Stop Transmission Of Messages

Send periodic signal
    Start Transmission Of Signal SENSOR_SONARS_middle And 0 As Value With 1 Seconds Period
    Waiting 5 Seconds
    Stop Transmission Of Messages

Check the reception of a CAN signal
    Check CAN Signal SENSOR_SONARS_middle Equals To 0 TimeOut ${DEFAULT TIMEOUT} Seconds

Check the non reception of a CAN signal
    Check CAN Signal SENSOR_SONARS_err_count Is Not Received In Timeout ${DEFAULT TIMEOUT} Seconds

Check the periodicity of a frame with a given ID
    Check Frame ID 0x5D3 For 10 Times Expect Period 1 Seconds


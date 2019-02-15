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
${CONST1}                         0x9735A267
${CONST2}                         0x1F5C2C27
*** Test Cases ***
Clear diagnostic information
    Set ISOTP Protocol ${SOURCE} ${DESTINATION} ${ADDRESSING MODE}
    Clear All Diagnostic Information

Reset the ECU
    Set ISOTP Protocol ${SOURCE} ${DESTINATION} ${ADDRESSING MODE}
    Reset ECU 

Log a VehicleManufacturerSparePartNumber
    Set ISOTP Protocol ${SOURCE} ${DESTINATION} ${ADDRESSING MODE}
    ${RES} =     Report DID F187
    Log     ${RES}

Check the bit TestFailed
    Set ISOTP Protocol ${SOURCE} ${DESTINATION} ${ADDRESSING MODE}
    Clear All Diagnostic Information   
    &{DTCMaskRecords}=  Get DTCMaskRecords
    
    :FOR    ${key}    IN    @{DTCMaskRecords.keys()}
    \  The Bit testFailed Of statusOfDTC Must Be 0 For DTCMaskRecord ${DTCMaskRecords["${key}"]}
    
Check Security handshake
    Set ISOTP Protocol ${SOURCE} ${DESTINATION} ${ADDRESSING MODE}
    Send DIAG Request 2761
    ${Seed1} =  Get Next DIAG Frame
    ${Seed1} =  Remove The First 4 Char From ${Seed1}
    ${Seed1}    Catenate  SEPARATOR=  0x   ${Seed1}
    ${SeedKey} =     Get Key From Seed ${Seed1} With ${CONST1} As Const1 and ${CONST2} As Const2

    ${Key1}     Catenate  SEPARATOR=  2762    ${SeedKey}
    ${Key1}=  Set Variable      ${Key1}
    Send DIAG Request ${Key1}
    Diag Response Must Start With 6762

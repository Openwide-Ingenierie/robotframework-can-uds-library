*** Settings ***
Library    OperatingSystem
Library    ../base/Curf.py
Library    BuiltIn

*** Variables ***
${DEFAULT_DIAG_TIMEOUT}         5

*** Keywords ***

# Utilities

Waiting ${WAIT TIME} Seconds
	Waiting     ${WAIT TIME}

Remove The First ${NB_OF_BITS} Char From ${PAYLOAD}
        ${RESPONSE} =       Remove Char From        ${NB_OF_BITS}   ${PAYLOAD}
        [Return]        ${RESPONSE}  

${PAYLOAD} Length Must Be ${NB_OF_BYTES} Bytes
        Length Must Be        ${NB_OF_BYTES}   ${PAYLOAD}

# Can Bus Configuration

Set CAN Bus ${INTERFACE} ${CHANNEL} ${BITRATE} ${DB FILE}
    Set Can     ${INTERFACE}        ${CHANNEL}      ${BITRATE}      ${DB FILE}         ${TEST NAME}

Get CAN Bus Configuration
    ${RES} =    Get Can Config 
    [return]    ${RES}

Set ISOTP Protocol ${SOURCE} ${DESTINATION} ${ADDRESSING MODE}
    Set Isotp       ${SOURCE}       ${DESTINATION}      ${ADDRESSING MODE}       ${TEST NAME}

#Get CAN Bus State
#    ${RES} =    Get Can State
#    [return]    ${RES}

Clean CAN BUS
        FOR    ${i}    IN RANGE    10
    \    ${RES} = 	Get Next Raw Can Frame
    \    Log    ${RES}
    \    Exit For Loop If    '${RES}' == 'None'

Stop Bus
        Stop Bus

End Log Can
        End Can

# Non IsoTP CAN Keywords

Get Next Raw Can Frame
    ${RES} =    Get Next Raw Can 
    [return]    ${RES}

Check The Reception Of ${MSG NAME} TimeOut ${TIME OUT} Seconds
        Check Msg      ${MSG NAME}       ${TIME OUT}     False      None

Check Message ${MSG NAME} TimeOut ${TIME OUT} Seconds Is Not Received
        Check Msg      ${MSG NAME}            ${TIME OUT}      True     None

Check The Reception Of ${MSG NAME} TimeOut ${TIME OUT} Seconds In Node ${NODE}
        Check Msg      ${MSG NAME}       ${TIME OUT}     False      ${NODE}

Check Message ${MSG NAME} TimeOut ${TIME OUT} Seconds Is Not Received In Node ${NODE}
        Check Msg      ${MSG NAME}            ${TIME OUT}      True     ${NODE}

Send Frame With ID ${FRAME ID} And ${FRAME DATA} As Data
        Send Frame     ${FRAME ID}        ${FRAME DATA}

Send Signal ${SIGNAL NAME} With Value ${VALUE}
        Send Signal     ${SIGNAL NAME}        ${VALUE}

Check The Frame Reception With ID ${FRAME ID} And ${FRAME DATA} As Data Timeout ${TIMEOUT} Seconds
        Check Frame     ${FRAME ID}        ${FRAME DATA}        ${TIMEOUT}

Start Transmission Of Message ${MSG NAME} Without Data With ${PERIOD TIME} Seconds Period
	Send Periodic Message     ${MSG NAME}        ${PERIOD TIME}         None

Start Transmission Of Message ${MSG NAME} And ${DATA} As Data With ${PERIOD TIME} Seconds Period
	Send Periodic Message     ${MSG NAME}        ${PERIOD TIME}         ${DATA}

Stop Transmission Of Messages
        Stop Periodic Message

Start Transmission Of Signal ${SIGNAL NAME} And ${VALUE} As Value With ${PERIOD TIME} Seconds Period
	Send Periodic Signal     ${SIGNAL NAME}        ${VALUE}         ${PERIOD TIME}

Check CAN Signal ${SIGNAL NAME} Equals To ${SIGNAL VALUE} TimeOut ${TIME OUT} Seconds
       Check Signal      ${SIGNAL NAME}      ${SIGNAL VALUE}         ${TIME OUT}

Check CAN Signal ${SIGNAL NAME} Is Not Received
       Check Signal      ${SIGNAL NAME}        NoReception      10

Check CAN Signal ${SIGNAL NAME} Is Not Received In Timeout ${TIME OUT} Seconds
       Check Signal      ${SIGNAL NAME}        NoReception      ${TIME OUT}

Check Frame ID ${ID FRAME} For ${TIMES} Times Expect Period ${EXPECTED PERIOD} Seconds
        Check Period       ${ID FRAME}       ${EXPECTED PERIOD}      ${TIMES}


# Iso-TP Specific Keywords

Send DIAG Request ${DIAG MSG}
	Send Diagnostic Request   ${DIAG MSG}        Physical

Send DIAG Request ${DIAG MSG} Functional
	Send Diagnostic Request   ${DIAG MSG}        Functional

Diag Response Must Be ${REPONSE MSG}
        Check Diag Request   ${REPONSE MSG}   ${DEFAULT_DIAG_TIMEOUT}   EXACT

Diag Response Must Contain ${REPONSE MSG}
        Check Diag Request   ${REPONSE MSG}   ${DEFAULT_DIAG_TIMEOUT}   CONTAIN

Diag Response Must Start With ${REPONSE MSG}
        Check Diag Request   ${REPONSE MSG}   ${DEFAULT_DIAG_TIMEOUT}   START

Diag Response Must Not Start With ${REPONSE MSG}
        Check Diag Request   ${REPONSE MSG}   ${DEFAULT_DIAG_TIMEOUT}   NOTSTART

Get Next DIAG Frame
        ${DtcStatus} =   Get Next Isotp Frame   ${DEFAULT_DIAG_TIMEOUT} 
        [Return]        ${DtcStatus}

# UDS Specific Keywords

Clear All Diagnostic Information
  ...   Run Keywords 
  ...   Send Diagnostic Request   14FFFFFF
  ...   AND     Diag Response Must Be 54
  ...   AND     Waiting 1 Seconds

Reset ECU 
  ...   Run Keywords 
  ...   Send Diagnostic Request   1101
  ...   AND     Diag Response Must Be 5101
  ...   AND     Waiting 1 Seconds

Report DID ${RDI_NUMBER}
        ${RDI_CMD} =    Catenate        22    ${RDI_NUMBER}
        Send Diagnostic Request    ${RDI_CMD}
        ${RDI_RESPONSE} =     Get Next Isotp Frame    
        [Return]        ${RDI_RESPONSE}

${DtcSnapshot} Must Have DID Number ${DTCMaskRecord} Set To ${DID_VALUE}
        Check Snapshot   ${DtcSnapshot}   ${DTCMaskRecord}   ${DID_VALUE}

ReportDTCSnapshotRecordByDTCNumber ${DtcMaskRecord} ${SNAPSHOT_RECORD_NUMBER}
        ${DTC_CMD} =    Catenate        1904    ${DtcMaskRecord}        ${SNAPSHOT_RECORD_NUMBER}
        Send Diagnostic Request    ${DTC_CMD} 

ReportDTCExtendedDataRecordByDTCNumber ${DtcMaskRecord} ${EXT_DATA_RECORD_NUMBER}  
        ${DTC_CMD} =    Catenate        1906    ${DtcMaskRecord}        ${EXT_DATA_RECORD_NUMBER}
        Send Diagnostic Request    ${DTC_CMD}

reportNumberOfDTCBySeverityMaskRecord ${DtcSeverityMask} ${DtcStatusMask}
        ${DTC_CMD} =    Catenate        1907    ${DtcSeverityMask}        ${DtcStatusMask}
        Send Diagnostic Request    ${DTC_CMD}

reportDTCBySeverityMaskRecord ${DtcSeverityMask} ${DtcStatusMask} 
	${DTC_CMD} =    Catenate        1908    ${DtcSeverityMask}        ${DtcStatusMask}
        Send Diagnostic Request    ${DTC_CMD}
        
reportSeverityInformationOfDTC ${DtcMaskRecord}
        ${DTC_CMD} =    Catenate        1909    ${DtcMaskRecord}
        Send Diagnostic Request    ${DTC_CMD}
 
reportFirstConfirmedDTC
        Send Diagnostic Request    190C

reportMostRecentConfirmedDTC
        Send Diagnostic Request    190E

The Bit ${BIT_NAME} Of statusOfDTC Must Be ${BIT_VALUE} For DTCMaskRecord ${DtcMaskRecord} 
        ReportDTCSnapshotRecordByDTCNumber ${DtcMaskRecord} 01
        ${SnapShot}=    Get Next Isotp Frame   
        Log             ${SnapShot}
        Check Statusofdtc   ${BIT_NAME}    ${BIT_VALUE}    ${SnapShot}

Get DTCMaskRecords
        &{DTCMaskRecords} =     Create Dictionary	  0=010101   1=121212   2=232323   3=343434   4=454545   5=565656
        [Return]        &{DTCMaskRecords}

Get Key From Seed ${SEED} With ${CONST1} As Const1 and ${CONST2} As Const2
        ${Result_Key} =  Get Seedkey    ${SEED}       ${CONST1}       ${CONST2}
        [Return]        ${Result_Key}
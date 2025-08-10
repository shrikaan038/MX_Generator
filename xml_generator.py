# xml_generator.py
import datetime
import uuid
import re


def generate_pain001_xml(data):
    """
    Generates a pain.001 (Customer Credit Transfer Initiation) XML message.

    Args:
        data (dict): A dictionary containing the necessary data for the XML.
                     Expected keys: msgId, creDtTm, initgPtyNm, pmtInfId, pmtMtd,
                     btchBookg, reqdExctnDt, dbtrNm, dbtrStrtNm, dbtrBldgNb,
                     dbtrPstCd, dbtrTwnNm, dbtrCtry, dbtrAcctIBAN, dbtrAgtBICFI,
                     cdtrAgtBICFI, cdtrNm, cdtrStrtNm, cdtrBldgNb, cdtrPstCd,
                     cdtrTwnNm, cdtrCtry, cdtrAcctIBAN, instdAmt, ustrdRmtInf.
    Returns:
        str: The generated pain.001 XML string.
    """
    # The logic for pain001 is not the source of the current issue and remains unchanged.
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09 pain.001.001.09.xsd">
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>{data.get('msgId', '')}</MsgId>
            <CreDtTm>{data.get('creDtTm', '')}</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
            <InitgPty>
                <Nm>{data.get('initgPtyNm', '')}</Nm>
            </InitgPty>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>{data.get('pmtInfId', '')}</PmtInfId>
            <PmtMtd>{data.get('pmtMtd', '')}</PmtMtd>
            <BtchBookg>{str(data.get('btchBookg', False)).lower()}</BtchBookg>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>{data.get('instdAmt', 0.00):.2f}</CtrlSum>
            <PmtTpInf>
                <SvcLvl>
                    <Cd>SEPA</Cd>
                </SvcLvl>
            </PmtTpInf>
            <ReqdExctnDt>{data.get('reqdExctnDt', '')}</ReqdExctnDt>
            <Dbtr>
                <Nm>{data.get('dbtrNm', '')}</Nm>
                <PstlAdr>
                    <StrtNm>{data.get('dbtrStrtNm', '')}</StrtNm>
                    <BldgNb>{data.get('dbtrBldgNb', '')}</BldgNb>
                    <PstCd>{data.get('dbtrPstCd', '')}</PstCd>
                    <TwnNm>{data.get('dbtrTwnNm', '')}</TwnNm>
                    <Ctry>{data.get('dbtrCtry', '')}</Ctry>
                </PstlAdr>
            </Dbtr>
            <DbtrAcct>
                <Id>
                    <IBAN>{data.get('dbtrAcctIBAN', '')}</IBAN>
                </Id>
            </DbtrAcct>
            <DbtrAgt>
                <FinInstnId>
                    <BICFI>{data.get('dbtrAgtBICFI', '')}</BICFI>
                </FinInstnId>
            </DbtrAgt>
            <CdtrAgt>
                <FinInstnId>
                    <BICFI>{data.get('cdtrAgtBICFI', '')}</BICFI>
                </FinInstnId>
            </CdtrAgt>
            <Cdtr>
                <Nm>{data.get('cdtrNm', '')}</Nm>
                <PstlAdr>
                    <StrtNm>{data.get('cdtrStrtNm', '')}</StrtNm>
                    <BldgNb>{data.get('cdtrBldgNb', '')}</BldgNb>
                    <PstCd>{data.get('cdtrPstCd', '')}</PstCd>
                    <TwnNm>{data.get('cdtrTwnNm', '')}</TwnNm>
                    <Ctry>{data.get('cdtrCtry', '')}</Ctry>
                </PstlAdr>
            </Cdtr>
            <CdtrAcct>
                <Id>
                    <IBAN>{data.get('cdtrAcctIBAN', '')}</IBAN>
                </Id>
            </CdtrAcct>
            <Purp>
                <Cd>GDDS</Cd>
            </Purp>
            <RmtInf>
                <Ustrd>{data.get('ustrdRmtInf', '')}</Ustrd>
            </RmtInf>
            <CdtTrfTxInf>
                <PmtId>
                    <EndToEndId>E2EID{data.get('pmtInfId', '')}</EndToEndId>
                </PmtId>
                <PmtTpInf>
                    <InstrPrty>NORM</InstrPrty>
                </PmtTpInf>
                <Amt>
                    <InstdAmt Ccy="EUR">{data.get('instdAmt', 0.00):.2f}</InstdAmt>
                </Amt>
                <Dbtr>
                    <Nm>{data.get('dbtrNm', '')}</Nm>
                </Dbtr>
                <DbtrAcct>
                    <Id>
                        <IBAN>{data.get('dbtrAcctIBAN', '')}</IBAN>
                    </Id>
                </DbtrAcct>
                <DbtrAgt>
                    <FinInstnId>
                        <BICFI>{data.get('dbtrAgtBICFI', '')}</BICFI>
                    </FinInstnId>
                </DbtrAgt>
                <CdtrAgt>
                    <FinInstnId>
                        <BICFI>{data.get('cdtrAgtBICFI', '')}</BICFI>
                    </FinInstnId>
                </CdtrAgt>
                <Cdtr>
                    <Nm>{data.get('cdtrNm', '')}</Nm>
                </Dbtr>
                <CdtrAcct>
                    <Id>
                        <IBAN>{data.get('cdtrAcctIBAN', '')}</IBAN>
                    </Id>
                </CdtrAcct>
            </CdtTrfTxInf>
        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>
"""


def generate_pacs008_xml(data, channel_type, fedwire_type):
    """
    Generates a pacs.008 (FI to FI Customer Credit Transfer) XML message.

    Args:
        data (dict): A dictionary containing the necessary data for the XML.
                     Expected keys: msgId, creDtTm, intrBkSttlmDt, sttlmMtd,
                     instgAgtBICFI/instgAgtMmbId, instdAgtBICFI/instdAgtMmbId,
                     dbtrNm, dbtrStrtNm, dbtrBldgNb, dbtrPstCd, dbtrTwnNm,
                     dbtrCtry, dbtrAcctIBAN, dbtrAgtBICFI_tx/dbtrAgtMmbId,
                     cdtrAgtBICFI_tx/cdtrAgtMmbId, cdtrNm, cdtrStrtNm,
                     cdtrBldgNb, cdtrPstCd, cdtrTwnNm, cdtrCtry, cdtrAcctIBAN,
                     instdAmt, ustrdRmtInf, plus new keys for agent addresses.
        channel_type (str): 'fedwire' or 'swift' to determine XML structure.
        fedwire_type (str): 'domestic' or 'international' to apply specific Fedwire rules.
    Returns:
        str: The generated pacs.008 XML string.
    """
    msg_id = data.get('msgId', '')
    app_hdr = ""
    cre_dt_tm_formatted = ""

    if channel_type == 'swift':
        cre_dt_tm_formatted = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')
        app_hdr = f"""<?xml version="1.0" encoding="UTF-8"?>
    <AppHdr xmlns="urn:iso:std:iso:20022:tech:xsd:head.001.001.02">
        <Fr>
            <FIId>
                <FinInstnId>
                    <BICFI>{data.get('instgAgtBICFI', '')}</BICFI>
                </FinInstnId>
            </FIId>    
        </Fr>
        <To>
            <FIId>
                <FinInstnId>
                    <BICFI>{data.get('instdAgtBICFI', '')}</BICFI>
                </FinInstnId>
            </FIId>    
        </To>
        <BizMsgIdr>{msg_id}</BizMsgIdr>
        <MsgDefIdr>pacs.008.001.08</MsgDefIdr>
        <BizSvc>swift.cbprplus.02</BizSvc>
        <CreDt>{cre_dt_tm_formatted}</CreDt>
    </AppHdr>
    """

    elif channel_type == 'fedwire':
        cre_dt_tm_formatted = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        app_hdr = ""

    def get_agent_xml(agent_type, channel_type, fedwire_type, data):
        """
        Helper to generate agent XML for Debtor/Creditor Agent based on the rules.
        If BICFI or MmbId is not present, falls back to Name and Postal Address.
        """
        # Determine the correct keys for the agent based on type and channel
        if agent_type == 'DbtrAgt':
            bicfi = data.get('dbtrAgtBICFI_tx', '')
            mmb_id = data.get('dbtrAgtMmbId', '')
            name = data.get('dbtrAgtNm', '')
            street = data.get('dbtrAgtStrtNm', '')
            bldg_nb = data.get('dbtrAgtBldgNb', '')
            pst_cd = data.get('dbtrAgtPstCd', '')
            twn_nm = data.get('dbtrAgtTwnNm', '')
            ctry = data.get('dbtrAgtCtry', '')
        else:  # CdtrAgt
            bicfi = data.get('cdtrAgtBICFI_tx', '')
            mmb_id = data.get('cdtrAgtMmbId', '')
            name = data.get('cdtrAgtNm', '')
            street = data.get('cdtrAgtStrtNm', '')
            bldg_nb = data.get('cdtrAgtBldgNb', '')
            pst_cd = data.get('cdtrAgtPstCd', '')
            twn_nm = data.get('cdtrAgtTwnNm', '')
            ctry = data.get('cdtrAgtCtry', '')

        # Check for BICFI or MmbId first
        if channel_type == 'swift' and bicfi:
            return f"<FinInstnId><BICFI>{bicfi}</BICFI></FinInstnId>"

        if channel_type == 'fedwire':
            if fedwire_type == 'domestic' and mmb_id:
                return (f"""<FinInstnId>
                    <ClrSysMmbId>
                        <ClrSysId>
                            <Cd>USABA</Cd>
                        </ClrSysId>
                        <MmbId>{mmb_id}</MmbId>
                    </ClrSysMmbId>
                    <Nm>{name}</Nm>
                    <PstlAdr>
                        <StrtNm>{street}</StrtNm>
                        <BldgNb>{bldg_nb}</BldgNb>
                        <PstCd>{pst_cd}</PstCd>
                        <TwnNm>{twn_nm}</TwnNm>
                        <Ctry>{ctry}</Ctry>
                    </PstlAdr>
                </FinInstnId>""")
            if fedwire_type == 'international':
                if agent_type == 'DbtrAgt' and mmb_id:
                    return (f"""<FinInstnId>
                                    <ClrSysMmbId>
                                        <ClrSysId>
                                            <Cd>USABA</Cd>
                                        </ClrSysId>
                                        <MmbId>{mmb_id}</MmbId>
                                    </ClrSysMmbId>
                                    <Nm>{name}</Nm>
                                    <PstlAdr>
                                        <StrtNm>{street}</StrtNm>
                                        <BldgNb>{bldg_nb}</BldgNb>
                                        <PstCd>{pst_cd}</PstCd>
                                        <TwnNm>{twn_nm}</TwnNm>
                                        <Ctry>{ctry}</Ctry>
                                    </PstlAdr>
                                </FinInstnId>""")
                if agent_type == 'CdtrAgt' and bicfi:
                    return f"<FinInstnId><BICFI>{bicfi}</BICFI></FinInstnId>"

        # If no BICFI or MmbId is present, fall back to Name and Address
        # if name:
        #     # Note: The <FinInstnId> is included here and not in the main function
        #     return f"""<FinInstnId>
        #         <Nm>{name}</Nm>
        #         <PstlAdr>
        #             <StrtNm>{street}</StrtNm>
        #             <BldgNb>{bldg_nb}</BldgNb>
        #             <PstCd>{pst_cd}</PstCd>
        #             <TwnNm>{twn_nm}</TwnNm>
        #             <Ctry>{ctry}</Ctry>
        #         </PstlAdr>
        #     </FinInstnId>"""

        return ""  # Return empty string if no valid data is available

    def get_inst_agent_xml(agent_type, channel_type, data):
        """Helper to generate Instructing/Instructed Agent XML based on the channel."""
        if channel_type == 'swift':
            bicfi_key = 'instgAgtBICFI' if agent_type == 'InstgAgt' else 'instdAgtBICFI'
            return f"""<FinInstnId><BICFI>{data.get(bicfi_key, '')}</BICFI></FinInstnId>"""

        elif channel_type == 'fedwire':
            mmb_id_key = 'instgAgtMmbId' if agent_type == 'InstgAgt' else 'instdAgtMmbId'
            return f"""<FinInstnId><ClrSysMmbId><ClrSysId><Cd>USABA</Cd></ClrSysId><MmbId>{data.get(mmb_id_key, '')}</MmbId></ClrSysMmbId></FinInstnId>"""


    currency = data.get('currency', 'USD')

    # Generate the XML content
    xml_content = f"""{app_hdr}
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08 pacs.008.001.08.xsd">
    <FIToFICstmrCdtTrf>
        <GrpHdr>
            <MsgId>{data.get('msgId', '')}</MsgId>
            <CreDtTm>{cre_dt_tm_formatted}</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
            <SttlmInf>
                <SttlmMtd>{data.get('sttlmMtd', '')}</SttlmMtd>
                {f"<ClrSys><Cd>{'FDW' if channel_type == 'fedwire' else 'UNKN'}</Cd></ClrSys>" if channel_type == 'fedwire' else ""}
            </SttlmInf>
        </GrpHdr>
        <CdtTrfTxInf>
            <PmtId>
                <InstrId>INSTID{data.get('msgId', '')[:10]}</InstrId>
                <EndToEndId>E2EID{data.get('msgId', '')[:10]}</EndToEndId>
                <UETR>{str(uuid.uuid4())}</UETR>
            </PmtId>
            <PmtTpInf>
                <SvcLvl>
                    <Cd>NURG</Cd>
                </SvcLvl>
                {f"<LclInstrm><Prtry>CTRC</Prtry></LclInstrm>" if channel_type == 'fedwire' else ""}
            </PmtTpInf>
            <IntrBkSttlmAmt Ccy="{currency}">{data.get('instdAmt', 0.00):.2f}</IntrBkSttlmAmt>
            <IntrBkSttlmDt>{data.get('intrBkSttlmDt', '')}</IntrBkSttlmDt>
            <InstdAmt Ccy="{currency}">{data.get('instdAmt', 0.00):.2f}</InstdAmt>
            <ChrgBr>SHAR</ChrgBr>
            <InstgAgt>
                {get_inst_agent_xml('InstgAgt', channel_type, data)}
            </InstgAgt>
            <InstdAgt>
                {get_inst_agent_xml('InstdAgt', channel_type, data)}
            </InstdAgt>
            <Dbtr>
                <Nm>{data.get('dbtrNm', '')}</Nm>
                <PstlAdr>
                    <StrtNm>{data.get('dbtrStrtNm', '')}</StrtNm>
                    <BldgNb>{data.get('dbtrBldgNb', '')}</BldgNb>
                    <PstCd>{data.get('dbtrPstCd', '')}</PstCd>
                    <TwnNm>{data.get('dbtrTwnNm', '')}</TwnNm>
                    <Ctry>{data.get('dbtrCtry', '')}</Ctry>
                </PstlAdr>
            </Dbtr>
            <DbtrAcct>
                <Id>
                    <IBAN>{data.get('dbtrAcctIBAN', '')}</IBAN>
                </Id>
            </DbtrAcct>
            <DbtrAgt>
                {get_agent_xml('DbtrAgt', channel_type, fedwire_type, data)}
            </DbtrAgt>
            <CdtrAgt>
                {get_agent_xml('CdtrAgt', channel_type, fedwire_type, data)}
            </CdtrAgt>
            <Cdtr>
                <Nm>{data.get('cdtrNm', '')}</Nm>
                <PstlAdr>
                    <StrtNm>{data.get('cdtrStrtNm', '')}</StrtNm>
                    <BldgNb>{data.get('cdtrBldgNb', '')}</BldgNb>
                    <PstCd>{data.get('cdtrPstCd', '')}</PstCd>
                    <TwnNm>{data.get('cdtrTwnNm', '')}</TwnNm>
                    <Ctry>{data.get('cdtrCtry', '')}</Ctry>
                </PstlAdr>
            </Cdtr>
            <CdtrAcct>
                <Id>
                    <IBAN>{data.get('cdtrAcctIBAN', '')}</IBAN>
                </Id>
            </CdtrAcct>
            <RmtInf>
                <Ustrd>{data.get('ustrdRmtInf', '')}</Ustrd>
            </RmtInf>
        </CdtTrfTxInf>
    </FIToFICstmrCdtTrf>
</Document>
"""
    return xml_content
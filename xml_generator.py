# xml_generator_v03.py

import uuid

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
                </Cdtr>
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

def generate_pacs008_xml(data, pacs008_type='fedwire'):
    """
    Generates a pacs.008 (FI to FI Customer Credit Transfer) XML message.

    Args:
        data (dict): A dictionary containing the necessary data for the XML.
                     Expected keys: msgId, creDtTm, initgPtyNm, pmtInfId,
                     intrBkSttlmDt, sttlmMtd, instgAgtBICFI, instdAgtBICFI,
                     dbtrNm, dbtrStrtNm, dbtrBldgNb, dbtrPstCd, dbtrTwnNm,
                     dbtrCtry, dbtrAcctIBAN, dbtrAgtBICFI_tx, cdtrAgtBICFI_tx,
                     cdtrNm, cdtrStrtNm, cdtrBldgNb, cdtrPstCd, cdtrTwnNm,
                     cdtrCtry, cdtrAcctIBAN, instdAmt, ustrdRmtInf.
        pacs008_type (str): 'fedwire' or 'swift' to determine XML structure.
    Returns:
        str: The generated pacs.008 XML string.
    """

    # Helper function for agent FinInstnId based on type
    def get_agent_fin_instn_id_xml(agent_data_key_bicfi, mmb_id_fedwire, pacs_type):
        if pacs_type == 'fedwire':
            return f"""
                    <ClrSysMmbId>
                        <ClrSysId>
                            <Cd>USABA</Cd>
                        </ClrSysId>
                        <MmbId>{mmb_id_fedwire}</MmbId>
                    </ClrSysMmbId>
                """
        else: # swift
            return f"""<BICFI>{data.get(agent_data_key_bicfi, '')}</BICFI>"""

    currency = data.get('currency', 'USD') # Get currency from data

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08 pacs.008.001.08.xsd">
    <FIToFICstmrCdtTrf>
        <GrpHdr>
            <MsgId>{data.get('msgId', '')}</MsgId>
            <CreDtTm>{data.get('creDtTm', '')}</CreDtTm>
            <NbOfTxs>1</NbOfTxs>            
            <SttlmInf>
                <SttlmMtd>{data.get('sttlmMtd', '')}</SttlmMtd>
                {"" if pacs008_type == 'swift' else """
                <ClrSys> 
                    <Cd>FDW</Cd>
                </ClrSys> 
                """}
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
                {"" if pacs008_type == 'swift' else """
                <LclInstrm>
                    <Prtry>CTRC</Prtry>
                </LclInstrm>
                """}
            </PmtTpInf>
            <IntrBkSttlmAmt Ccy="{currency}">{data.get('instdAmt', 0.00):.2f}</IntrBkSttlmAmt>
            <IntrBkSttlmDt>{data.get('intrBkSttlmDt', '')}</IntrBkSttlmDt>
            <InstdAmt Ccy="{currency}">{data.get('instdAmt', 0.00):.2f}</InstdAmt>
            <ChrgBr>SHAR</ChrgBr>
            <InstgAgt>
                <FinInstnId>
                    {get_agent_fin_instn_id_xml('instgAgtBICFI', '011104238', pacs008_type)}
                </FinInstnId>
            </InstgAgt>
            <InstdAgt>
                <FinInstnId>
                    {get_agent_fin_instn_id_xml('instdAgtBICFI', '021040078', pacs008_type)}
                </FinInstnId>
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
                <FinInstnId>
                    <BICFI>{data.get('dbtrAgtBICFI_tx', '')}</BICFI>
                </FinInstnId>
            </DbtrAgt>
            <CdtrAgt>
                <FinInstnId>
                    <BICFI>{data.get('cdtrAgtBICFI_tx', '')}</BICFI>
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
            <RmtInf>
                <Ustrd>{data.get('ustrdRmtInf', '')}</Ustrd>
            </RmtInf>
        </CdtTrfTxInf>
    </FIToFICstmrCdtTrf>
</Document>
"""
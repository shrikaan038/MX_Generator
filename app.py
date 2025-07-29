# app_v03.py
import streamlit as st
import datetime
import uuid
import random # Added for generating random digits for Fedwire MsgId
from xml_generator import generate_pain001_xml, generate_pacs008_xml

st.set_page_config(layout="wide", page_title="ISO 20022 XML Payment Generator")

# Custom CSS for styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        font-size: 2.5em;
        color: #1a202c;
        text-align: center;
        margin-bottom: 1.5em;
        font-weight: 700;
    }
    .stButton>button {
        background-color: #2563eb; /* Blue-600 */
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #3b82f6; /* Blue-500 */
        transform: translateY(-1px);
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea {
        border-radius: 0.375rem;
        border: 1px solid #d1d5db;
        padding: 0.5rem 0.75rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1em;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>ISO 20022 XML Payment Generator</h1>", unsafe_allow_html=True)

# Function to get current datetime in required format (+HH:MM offset)
def get_current_datetime_with_offset():
    now = datetime.datetime.now(datetime.timezone.utc)
    # Format to YYYY-MM-DDTHH:MM:SS+00:00 for UTC, which is common for SWIFT CBPR+
    return now.strftime('%Y-%m-%dT%H:%M:%S+00:00')


# Initialize session state for form data and generated XML
if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'pain001': {
            'msgId': f"MSG{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            'creDtTm': get_current_datetime_with_offset(),
            'initgPtyNm': 'Originator Company',
            'pmtInfId': f"PMTINF{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            'pmtMtd': 'TRF',
            'btchBookg': True,
            'reqdExctnDt': (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
            'dbtrNm': 'Debtor Name',
            'dbtrStrtNm': 'Debtor Street',
            'dbtrBldgNb': '10',
            'dbtrPstCd': '10001',
            'dbtrTwnNm': 'New York',
            'dbtrCtry': 'US',
            'dbtrAcctIBAN': 'US12345678901234567890',
            'dbtrAgtBICFI': 'DBTRUS33XXX',
            'cdtrAgtBICFI': 'CDTRGB2LXXX',
            'cdtrNm': 'Creditor Name',
            'cdtrStrtNm': 'Creditor Street',
            'cdtrBldgNb': '20',
            'cdtrPstCd': 'SW1A0AA',
            'cdtrTwnNm': 'London',
            'cdtrCtry': 'GB',
            'cdtrAcctIBAN': 'GB98765432109876543210',
            'instdAmt': 100.00,
            'ustrdRmtInf': 'Payment for services rendered - Invoice ABC123',
            'currency': 'EUR' # Default for pain.001
        },
        'pacs008': {
            'msgId': '', # Initialized empty, will be set by input field based on channel type
            'creDtTm': get_current_datetime_with_offset(),
            'intrBkSttlmDt': (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
            'sttlmMtd': 'CLRG', # Default to CLRG, will be dynamically set
            'instgAgtBICFI': 'INSTGB2LXXX', # Used for SWIFT only now
            'instdAgtBICFI': 'CDTRGB2LXXX', # Used for SWIFT only now
            'txId': f"TX{uuid.uuid4().hex[:14].upper()}", # Updated to be exactly 16 chars for SWIFT
            'dbtrNm': 'Debtor Name',
            'dbtrStrtNm': 'Debtor Street',
            'dbtrBldgNb': '123',
            'dbtrPstCd': '12345',
            'dbtrTwnNm': 'Debtor City',
            'dbtrCtry': 'US',
            'dbtrAcctIBAN': 'US12345678901234567890',
            'dbtrAgtBICFI_tx': 'DBTRUS33XXX',
            'cdtrAgtBICFI_tx': 'CDTRGB2LXXX',
            'cdtrNm': 'Creditor Name',
            'cdtrStrtNm': 'Creditor Street',
            'cdtrBldgNb': '456',
            'cdtrPstCd': 'SW1A0AA',
            'cdtrTwnNm': 'London',
            'cdtrCtry': 'GB',
            'cdtrAcctIBAN': 'GB98765432109876543210',
            'instdAmt': 100.00,
            'ustrdRmtInf': 'Invoice 67890',
            'currency': 'USD' # Default for pacs.008
        }
    }
if 'generated_xml' not in st.session_state:
    st.session_state.generated_xml = ""
if 'message_type' not in st.session_state:
    st.session_state.message_type = 'pacs008' # Default to pacs008 for initial view

# Type selection for ISO 20022 message
st.session_state.message_type = st.radio(
    "Select ISO 20022 Message Type:",
    ('pacs008', 'pain001'),
    key="message_type_selector",
    horizontal=True
)

# Render forms based on selection
if st.session_state.message_type == 'pain001':
    st.subheader("pain.001 - Customer Credit Transfer Initiation")

    # Group Header (GrpHdr)
    st.markdown("### Group Header")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.form_data['pain001']['msgId'] = st.text_input("Message ID (MsgId)", value=st.session_state.form_data['pain001']['msgId'], key="pain001_msgId")
        st.session_state.form_data['pain001']['initgPtyNm'] = st.text_input("Initiating Party Name (InitgPty.Nm)", value=st.session_state.form_data['pain001']['initgPtyNm'], key="pain001_initgPtyNm")
    with col2:
        st.session_state.form_data['pain001']['creDtTm'] = st.text_input("Creation Date Time (CreDtTm)", value=st.session_state.form_data['pain001']['creDtTm'], key="pain001_creDtTm")
        st.session_state.form_data['pain001']['btchBookg'] = st.checkbox("Batch Booking (BtchBookg)", value=st.session_state.form_data['pain001']['btchBookg'], key="pain001_btchBookg")

    # Payment Information (PmtInf)
    st.markdown("### Payment Information")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.form_data['pain001']['pmtInfId'] = st.text_input("Payment Information ID (PmtInfId)", value=st.session_state.form_data['pain001']['pmtInfId'], key="pain001_pmtInfId")
        st.session_state.form_data['pain001']['pmtMtd'] = st.selectbox("Payment Method (PmtMtd)", ['TRF'], index=0, key="pain001_pmtMtd")
    with col2:
        st.session_state.form_data['pain001']['reqdExctnDt'] = st.text_input("Requested Execution Date (ReqdExctnDt)", value=st.session_state.form_data['pain001']['reqdExctnDt'], key="pain001_reqdExctnDt")
        st.session_state.form_data['pain001']['currency'] = st.text_input("Currency (e.g., EUR, USD)", value=st.session_state.form_data['pain001']['currency'], key="pain001_currency")


    # Debtor (Dbtr)
    st.markdown("### Debtor Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.form_data['pain001']['dbtrNm'] = st.text_input("Debtor Name (Dbtr.Nm)", value=st.session_state.form_data['pain001']['dbtrNm'], key="pain001_dbtrNm")
        st.session_state.form_data['pain001']['dbtrStrtNm'] = st.text_input("Debtor Street (Dbtr.PstlAdr.StrtNm)", value=st.session_state.form_data['pain001']['dbtrStrtNm'], key="pain001_dbtrStrtNm")
        st.session_state.form_data['pain001']['dbtrBldgNb'] = st.text_input("Debtor Building Number (Dbtr.PstlAdr.BldgNb)", value=st.session_state.form_data['pain001']['dbtrBldgNb'], key="pain001_dbtrBldgNb")
    with col2:
        st.session_state.form_data['pain001']['dbtrPstCd'] = st.text_input("Debtor Post Code (Dbtr.PstlAdr.PstCd)", value=st.session_state.form_data['pain001']['dbtrPstCd'], key="pain001_dbtrPstCd")
        st.session_state.form_data['pain001']['dbtrTwnNm'] = st.text_input("Debtor Town Name (Dbtr.PstlAdr.TwnNm)", value=st.session_state.form_data['pain001']['dbtrTwnNm'], key="pain001_dbtrTwnNm")
        st.session_state.form_data['pain001']['dbtrCtry'] = st.text_input("Debtor Country (Dbtr.PstlAdr.Ctry)", value=st.session_state.form_data['pain001']['dbtrCtry'], key="pain001_dbtrCtry")
    with col3:
        st.session_state.form_data['pain001']['dbtrAcctIBAN'] = st.text_input("Debtor Account IBAN (DbtrAcct.Id.IBAN)", value=st.session_state.form_data['pain001']['dbtrAcctIBAN'], key="pain001_dbtrAcctIBAN")
        st.session_state.form_data['pain001']['dbtrAgtBICFI'] = st.text_input("Debtor Agent BICFI (DbtrAgt.FinInstnId.BICFI)", value=st.session_state.form_data['pain001']['dbtrAgtBICFI'], key="pain001_dbtrAgtBICFI")

    # Creditor (Cdtr)
    st.markdown("### Creditor Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.form_data['pain001']['cdtrNm'] = st.text_input("Creditor Name (Cdtr.Nm)", value=st.session_state.form_data['pain001']['cdtrNm'], key="pain001_cdtrNm")
        st.session_state.form_data['pain001']['cdtrStrtNm'] = st.text_input("Creditor Street (Cdtr.PstlAdr.StrtNm)", value=st.session_state.form_data['pain001']['cdtrStrtNm'], key="pain001_cdtrStrtNm")
        st.session_state.form_data['pain001']['cdtrBldgNb'] = st.text_input("Creditor Building Number (Cdtr.PstlAdr.BldgNb)", value=st.session_state.form_data['pain001']['cdtrBldgNb'], key="pain001_cdtrBldgNb")
    with col2:
        st.session_state.form_data['pain001']['cdtrPstCd'] = st.text_input("Creditor Post Code (Cdtr.PstlAdr.PstCd)", value=st.session_state.form_data['pain001']['cdtrPstCd'], key="pain001_cdtrPstCd")
        st.session_state.form_data['pain001']['cdtrTwnNm'] = st.text_input("Creditor Town Name (Cdtr.PstlAdr.TwnNm)", value=st.session_state.form_data['pain001']['cdtrTwnNm'], key="pain001_cdtrTwnNm")
        st.session_state.form_data['pain001']['cdtrCtry'] = st.text_input("Creditor Country (Cdtr.PstlAdr.Ctry)", value=st.session_state.form_data['pain001']['cdtrCtry'], key="pain001_cdtrCtry")
    with col3:
        st.session_state.form_data['pain001']['cdtrAcctIBAN'] = st.text_input("Creditor Account IBAN (CdtrAcct.Id.IBAN)", value=st.session_state.form_data['pain001']['cdtrAcctIBAN'], key="pain001_cdtrAcctIBAN")
        st.session_state.form_data['pain001']['cdtrAgtBICFI'] = st.text_input("Creditor Agent BICFI (CdtrAgt.FinInstnId.BICFI)", value=st.session_state.form_data['pain001']['cdtrAgtBICFI'], key="pain001_cdtrAgtBICFI")

    # Transaction Details
    st.markdown("### Transaction Details")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.form_data['pain001']['instdAmt'] = st.number_input("Instructed Amount (InstdAmt)", value=float(st.session_state.form_data['pain001']['instdAmt']), min_value=0.01, step=0.01, format="%.2f", key="pain001_instdAmt")
    with col2:
        st.session_state.form_data['pain001']['ustrdRmtInf'] = st.text_area("Unstructured Remittance Info (RmtInf.Ustrd)", st.session_state.form_data['pain001']['ustrdRmtInf'], key="pain001_ustrdRmtInf")


else: # pacs008
    st.subheader("pacs.008 - FI to FI Customer Credit Transfer")

    # Add a radio button for Fedwire vs SWIFT
    pacs008_channel_type = st.radio(
        "Select pacs.008 Channel Type:",
        ('Fedwire', 'SWIFT'),
        key="pacs008_channel_type_selector",
        horizontal=True
    )
    pacs008_channel_type_lower = pacs008_channel_type.lower()

    # Dynamic SttlmMtd options based on channel type
    if pacs008_channel_type_lower == 'fedwire':
        sttlm_mtd_options = ['CLRG']
        if st.session_state.form_data['pacs008']['sttlmMtd'] != 'CLRG':
            st.session_state.form_data['pacs008']['sttlmMtd'] = 'CLRG'
        sttlm_mtd_index = 0
    else: # SWIFT
        sttlm_mtd_options = ['INDA', 'COVE'] # Assuming INDA and COVE are valid for SWIFT
        if st.session_state.form_data['pacs008']['sttlmMtd'] == 'CLRG' or st.session_state.form_data['pacs008']['sttlmMtd'] not in sttlm_mtd_options:
            st.session_state.form_data['pacs008']['sttlmMtd'] = 'INDA' # Set a default for SWIFT
        sttlm_mtd_index = sttlm_mtd_options.index(st.session_state.form_data['pacs008']['sttlmMtd'])


    # Group Header (GrpHdr)
    st.markdown("### Group Header")
    col1, col2 = st.columns(2)

    current_date = datetime.datetime.now().strftime('%Y%m%d')
    if pacs008_channel_type_lower == 'fedwire':
        # Generate Fedwire-specific MsgId: [0-9]{8}[A-Z0-9]{8}[0-9]{6}
        unique_alpha = uuid.uuid4().hex[8:16].upper() # 8 alphanumeric chars
        sequence_digits = str(random.randint(0, 999999)).zfill(6) # 6 random digits
        default_msg_id_pacs008 = f"{current_date}{unique_alpha}{sequence_digits}"
    else: # SWIFT
        # General SWIFT-like MsgId (UUID based)
        default_msg_id_pacs008 = f"{current_date}SWIFT{uuid.uuid4().hex[:10].upper()}"

    with col1:
        st.session_state.form_data['pacs008']['msgId'] = st.text_input(
            "Message ID (MsgId)",
            value=default_msg_id_pacs008, # Set default value dynamically
            key="pacs008_msgId"
        )
        st.session_state.form_data['pacs008']['sttlmMtd'] = st.selectbox(
            "Settlement Method (SttlmMtd)",
            options=sttlm_mtd_options, # Use dynamic options
            index=sttlm_mtd_index,     # Use dynamic index
            key="pacs008_sttlmMtd"
        )
    with col2:
        st.session_state.form_data['pacs008']['creDtTm'] = st.text_input("Creation Date Time (CreDtTm)", value=st.session_state.form_data['pacs008']['creDtTm'], key="pacs008_creDtTm")
        st.session_state.form_data['pacs008']['intrBkSttlmDt'] = st.text_input("Interbank Settlement Date (IntrBkSttlmDt)", value=st.session_state.form_data['pacs008']['intrBkSttlmDt'], key="pacs008_intrBkSttlmDt")

    # Conditional Agent BICFI inputs
    if pacs008_channel_type_lower == 'swift':
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.form_data['pacs008']['instgAgtBICFI'] = st.text_input("Instructing Agent BICFI (GrpHdr.InstgAgt.BICFI)", value=st.session_state.form_data['pacs008']['instgAgtBICFI'], key="pacs008_instgAgtBICFI")
        with col2:
            st.session_state.form_data['pacs008']['instdAgtBICFI'] = st.text_input("Instructed Agent BICFI (CdtTrfTxInf.InstdAgt.BICFI)", value=st.session_state.form_data['pacs008']['instdAgtBICFI'], key="pacs008_instdAgtBICFI")
    else:
        st.info("Instructing and Instructed Agent IDs are hardcoded for Fedwire (USABA).")
        # Ensure BICFI fields are cleared/defaulted if switching from Swift to Fedwire
        st.session_state.form_data['pacs008']['instgAgtBICFI'] = ''
        st.session_state.form_data['pacs008']['instdAgtBICFI'] = ''


    # Transaction Information (TxId)
    st.markdown("### Transaction Information")
    st.session_state.form_data['pacs008']['txId'] = st.text_input(
        "Transaction ID (TxId)",
        value=st.session_state.form_data['pacs008']['txId'],
        help="Max 16 characters for SWIFT pacs.008", # Added guidance
        key="pacs008_txId"
    )

    # Debtor (Dbtr)
    st.markdown("### Debtor Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.form_data['pacs008']['dbtrNm'] = st.text_input("Debtor Name (Dbtr.Nm)", value=st.session_state.form_data['pacs008']['dbtrNm'], key="pacs008_dbtrNm")
        st.session_state.form_data['pacs008']['dbtrStrtNm'] = st.text_input("Debtor Street (Dbtr.PstlAdr.StrtNm)", value=st.session_state.form_data['pacs008']['dbtrStrtNm'], key="pacs008_dbtrStrtNm")
        st.session_state.form_data['pacs008']['dbtrBldgNb'] = st.text_input("Debtor Building Number (Dbtr.PstlAdr.BldgNb)", value=st.session_state.form_data['pacs008']['dbtrBldgNb'], key="pacs008_dbtrBldgNb")
    with col2:
        st.session_state.form_data['pacs008']['dbtrPstCd'] = st.text_input("Debtor Post Code (Dbtr.PstlAdr.PstCd)", value=st.session_state.form_data['pacs008']['dbtrPstCd'], key="pacs008_dbtrPstCd")
        st.session_state.form_data['pacs008']['dbtrTwnNm'] = st.text_input("Debtor Town Name (Dbtr.PstlAdr.TwnNm)", value=st.session_state.form_data['pacs008']['dbtrTwnNm'], key="pacs008_dbtrTwnNm")
        st.session_state.form_data['pacs008']['dbtrCtry'] = st.text_input("Debtor Country (Dbtr.PstlAdr.Ctry)", value=st.session_state.form_data['pacs008']['dbtrCtry'], key="pacs008_dbtrCtry")
    with col3:
        st.session_state.form_data['pacs008']['dbtrAcctIBAN'] = st.text_input("Debtor Account IBAN (DbtrAcct.Id.IBAN)", value=st.session_state.form_data['pacs008']['dbtrAcctIBAN'], key="pacs008_dbtrAcctIBAN")
        st.session_state.form_data['pacs008']['dbtrAgtBICFI_tx'] = st.text_input("Debtor Agent BICFI (DbtrAgt.FinInstnId.BICFI)", value=st.session_state.form_data['pacs008']['dbtrAgtBICFI_tx'], key="pacs008_dbtrAgtBICFI_tx")

    # Creditor (Cdtr)
    st.markdown("### Creditor Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.form_data['pacs008']['cdtrNm'] = st.text_input("Creditor Name (Cdtr.Nm)", value=st.session_state.form_data['pacs008']['cdtrNm'], key="pacs008_cdtrNm")
        st.session_state.form_data['pacs008']['cdtrStrtNm'] = st.text_input("Creditor Street (Cdtr.PstlAdr.StrtNm)", value=st.session_state.form_data['pacs008']['cdtrStrtNm'], key="pacs008_cdtrStrtNm")
        st.session_state.form_data['pacs008']['cdtrBldgNb'] = st.text_input("Creditor Building Number (Cdtr.PstlAdr.BldgNb)", value=st.session_state.form_data['pacs008']['cdtrBldgNb'], key="pacs008_cdtrBldgNb")
    with col2:
        st.session_state.form_data['pacs008']['cdtrPstCd'] = st.text_input("Creditor Post Code (Cdtr.PstlAdr.PstCd)", value=st.session_state.form_data['pacs008']['cdtrPstCd'], key="pacs008_cdtrPstCd")
        st.session_state.form_data['pacs008']['cdtrTwnNm'] = st.text_input("Creditor Town Name (Cdtr.PstlAdr.TwnNm)", value=st.session_state.form_data['pacs008']['cdtrTwnNm'], key="pacs008_cdtrTwnNm")
    with col3:
        st.session_state.form_data['pacs008']['cdtrCtry'] = st.text_input("Creditor Country (Cdtr.PstlAdr.Ctry)", value=st.session_state.form_data['pacs008']['cdtrCtry'], key="pacs008_cdtrCtry")
    with col3:
        st.session_state.form_data['pacs008']['cdtrAcctIBAN'] = st.text_input("Creditor Account IBAN (CdtrAcct.Id.IBAN)", value=st.session_state.form_data['pacs008']['cdtrAcctIBAN'], key="pacs008_cdtrAcctIBAN")
        st.session_state.form_data['pacs008']['cdtrAgtBICFI_tx'] = st.text_input("Creditor Agent BICFI (CdtrAgt.FinInstnId.BICFI)", value=st.session_state.form_data['pacs008']['cdtrAgtBICFI_tx'], key="pacs008_cdtrAgtBICFI_tx")

    # Transaction Details
    st.markdown("### Transaction Details")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.form_data['pacs008']['instdAmt'] = st.number_input("Instructed Amount (InstdAmt)", value=float(st.session_state.form_data['pacs008']['instdAmt']), min_value=0.01, step=0.01, format="%.2f", key="pacs008_instdAmt")
        st.session_state.form_data['pacs008']['currency'] = st.text_input("Currency (e.g., USD, EUR)", value=st.session_state.form_data['pacs008']['currency'], key="pacs008_currency")
    with col2:
        st.session_state.form_data['pacs008']['ustrdRmtInf'] = st.text_area("Unstructured Remittance Info", st.session_state.form_data['pacs008']['ustrdRmtInf'], key="pacs008_ustrdRmtInf")


# Generate XML button
if st.button("Generate XML", key="generate_xml_button"):
    if st.session_state.message_type == 'pain001':
        st.session_state.generated_xml = generate_pain001_xml(st.session_state.form_data['pain001'])
    else: # pacs008
        st.session_state.generated_xml = generate_pacs008_xml(st.session_state.form_data['pacs008'], pacs008_channel_type_lower)

# Display generated XML
if st.session_state.generated_xml:
    st.markdown("---")
    st.subheader("Generated XML")
    st.code(st.session_state.generated_xml, language='xml')

    # Copy to clipboard functionality
    if st.button("Copy to Clipboard", key="copy_xml_button", help="Click to copy the XML to your clipboard"):
        st.components.v1.html(
            f"""
            <script>
                navigator.clipboard.writeText(`{st.session_state.generated_xml}`).then(function() {{
                    alert('XML copied to clipboard!');
                }}, function(err) {{
                    alert('Could not copy XML: ', err);
                }});
            </script>
            """,
            height=0
        )
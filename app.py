# app.py
import streamlit as st
import datetime
import uuid
import random
import requests
from xml_generator import generate_pain001_xml, generate_pacs008_xml, is_iban_country

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
    .mandatory-field {
        background-color: #fef3c7 !important;
        border: 2px solid #f59e0b !important;
    }
    .error-message {
        color: #dc2626;
        background-color: #fef2f2;
        padding: 0.75rem;
        border-radius: 0.375rem;
        border: 1px solid #fecaca;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .fx-info-box {
        background-color: #f0f9ff;
        border: 1px solid #7dd3fc;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .fx-rate-display {
        background-color: #ecfdf5;
        border: 1px solid #6ee7b7;
        border-radius: 0.375rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>ISO 20022 XML Payment Generator</h1>", unsafe_allow_html=True)

# Add user instruction
st.info(
    "💡 **Tip**: After entering values in text fields, press Enter or click outside the field to save your input before generating XML.")


# Function to get current datetime in required format (+HH:MM offset)
def get_current_datetime_with_offset():
    now = datetime.datetime.now(datetime.timezone.utc)
    # Format to YYYY-MM-DDTHH:MM:SS+00:00 for UTC, which is common for SWIFT CBPR+
    return now.strftime('%Y-%m-%dT%H:%M:%S+00:00')


def get_exchange_rate(from_currency, to_currency):
    """
    Fetch current exchange rate from a free API service.
    Returns rate and timestamp, or None if failed.
    """
    if from_currency == to_currency:
        return 1.0, datetime.datetime.now()

    try:
        # Using exchangerate-api.com (free tier allows 1500 requests/month)
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if to_currency in data['rates']:
                rate = data['rates'][to_currency]
                timestamp = datetime.datetime.now()
                return rate, timestamp
    except Exception as e:
        st.warning(f"Could not fetch live exchange rate: {e}")

    # Fallback to mock rates if API fails
    mock_rates = {
        ('USD', 'EUR'): 0.92,
        ('EUR', 'USD'): 1.08,
        ('USD', 'GBP'): 0.79,
        ('GBP', 'USD'): 1.27,
        ('EUR', 'GBP'): 0.85,
        ('GBP', 'EUR'): 1.18,
        ('USD', 'JPY'): 150.25,
        ('JPY', 'USD'): 0.0067,
        ('EUR', 'JPY'): 163.04,
        ('JPY', 'EUR'): 0.0061
    }

    rate = mock_rates.get((from_currency, to_currency))
    if rate:
        return rate, datetime.datetime.now()

    # If no rate found, try inverse
    inverse_rate = mock_rates.get((to_currency, from_currency))
    if inverse_rate:
        return 1 / inverse_rate, datetime.datetime.now()

    return None, None


def needs_exchange_rate(payment_type, origin, settlement_ccy, instructed_ccy):
    """
    Determine if exchange rate is needed based on the payment scenario.
    Returns True if FX conversion is required.
    """
    if settlement_ccy == instructed_ccy:
        return False

    # Based on the PDF logic
    if payment_type == 'fedwire_intl':
        return settlement_ccy != instructed_ccy
    elif payment_type == 'swift':
        return settlement_ccy != instructed_ccy

    return False


def calculate_settlement_amount(instructed_amount, settlement_ccy, instructed_ccy, exchange_rate=None):
    """
    Calculate settlement amount based on currencies and exchange rate.
    """
    if settlement_ccy == instructed_ccy:
        return instructed_amount

    if exchange_rate:
        # Settlement amount = Instructed amount * exchange rate
        return round(instructed_amount * exchange_rate, 2)

    return instructed_amount


# Function to validate USABA agent fields
def validate_usaba_fields(data, channel_type, fedwire_type):
    """
    Validates that when USABA Member IDs are used, corresponding name and address fields are provided.
    Also validates country codes are 2 characters.
    Returns list of error messages.
    """
    errors = []

    if channel_type == 'fedwire':
        # Check Debtor Agent
        if data.get('dbtrAgtMmbId', '').strip():
            if not data.get('dbtrAgtNm', '').strip():
                errors.append("Debtor Agent Name is mandatory when USABA Member ID is provided")
            if not data.get('dbtrAgtStrtNm', '').strip():
                errors.append("Debtor Agent Street Name is mandatory when USABA Member ID is provided")
            if not data.get('dbtrAgtTwnNm', '').strip():
                errors.append("Debtor Agent Town Name is mandatory when USABA Member ID is provided")
            if not data.get('dbtrAgtCtry', '').strip():
                errors.append("Debtor Agent Country is mandatory when USABA Member ID is provided")
            elif len(data.get('dbtrAgtCtry', '').strip()) != 2:
                errors.append("Debtor Agent Country must be exactly 2 characters (ISO country code)")

        # Validate country code length even if not mandatory
        if data.get('dbtrAgtCtry', '').strip() and len(data.get('dbtrAgtCtry', '').strip()) != 2:
            errors.append("Debtor Agent Country must be exactly 2 characters (ISO country code)")

        # Check Creditor Agent for domestic payments or when USABA is used for international
        if fedwire_type == 'domestic':
            if data.get('cdtrAgtMmbId', '').strip():
                if not data.get('cdtrAgtNm', '').strip():
                    errors.append("Creditor Agent Name is mandatory when USABA Member ID is provided")
                if not data.get('cdtrAgtStrtNm', '').strip():
                    errors.append("Creditor Agent Street Name is mandatory when USABA Member ID is provided")
                if not data.get('cdtrAgtTwnNm', '').strip():
                    errors.append("Creditor Agent Town Name is mandatory when USABA Member ID is provided")
                if not data.get('cdtrAgtCtry', '').strip():
                    errors.append("Creditor Agent Country is mandatory when USABA Member ID is provided")
                elif len(data.get('cdtrAgtCtry', '').strip()) != 2:
                    errors.append("Creditor Agent Country must be exactly 2 characters (ISO country code)")

        # Validate creditor agent country code length even if not mandatory
        if data.get('cdtrAgtCtry', '').strip() and len(data.get('cdtrAgtCtry', '').strip()) != 2:
            errors.append("Creditor Agent Country must be exactly 2 characters (ISO country code)")

    return errors


def get_account_field_help(channel_type, fedwire_type, country_code, sender_country='US'):
    """
    Generate help text for account fields based on the payment scheme rules.
    """
    if channel_type == 'fedwire':
        if fedwire_type == 'domestic':
            return "Enter US account number (IBAN not used for Fedwire domestic)"
        elif fedwire_type == 'international':
            if is_iban_country(country_code):
                return "Enter IBAN (required for IBAN countries in Fedwire international)"
            else:
                return "Enter local account number (IBAN not available for this country)"
    elif channel_type == 'swift':
        if is_iban_country(country_code):
            return "Enter IBAN (required for IBAN countries in SWIFT CBPR+)"
        else:
            return "Enter local account number (IBAN not available for this country)"

    return "Enter account number or IBAN"


def get_account_field_label(channel_type, fedwire_type, country_code, account_type='Debtor'):
    """
    Generate appropriate label for account fields.
    """
    base_label = f"{account_type} Account"

    if channel_type == 'fedwire':
        if fedwire_type == 'domestic':
            return f"{base_label} Number"
        elif fedwire_type == 'international':
            if is_iban_country(country_code):
                return f"{base_label} IBAN"
            else:
                return f"{base_label} Number"
    elif channel_type == 'swift':
        if is_iban_country(country_code):
            return f"{base_label} IBAN"
        else:
            return f"{base_label} Number"

    return f"{base_label} (IBAN/Number)"


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
            'cdtrAcctIBAN': 'GB33BUKB20201555555555',
            'instdAmt': 100.00,
            'ustrdRmtInf': 'Payment for services rendered - Invoice ABC123',
            'currency': 'EUR'
        },
        'pacs008': {
            'msgId': '',
            'creDtTm': get_current_datetime_with_offset(),
            'intrBkSttlmDt': (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
            'sttlmMtd': 'CLRG',
            'instgAgtBICFI': 'INSTGB2LXXX',
            'instdAgtBICFI': 'CDTRGB2LXXX',
            'instgAgtMmbId': '011104238',
            'instdAgtMmbId': '021040078',
            'txId': f"TX{uuid.uuid4().hex[:14].upper()}",
            'dbtrNm': 'Debtor Name',
            'dbtrStrtNm': 'Debtor Street',
            'dbtrBldgNb': '123',
            'dbtrPstCd': '12345',
            'dbtrTwnNm': 'Debtor City',
            'dbtrCtry': 'US',
            'dbtrAcctIBAN': '123456789012',
            'dbtrAgtBICFI_tx': 'DBTRUS33XXX',
            'cdtrAgtBICFI_tx': 'CDTRGB2LXXX',
            'dbtrAgtMmbId': '011104238',
            'cdtrAgtMmbId': '021040078',
            'dbtrAgtNm': '',
            'dbtrAgtStrtNm': '',
            'dbtrAgtBldgNb': '',
            'dbtrAgtPstCd': '',
            'dbtrAgtTwnNm': '',
            'dbtrAgtCtry': '',
            'cdtrAgtNm': '',
            'cdtrAgtStrtNm': '',
            'cdtrAgtBldgNb': '',
            'cdtrAgtPstCd': '',
            'cdtrAgtTwnNm': '',
            'cdtrAgtCtry': '',
            'cdtrNm': 'Creditor Name',
            'cdtrStrtNm': 'Creditor Street',
            'cdtrBldgNb': '456',
            'cdtrPstCd': 'SW1A0AA',
            'cdtrTwnNm': 'London',
            'cdtrCtry': 'GB',
            'cdtrAcctIBAN': 'GB33BUKB20201555555555',
            'instdAmt': 100.00,
            'intrBkSttlmAmt': 100.00,
            'ustrdRmtInf': 'Invoice 67890',
            'primaryCurrency': 'USD',
            'secondaryCurrency': 'USD',
            'exchangeRate': None,
            'exchangeRateTimestamp': None
        }
    }
if 'generated_xml' not in st.session_state:
    st.session_state.generated_xml = ""
if 'message_type' not in st.session_state:
    st.session_state.message_type = 'pacs008'

st.session_state.message_type = st.radio(
    "Select ISO 20022 Message Type:",
    ('pacs008', 'pain001'),
    key="message_type_selector",
    horizontal=True
)

if st.session_state.message_type == 'pain001':
    st.subheader("pain.001 - Customer Credit Transfer Initiation")

    st.markdown("### Group Header")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.form_data['pain001']['msgId'] = st.text_input("Message ID (MsgId)",
                                                                       value=st.session_state.form_data['pain001'][
                                                                           'msgId'], key="pain001_msgId")
        st.session_state.form_data['pain001']['initgPtyNm'] = st.text_input("Initiating Party Name (InitgPty.Nm)",
                                                                            value=st.session_state.form_data['pain001'][
                                                                                'initgPtyNm'], key="pain001_initgPtyNm")
    with col2:
        st.session_state.form_data['pain001']['creDtTm'] = st.text_input("Creation Date Time (CreDtTm)",
                                                                         value=st.session_state.form_data['pain001'][
                                                                             'creDtTm'], key="pain001_creDtTm")
        st.session_state.form_data['pain001']['btchBookg'] = st.checkbox("Batch Booking (BtchBookg)",
                                                                         value=st.session_state.form_data['pain001'][
                                                                             'btchBookg'], key="pain001_btchBookg")

    st.markdown("### Payment Information")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.form_data['pain001']['pmtInfId'] = st.text_input("Payment Information ID (PmtInfId)",
                                                                          value=st.session_state.form_data['pain001'][
                                                                              'pmtInfId'], key="pain001_pmtInfId")
        st.session_state.form_data['pain001']['pmtMtd'] = st.selectbox("Payment Method (PmtMtd)", ['TRF'], index=0,
                                                                       key="pain001_pmtMtd")
    with col2:
        st.session_state.form_data['pain001']['reqdExctnDt'] = st.text_input("Requested Execution Date (ReqdExctnDt)",
                                                                             value=
                                                                             st.session_state.form_data['pain001'][
                                                                                 'reqdExctnDt'],
                                                                             key="pain001_reqdExctnDt")
        st.session_state.form_data['pain001']['currency'] = st.text_input(
            "Currency (e.g., EUR, USD)",
            value=st.session_state.form_data['pain001']['currency'],
            key="pain001_currency",
            help="Use valid ISO 4217 currency codes, e.g., USD for US Dollars, EUR for Euro"
        )

    # SEPA uses IBAN - no change needed for pain001
    st.markdown("### Debtor Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.form_data['pain001']['dbtrNm'] = st.text_input("Debtor Name (Dbtr.Nm)",
                                                                        value=st.session_state.form_data['pain001'][
                                                                            'dbtrNm'], key="pain001_dbtrNm")
        st.session_state.form_data['pain001']['dbtrStrtNm'] = st.text_input("Debtor Street (Dbtr.PstlAdr.StrtNm)",
                                                                            value=st.session_state.form_data['pain001'][
                                                                                'dbtrStrtNm'], key="pain001_dbtrStrtNm")
        st.session_state.form_data['pain001']['dbtrBldgNb'] = st.text_input(
            "Debtor Building Number (Dbtr.PstlAdr.BldgNb)", value=st.session_state.form_data['pain001']['dbtrBldgNb'],
            key="pain001_dbtrBldgNb")
    with col2:
        st.session_state.form_data['pain001']['dbtrPstCd'] = st.text_input("Debtor Post Code (Dbtr.PstlAdr.PstCd)",
                                                                           value=st.session_state.form_data['pain001'][
                                                                               'dbtrPstCd'], key="pain001_dbtrPstCd")
        st.session_state.form_data['pain001']['dbtrTwnNm'] = st.text_input("Debtor Town Name (Dbtr.PstlAdr.TwnNm)",
                                                                           value=st.session_state.form_data['pain001'][
                                                                               'dbtrTwnNm'], key="pain001_dbtrTwnNm")
        st.session_state.form_data['pain001']['dbtrCtry'] = st.text_input("Debtor Country (Dbtr.PstlAdr.Ctry)",
                                                                          value=st.session_state.form_data['pain001'][
                                                                              'dbtrCtry'], key="pain001_dbtrCtry",
                                                                          max_chars=2,
                                                                          help="Use 2-letter ISO country codes (e.g., US, GB, DE)")
    with col3:
        st.session_state.form_data['pain001']['dbtrAcctIBAN'] = st.text_input("Debtor Account IBAN (DbtrAcct.Id.IBAN)",
                                                                              value=
                                                                              st.session_state.form_data['pain001'][
                                                                                  'dbtrAcctIBAN'],
                                                                              key="pain001_dbtrAcctIBAN",
                                                                              help="IBAN is mandatory for SEPA pain.001 messages")
        st.session_state.form_data['pain001']['dbtrAgtBICFI'] = st.text_input(
            "Debtor Agent BICFI (DbtrAgt.FinInstnId.BICFI)",
            value=st.session_state.form_data['pain001']['dbtrAgtBICFI'], key="pain001_dbtrAgtBICFI")

    st.markdown("### Creditor Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.form_data['pain001']['cdtrNm'] = st.text_input("Creditor Name (Cdtr.Nm)",
                                                                        value=st.session_state.form_data['pain001'][
                                                                            'cdtrNm'], key="pain001_cdtrNm")
        st.session_state.form_data['pain001']['cdtrStrtNm'] = st.text_input("Creditor Street (Cdtr.PstlAdr.StrtNm)",
                                                                            value=st.session_state.form_data['pain001'][
                                                                                'cdtrStrtNm'], key="pain001_cdtrStrtNm")
        st.session_state.form_data['pain001']['cdtrBldgNb'] = st.text_input(
            "Creditor Building Number (Cdtr.PstlAdr.BldgNb)", value=st.session_state.form_data['pain001']['cdtrBldgNb'],
            key="pain001_cdtrBldgNb")
    with col2:
        st.session_state.form_data['pain001']['cdtrPstCd'] = st.text_input("Creditor Post Code (Cdtr.PstlAdr.PstCd)",
                                                                           value=st.session_state.form_data['pain001'][
                                                                               'cdtrPstCd'], key="pain001_cdtrPstCd")
        st.session_state.form_data['pain001']['cdtrTwnNm'] = st.text_input("Creditor Town Name (Cdtr.PstlAdr.TwnNm)",
                                                                           value=st.session_state.form_data['pain001'][
                                                                               'cdtrTwnNm'], key="pain001_cdtrTwnNm")
    with col3:
        st.session_state.form_data['pain001']['cdtrCtry'] = st.text_input("Creditor Country (Cdtr.PstlAdr.Ctry)",
                                                                          value=st.session_state.form_data['pain001'][
                                                                              'cdtrCtry'], key="pain001_cdtrCtry",
                                                                          max_chars=2,
                                                                          help="Use 2-letter ISO country codes (e.g., US, GB, DE)")
        st.session_state.form_data['pain001']['cdtrAcctIBAN'] = st.text_input(
            "Creditor Account IBAN (CdtrAcct.Id.IBAN)", value=st.session_state.form_data['pain001']['cdtrAcctIBAN'],
            key="pain001_cdtrAcctIBAN",
            help="IBAN is mandatory for SEPA pain.001 messages")
        st.session_state.form_data['pain001']['cdtrAgtBICFI'] = st.text_input(
            "Creditor Agent BICFI (CdtrAgt.FinInstnId.BICFI)",
            value=st.session_state.form_data['pain001']['cdtrAgtBICFI'], key="pain001_cdtrAgtBICFI")

    st.markdown("### Transaction Details")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.form_data['pain001']['instdAmt'] = st.number_input("Instructed Amount (InstdAmt)", value=float(
            st.session_state.form_data['pain001']['instdAmt']), min_value=0.01, step=0.01, format="%.2f",
                                                                            key="pain001_instdAmt")
    with col2:
        st.session_state.form_data['pain001']['ustrdRmtInf'] = st.text_area(
            "Unstructured Remittance Info (RmtInf.Ustrd)", st.session_state.form_data['pain001']['ustrdRmtInf'],
            key="pain001_ustrdRmtInf")

else:  # pacs008
    st.subheader("pacs.008 - FI to FI Customer Credit Transfer")

    pacs008_channel_type = st.radio(
        "Select pacs.008 Channel Type:",
        ('Fedwire', 'SWIFT'),
        key="pacs008_channel_type_selector",
        horizontal=True
    )
    pacs008_channel_type_lower = pacs008_channel_type.lower()

    if pacs008_channel_type_lower == 'fedwire':
        fedwire_type = st.radio(
            "Select Fedwire Payment Type:",
            ('Domestic', 'International'),
            key="fedwire_type_selector",
            horizontal=True
        ).lower()
    else:
        fedwire_type = None

    # Display account format rules info box
    if pacs008_channel_type_lower == 'fedwire':
        if fedwire_type == 'domestic':
            st.markdown(
                '<div class="info-box">📋 <strong>Account Format Rule:</strong> Fedwire Domestic (US ➔ US) uses <strong>account numbers</strong>, not IBANs. Bank identification via ABA routing numbers in Agent fields.</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="info-box">📋 <strong>Account Format Rule:</strong> Fedwire International uses <strong>IBAN for IBAN countries</strong>, account numbers for non-IBAN countries.</div>',
                unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="info-box">📋 <strong>Account Format Rule:</strong> SWIFT CBPR+ uses <strong>IBAN for IBAN countries</strong>, local account numbers for non-IBAN countries.</div>',
            unsafe_allow_html=True)

    # Currency and Exchange Rate Section
    st.markdown("### Currency & Exchange Rate Configuration")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.form_data['pacs008']['primaryCurrency'] = st.selectbox(
            "Primary Currency (Settlement)",
            ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF'],
            index=['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF'].index(
                st.session_state.form_data['pacs008'].get('primaryCurrency', 'USD')),
            key="pacs008_primaryCurrency",
            help="Currency used for interbank settlement (IntrBkSttlmAmt)"
        )
    with col2:
        st.session_state.form_data['pacs008']['secondaryCurrency'] = st.selectbox(
            "Secondary Currency (Instructed)",
            ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF'],
            index=['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF'].index(
                st.session_state.form_data['pacs008'].get('secondaryCurrency', 'USD')),
            key="pacs008_secondaryCurrency",
            help="Currency for the final payment to beneficiary (InstdAmt)"
        )

    # Check if exchange rate is needed
    primary_ccy = st.session_state.form_data['pacs008']['primaryCurrency']
    secondary_ccy = st.session_state.form_data['pacs008']['secondaryCurrency']

    payment_type = 'fedwire_intl' if pacs008_channel_type_lower == 'fedwire' and fedwire_type == 'international' else 'swift' if pacs008_channel_type_lower == 'swift' else 'fedwire_dom'
    fx_needed = needs_exchange_rate(payment_type, 'US', primary_ccy, secondary_ccy)

    if fx_needed:
        st.markdown(
            f'<div class="fx-info-box">💱 <strong>FX Conversion Required:</strong> {primary_ccy} ➔ {secondary_ccy}<br>'
            f'Settlement will be in {primary_ccy}, beneficiary receives {secondary_ccy}</div>',
            unsafe_allow_html=True)

        # Fetch exchange rate
        if st.button("🔄 Fetch Current Exchange Rate", key="fetch_fx_rate"):
            with st.spinner("Fetching exchange rate..."):
                rate, timestamp = get_exchange_rate(primary_ccy, secondary_ccy)
                if rate:
                    st.session_state.form_data['pacs008']['exchangeRate'] = rate
                    st.session_state.form_data['pacs008']['exchangeRateTimestamp'] = timestamp
                    st.success(f"Exchange rate updated: 1 {primary_ccy} = {rate:.6f} {secondary_ccy}")
                else:
                    st.error("Could not fetch exchange rate. Please enter manually.")

        # Display current rate if available
        current_rate = st.session_state.form_data['pacs008'].get('exchangeRate')
        if current_rate:
            rate_timestamp = st.session_state.form_data['pacs008'].get('exchangeRateTimestamp')
            timestamp_str = rate_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC') if rate_timestamp else 'Unknown'
            st.markdown(
                f'<div class="fx-rate-display">📊 Current Rate: 1 {primary_ccy} = {current_rate:.6f} {secondary_ccy}<br>'
                f'<small>Last updated: {timestamp_str}</small></div>',
                unsafe_allow_html=True)

        # Manual rate input
        manual_rate = st.number_input(
            f"Exchange Rate ({primary_ccy} to {secondary_ccy})",
            value=float(current_rate) if current_rate else 1.0,
            min_value=0.000001,
            step=0.000001,
            format="%.6f",
            key="pacs008_manual_exchange_rate",
            help="Enter the exchange rate manually if needed"
        )

        if manual_rate != current_rate:
            st.session_state.form_data['pacs008']['exchangeRate'] = manual_rate
            st.session_state.form_data['pacs008']['exchangeRateTimestamp'] = datetime.datetime.now()
    else:
        st.markdown(
            f'<div class="fx-info-box">✅ <strong>No FX Conversion:</strong> Both settlement and instruction in {primary_ccy}</div>',
            unsafe_allow_html=True)
        st.session_state.form_data['pacs008']['exchangeRate'] = None

    if pacs008_channel_type_lower == 'fedwire':
        sttlm_mtd_options = ['CLRG']
        if st.session_state.form_data['pacs008']['sttlmMtd'] != 'CLRG':
            st.session_state.form_data['pacs008']['sttlmMtd'] = 'CLRG'
        sttlm_mtd_index = 0
    else:  # SWIFT
        sttlm_mtd_options = ['INDA', 'INGA', 'COVE']
        if st.session_state.form_data['pacs008']['sttlmMtd'] == 'CLRG' or st.session_state.form_data['pacs008'][
            'sttlmMtd'] not in sttlm_mtd_options:
            st.session_state.form_data['pacs008']['sttlmMtd'] = 'INDA'
        sttlm_mtd_index = sttlm_mtd_options.index(st.session_state.form_data['pacs008']['sttlmMtd'])

    st.markdown("### Group Header")
    col1, col2 = st.columns(2)

    current_date = datetime.datetime.now().strftime('%Y%m%d')
    if pacs008_channel_type_lower == 'fedwire':
        unique_alpha = uuid.uuid4().hex[8:16].upper()
        sequence_digits = str(random.randint(0, 999999)).zfill(6)
        default_msg_id_pacs008 = f"{current_date}{unique_alpha}{sequence_digits}"
    else:  # SWIFT
        default_msg_id_pacs008 = f"{current_date}SWIFT{uuid.uuid4().hex[:10].upper()}"

    with col1:
        st.session_state.form_data['pacs008']['msgId'] = st.text_input(
            "Message ID (MsgId)",
            value=default_msg_id_pacs008,
            key="pacs008_msgId"
        )
        st.session_state.form_data['pacs008']['sttlmMtd'] = st.selectbox(
            "Settlement Method (SttlmMtd)",
            options=sttlm_mtd_options,
            index=sttlm_mtd_index,
            key="pacs008_sttlmMtd"
        )
    with col2:
        st.session_state.form_data['pacs008']['creDtTm'] = st.text_input("Creation Date Time (CreDtTm)",
                                                                         value=st.session_state.form_data['pacs008'][
                                                                             'creDtTm'], key="pacs008_creDtTm")
        st.session_state.form_data['pacs008']['intrBkSttlmDt'] = st.text_input(
            "Interbank Settlement Date (IntrBkSttlmDt)", value=st.session_state.form_data['pacs008']['intrBkSttlmDt'],
            key="pacs008_intrBkSttlmDt")

    col1, col2 = st.columns(2)
    with col1:
        if pacs008_channel_type_lower == 'swift':
            st.session_state.form_data['pacs008']['instgAgtBICFI'] = st.text_input("Instructing Agent BICFI", value=
            st.session_state.form_data['pacs008']['instgAgtBICFI'], key="pacs008_instgAgtBICFI")
        else:  # Fedwire
            st.session_state.form_data['pacs008']['instgAgtMmbId'] = st.text_input("Instructing Agent USABA (MmbId)",
                                                                                   value=st.session_state.form_data[
                                                                                       'pacs008']['instgAgtMmbId'],
                                                                                   key="pacs008_instgAgtMmbId")
    with col2:
        if pacs008_channel_type_lower == 'swift':
            st.session_state.form_data['pacs008']['instdAgtBICFI'] = st.text_input("Instructed Agent BICFI", value=
            st.session_state.form_data['pacs008']['instdAgtBICFI'], key="pacs008_instdAgtBICFI")
        else:  # Fedwire
            st.session_state.form_data['pacs008']['instdAgtMmbId'] = st.text_input("Instructed Agent USABA (MmbId)",
                                                                                   value=st.session_state.form_data[
                                                                                       'pacs008']['instdAgtMmbId'],
                                                                                   key="pacs008_instdAgtMmbId")

    st.markdown("### Transaction Information")
    st.session_state.form_data['pacs008']['txId'] = st.text_input(
        "Transaction ID (TxId)",
        value=st.session_state.form_data['pacs008']['txId'],
        help="Max 16 characters for SWIFT pacs.008",
        key="pacs008_txId"
    )

    st.markdown("### Debtor Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.form_data['pacs008']['dbtrNm'] = st.text_input("Debtor Name (Dbtr.Nm)",
                                                                        value=st.session_state.form_data['pacs008'][
                                                                            'dbtrNm'], key="pacs008_dbtrNm")
        st.session_state.form_data['pacs008']['dbtrStrtNm'] = st.text_input("Debtor Street (Dbtr.PstlAdr.StrtNm)",
                                                                            value=st.session_state.form_data['pacs008'][
                                                                                'dbtrStrtNm'], key="pacs008_dbtrStrtNm")
        st.session_state.form_data['pacs008']['dbtrBldgNb'] = st.text_input(
            "Debtor Building Number (Dbtr.PstlAdr.BldgNb)", value=st.session_state.form_data['pacs008']['dbtrBldgNb'],
            key="pacs008_dbtrBldgNb")
    with col2:
        st.session_state.form_data['pacs008']['dbtrPstCd'] = st.text_input("Debtor Post Code (Dbtr.PstlAdr.PstCd)",
                                                                           value=st.session_state.form_data['pacs008'][
                                                                               'dbtrPstCd'], key="pacs008_dbtrPstCd")
        st.session_state.form_data['pacs008']['dbtrTwnNm'] = st.text_input("Debtor Town Name (Dbtr.PstlAdr.TwnNm)",
                                                                           value=st.session_state.form_data['pacs008'][
                                                                               'dbtrTwnNm'], key="pacs008_dbtrTwnNm")
        st.session_state.form_data['pacs008']['dbtrCtry'] = st.text_input("Debtor Country (Dbtr.PstlAdr.Ctry)",
                                                                          value=st.session_state.form_data['pacs008'][
                                                                              'dbtrCtry'], key="pacs008_dbtrCtry",
                                                                          max_chars=2,
                                                                          help="Use 2-letter ISO country codes (e.g., US, GB, DE)")
    with col3:
        # Dynamic account field based on rules
        dbtr_country = st.session_state.form_data['pacs008'].get('dbtrCtry', 'US')
        dbtr_acct_label = get_account_field_label(pacs008_channel_type_lower, fedwire_type, dbtr_country, 'Debtor')
        dbtr_acct_help = get_account_field_help(pacs008_channel_type_lower, fedwire_type, dbtr_country)

        st.session_state.form_data['pacs008']['dbtrAcctIBAN'] = st.text_input(
            dbtr_acct_label,
            value=st.session_state.form_data['pacs008']['dbtrAcctIBAN'],
            key="pacs008_dbtrAcctIBAN",
            help=dbtr_acct_help
        )

        # Dynamic input fields for Debtor Agent
        st.markdown("#### Debtor Agent")
        if pacs008_channel_type_lower == 'fedwire':
            st.session_state.form_data['pacs008']['dbtrAgtMmbId'] = st.text_input("USABA Member ID", value=
            st.session_state.form_data['pacs008']['dbtrAgtMmbId'], key="pacs008_dbtrAgtMmbId",
                                                                                  help="When USABA Member ID is provided, Name and Address fields become mandatory")
        else:  # SWIFT
            st.session_state.form_data['pacs008']['dbtrAgtBICFI_tx'] = st.text_input("BICFI", value=
            st.session_state.form_data['pacs008']['dbtrAgtBICFI_tx'], key="pacs008_dbtrAgtBICFI_tx")

        # Check if USABA fields should be mandatory
        dbtr_usaba_mandatory = pacs008_channel_type_lower == 'fedwire' and st.session_state.form_data['pacs008'].get(
            'dbtrAgtMmbId', '').strip()

        name_help = "* Mandatory when USABA Member ID is provided" if dbtr_usaba_mandatory else ""
        st.session_state.form_data['pacs008']['dbtrAgtNm'] = st.text_input(
            f"Name {'*' if dbtr_usaba_mandatory else ''}",
            value=st.session_state.form_data['pacs008']['dbtrAgtNm'],
            key="pacs008_dbtrAgtNm",
            help=name_help
        )
        st.session_state.form_data['pacs008']['dbtrAgtStrtNm'] = st.text_input(
            f"Street Name {'*' if dbtr_usaba_mandatory else ''}",
            value=st.session_state.form_data['pacs008']['dbtrAgtStrtNm'],
            key="pacs008_dbtrAgtStrtNm",
            help=name_help
        )
        st.session_state.form_data['pacs008']['dbtrAgtBldgNb'] = st.text_input("Building Number", value=
        st.session_state.form_data['pacs008']['dbtrAgtBldgNb'], key="pacs008_dbtrAgtBldgNb")
        st.session_state.form_data['pacs008']['dbtrAgtPstCd'] = st.text_input("Post Code", value=
        st.session_state.form_data['pacs008']['dbtrAgtPstCd'], key="pacs008_dbtrAgtPstCd")
        st.session_state.form_data['pacs008']['dbtrAgtTwnNm'] = st.text_input(
            f"Town Name {'*' if dbtr_usaba_mandatory else ''}",
            value=st.session_state.form_data['pacs008']['dbtrAgtTwnNm'],
            key="pacs008_dbtrAgtTwnNm",
            help=name_help
        )
        st.session_state.form_data['pacs008']['dbtrAgtCtry'] = st.text_input(
            f"Country {'*' if dbtr_usaba_mandatory else ''}",
            value=st.session_state.form_data['pacs008']['dbtrAgtCtry'],
            key="pacs008_dbtrAgtCtry",
            help=f"{name_help} Use 2-letter ISO country codes (e.g., US, GB, DE)",
            max_chars=2
        )

    st.markdown("### Creditor Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.form_data['pacs008']['cdtrNm'] = st.text_input("Creditor Name (Cdtr.Nm)",
                                                                        value=st.session_state.form_data['pacs008'][
                                                                            'cdtrNm'], key="pacs008_cdtrNm")
        st.session_state.form_data['pacs008']['cdtrStrtNm'] = st.text_input("Creditor Street (Cdtr.PstlAdr.StrtNm)",
                                                                            value=st.session_state.form_data['pacs008'][
                                                                                'cdtrStrtNm'], key="pacs008_cdtrStrtNm")
        st.session_state.form_data['pacs008']['cdtrBldgNb'] = st.text_input(
            "Creditor Building Number (Cdtr.PstlAdr.BldgNb)", value=st.session_state.form_data['pacs008']['cdtrBldgNb'],
            key="pacs008_cdtrBldgNb")
    with col2:
        st.session_state.form_data['pacs008']['cdtrPstCd'] = st.text_input("Creditor Post Code (Cdtr.PstlAdr.PstCd)",
                                                                           value=st.session_state.form_data['pacs008'][
                                                                               'cdtrPstCd'], key="pacs008_cdtrPstCd")
        st.session_state.form_data['pacs008']['cdtrTwnNm'] = st.text_input("Creditor Town Name (Cdtr.PstlAdr.TwnNm)",
                                                                           value=st.session_state.form_data['pacs008'][
                                                                               'cdtrTwnNm'], key="pacs008_cdtrTwnNm")
    with col3:
        st.session_state.form_data['pacs008']['cdtrCtry'] = st.text_input("Creditor Country (Cdtr.PstlAdr.Ctry)",
                                                                          value=st.session_state.form_data['pacs008'][
                                                                              'cdtrCtry'], key="pacs008_cdtrCtry",
                                                                          max_chars=2,
                                                                          help="Use 2-letter ISO country codes (e.g., US, GB, DE)")

        # Dynamic account field for creditor based on rules
        cdtr_country = st.session_state.form_data['pacs008'].get('cdtrCtry', 'GB')
        cdtr_acct_label = get_account_field_label(pacs008_channel_type_lower, fedwire_type, cdtr_country, 'Creditor')
        cdtr_acct_help = get_account_field_help(pacs008_channel_type_lower, fedwire_type, cdtr_country)

        st.session_state.form_data['pacs008']['cdtrAcctIBAN'] = st.text_input(
            cdtr_acct_label,
            value=st.session_state.form_data['pacs008']['cdtrAcctIBAN'],
            key="pacs008_cdtrAcctIBAN",
            help=cdtr_acct_help
        )

        # Dynamic input fields for Creditor Agent
        st.markdown("#### Creditor Agent")
        if pacs008_channel_type_lower == 'fedwire' and fedwire_type == 'domestic':
            st.session_state.form_data['pacs008']['cdtrAgtMmbId'] = st.text_input("USABA Member ID *", value=
            st.session_state.form_data['pacs008']['cdtrAgtMmbId'], key="pacs008_cdtrAgtMmbId",
                                                                                  help="When USABA Member ID is provided, Name and Address fields become mandatory")
        elif pacs008_channel_type_lower == 'fedwire' and fedwire_type == 'international':
            st.session_state.form_data['pacs008']['cdtrAgtBICFI_tx'] = st.text_input("BICFI", value=
            st.session_state.form_data['pacs008']['cdtrAgtBICFI_tx'], key="pacs008_cdtrAgtBICFI_tx")
        else:  # SWIFT
            st.session_state.form_data['pacs008']['cdtrAgtBICFI_tx'] = st.text_input("BICFI", value=
            st.session_state.form_data['pacs008']['cdtrAgtBICFI_tx'], key="pacs008_cdtrAgtBICFI_tx")

        # Check if USABA fields should be mandatory for creditor agent
        cdtr_usaba_mandatory = (pacs008_channel_type_lower == 'fedwire' and
                                fedwire_type == 'domestic' and
                                st.session_state.form_data['pacs008'].get('cdtrAgtMmbId', '').strip())

        cdtr_name_help = "* Mandatory when USABA Member ID is provided" if cdtr_usaba_mandatory else ""

        st.session_state.form_data['pacs008']['cdtrAgtNm'] = st.text_input(
            f"Name {'*' if cdtr_usaba_mandatory else ''}",
            value=st.session_state.form_data['pacs008']['cdtrAgtNm'],
            key="pacs008_cdtrAgtNm",
            help=cdtr_name_help
        )
        st.session_state.form_data['pacs008']['cdtrAgtStrtNm'] = st.text_input(
            f"Street Name {'*' if cdtr_usaba_mandatory else ''}",
            value=st.session_state.form_data['pacs008']['cdtrAgtStrtNm'],
            key="pacs008_cdtrAgtStrtNm",
            help=cdtr_name_help
        )
        st.session_state.form_data['pacs008']['cdtrAgtBldgNb'] = st.text_input("Building Number", value=
        st.session_state.form_data['pacs008']['cdtrAgtBldgNb'], key="pacs008_cdtrAgtBldgNb")
        st.session_state.form_data['pacs008']['cdtrAgtPstCd'] = st.text_input("Post Code", value=
        st.session_state.form_data['pacs008']['cdtrAgtPstCd'], key="pacs008_cdtrAgtPstCd")
        st.session_state.form_data['pacs008']['cdtrAgtTwnNm'] = st.text_input(
            f"Town Name {'*' if cdtr_usaba_mandatory else ''}",
            value=st.session_state.form_data['pacs008']['cdtrAgtTwnNm'],
            key="pacs008_cdtrAgtTwnNm",
            help=cdtr_name_help
        )
        st.session_state.form_data['pacs008']['cdtrAgtCtry'] = st.text_input(
            f"Country {'*' if cdtr_usaba_mandatory else ''}",
            value=st.session_state.form_data['pacs008']['cdtrAgtCtry'],
            key="pacs008_cdtrAgtCtry",
            help=f"{cdtr_name_help} Use 2-letter ISO country codes (e.g., US, GB, DE)",
            max_chars=2
        )

    st.markdown("### Transaction Details")
    col1, col2 = st.columns(2)
    with col1:
        # Instructed Amount (what beneficiary receives)
        st.session_state.form_data['pacs008']['instdAmt'] = st.number_input(
            f"Instructed Amount (InstdAmt) - {secondary_ccy}",
            value=float(st.session_state.form_data['pacs008']['instdAmt']),
            min_value=0.01,
            step=0.01,
            format="%.2f",
            key="pacs008_instdAmt",
            help=f"Amount the beneficiary will receive in {secondary_ccy}"
        )

        # Calculate settlement amount
        current_exchange_rate = st.session_state.form_data['pacs008'].get('exchangeRate')
        settlement_amount = st.session_state.form_data['pacs008']['instdAmt']

        if fx_needed and current_exchange_rate:
            # For FX conversion: settlement amount = instructed amount / exchange rate
            settlement_amount = round(st.session_state.form_data['pacs008']['instdAmt'] / current_exchange_rate, 2)

        st.session_state.form_data['pacs008']['intrBkSttlmAmt'] = settlement_amount

        # Display settlement amount (read-only)
        st.number_input(
            f"Settlement Amount (IntrBkSttlmAmt) - {primary_ccy}",
            value=settlement_amount,
            disabled=True,
            format="%.2f",
            help=f"Interbank settlement amount in {primary_ccy} (calculated automatically)"
        )

    with col2:
        st.session_state.form_data['pacs008']['ustrdRmtInf'] = st.text_area("Unstructured Remittance Info",
                                                                            st.session_state.form_data['pacs008'][
                                                                                'ustrdRmtInf'],
                                                                            key="pacs008_ustrdRmtInf")

if st.button("Generate XML", key="generate_xml_button"):
    # Validate USABA fields if pacs008 and Fedwire
    validation_errors = []

    if st.session_state.message_type == 'pacs008' and pacs008_channel_type_lower == 'fedwire':
        validation_errors = validate_usaba_fields(st.session_state.form_data['pacs008'], pacs008_channel_type_lower,
                                                  fedwire_type)

    if validation_errors:
        # Display errors
        st.markdown("### ⚠️ Validation Errors")
        for error in validation_errors:
            st.markdown(f'<div class="error-message">{error}</div>', unsafe_allow_html=True)
    else:
        # Generate XML if no validation errors
        if st.session_state.message_type == 'pain001':
            st.session_state.generated_xml = generate_pain001_xml(st.session_state.form_data['pain001'])
        else:
            st.session_state.generated_xml = generate_pacs008_xml(st.session_state.form_data['pacs008'],
                                                                  pacs008_channel_type_lower, fedwire_type)

if st.session_state.generated_xml:
    st.markdown("---")
    st.subheader("Generated XML")
    st.code(st.session_state.generated_xml, language='xml')

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

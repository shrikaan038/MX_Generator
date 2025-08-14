# 🧾 ISO 20022 XML Payment Message Generator

A user-friendly Streamlit-based utility for generating **ISO 20022 XML messages** — specifically `pacs.008` and `pain.001` — compatible with **SWIFT CBPR+** and **Fedwire** standards.

Supports:
- `pacs.008.001.08` for **FI-to-FI Customer Credit Transfers**
  - Channel: SWIFT (CBPR+) or Fedwire
- `pain.001.001.09` for **Customer Credit Transfer Initiation**

---

## 🚀 Features

- Generate ISO 20022 XML messages with dynamic form inputs
- Supports both **SWIFT** (with AppHdr) and **Fedwire** formats
- View and copy generated XML directly from the web UI
- Streamlit-powered interface (easy to use, no coding required)

---

## 📁 Folder Structure
├── app.py # Main Streamlit UI application
├── xml_generator.py # Logic for XML message creation
├── .gitignore # Ignores IDE/cache/env files
├── README.md # Project overview and usage
└── requirements.txt # Required packages (optional)

## ⚙️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/iso20022-generator.git
   cd iso20022-generator
Set up a virtual environment (optional but recommended):

python -m venv venv

venv/bin/activate  


### Install dependencies:

pip install streamlit

##  How to Use
🔌 Run the App

streamlit run app.py

## Use in Browser
The app will open in your default browser (usually http://localhost:8501).

### Steps
Choose message type: pacs.008 or pain.001

For pacs.008, choose either:

SWIFT — adds mandatory AppHdr

Fedwire — skips AppHdr, uses ABA routing (USABA)

Fill in form details:

Parties, account IBANs, BIC codes

Amounts, remittance info, settlement method

Click "Generate XML"

Copy or download your generated XML from the output section

## Output Example
The XML message includes:

Proper namespaces and schema locations

Optional AppHdr block (for SWIFT only)

Interbank settlement data, remittance details, and party info

## Validation
You can validate the generated XML:

With ISO 20022 XSD files (via xmllint or IDEs)

Or via SWIFT MyStandards https://www.swift.com/mystandards

## License
This project is open-source and provided under the MIT License.

## Support
Feel free to open an Issue or contribute improvements via Pull Requests!

## improvements
Add Initiating Party, Ultimate creditor and debtor                                                        
Pacs008 Incoming

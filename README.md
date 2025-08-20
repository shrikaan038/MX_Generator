# 🧾 ISO 20022 XML Payment Message Generator

A user-friendly **Streamlit** application for generating **ISO 20022 XML payment messages** — specifically `pacs.008` and `pain.001` — compatible with **SWIFT CBPR+** and **Fedwire** standards.

Supports:

* `pacs.008.001.08` for **FI-to-FI Customer Credit Transfers**

  * Channels: **SWIFT (CBPR+)**, **Fedwire Domestic**, **Fedwire International**, **Fedwire US Tax Payment**
* `pain.001.001.09` for **Customer Credit Transfer Initiation (SEPA)**

---

## 🚀 Features

* Generate ISO 20022 XML messages with dynamic form inputs
* Supports **SWIFT (with AppHdr)** and **Fedwire** formats
* Handles **Domestic**, **International**, and **Tax Payment** scenarios for Fedwire
* Automated **exchange rate fetching & caching** (with fallback to cache)
* Validation rules for **USABA routing numbers** and **IRS tax payment fields**
* SEPA-compliant `pain.001` (IBAN mandatory)
* View and copy generated XML directly in the browser
* Built with **Streamlit** — no coding knowledge required

---

## 📁 Folder Structure

```
├── app.py             # Main Streamlit UI application
├── xml_generator.py   # Core logic for XML message creation
├── exchange_rate_cache.json  # Cached FX rates (auto-generated)
├── .gitignore         # Ignores IDE/cache/env files
├── README.md          # Project overview and usage
└── requirements.txt   # Required packages
```

---

## ⚙️ Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-repo/iso20022-generator.git
   cd iso20022-generator
   ```

2. **Set up a virtual environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\\Scripts\\activate   # On Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 How to Use

1. Run the app:

   ```bash
   streamlit run app.py
   ```

2. Open in browser (default: [http://localhost:8501](http://localhost:8501))

3. Select message type:

   * **pacs.008** (SWIFT / Fedwire Domestic / Fedwire International / US Tax Payment)
   * **pain.001** (SEPA)

4. Fill in form fields:

   * Parties, account IBANs / numbers, BIC codes / USABA routing numbers
   * Amounts, remittance info, settlement method
   * Tax details (for IRS payments)

5. Click **Generate XML**

6. Copy or download the generated XML from the output section

---

## 📜 Output Example

* Proper namespaces and schema locations
* Optional **AppHdr** block (for SWIFT pacs.008)
* Interbank settlement data
* Remittance details and structured tax payment info (if applicable)
* Ultimate Debtor/Creditor and Initiating Party fields supported

---

## ✅ Validation

You can validate the generated XML using:

* ISO 20022 XSD schemas (via `xmllint`, IDE plugins, or XML tools)
* [SWIFT MyStandards](https://www.swift.com/mystandards)

---

## 📌 Improvements

* Added **Initiating Party**, **Ultimate Debtor**, and **Ultimate Creditor** support
* Added **US Tax Payment** (Fedwire) support with structured remittance info
* Added **FX exchange rate fetching and caching**
* Enhanced **validation** for tax fields and USABA agent details

---

## 📄 License

This project is open-source and provided under the **MIT License**.

---

## 🤝 Contributing

Feel free to open an **Issue** or submit a **Pull Request** with improvements or bug fixes.

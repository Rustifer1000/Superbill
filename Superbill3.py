import streamlit as st
import datetime

# ==============================================================================
# SESSION STATE INITIALIZATION
# ------------------------------------------------------------------------------
# Patient information (default values are empty)
if 'patient_info' not in st.session_state:
    st.session_state['patient_info'] = {
        "name": "",
        "address": "",
        "city": "",
        "state": "",
        "zip": "",
        "telephone": "",
        "dob": None,
        "gender": ""
    }

# List of services. Each service is a dict with keys:
#   - "date": datetime.date object for the service date.
#   - "diagnosis": string entered by the user.
if 'services' not in st.session_state:
    st.session_state['services'] = []

# For editing an existing service entry.
if 'editing_index' not in st.session_state:
    st.session_state['editing_index'] = None
if 'edit_service' not in st.session_state:
    st.session_state['edit_service'] = None

# ==============================================================================
# PATIENT INFORMATION FORM
# ------------------------------------------------------------------------------
st.header("Patient Information")
with st.form("patient_info_form"):
    name = st.text_input("Patient Name", value=st.session_state['patient_info']["name"])
    address = st.text_input("Address", value=st.session_state['patient_info']["address"])
    city = st.text_input("City", value=st.session_state['patient_info']["city"])
    state_input = st.text_input("State", value=st.session_state['patient_info']["state"])
    zip_code = st.text_input("ZIP Code", value=st.session_state['patient_info']["zip"])
    telephone = st.text_input("Telephone", value=st.session_state['patient_info']["telephone"])
    # Use a default DOB if not previously set.
    default_dob = st.session_state['patient_info']["dob"] or datetime.date(2000, 1, 1)
    dob = st.date_input("Date of Birth", value=default_dob)
    gender = st.selectbox("Gender", options=["Male", "Female", "Other"], index=0)
    
    submit_patient = st.form_submit_button("Save Patient Info")
    if submit_patient:
        st.session_state['patient_info'] = {
            "name": name,
            "address": address,
            "city": city,
            "state": state_input,
            "zip": zip_code,
            "telephone": telephone,
            "dob": dob,
            "gender": gender
        }
        st.success("Patient information saved!")

# ==============================================================================
# SERVICE DATE & BILLING DETAILS FORM
# ------------------------------------------------------------------------------
st.header("Service Dates & Billing Details")
with st.form("add_service_form", clear_on_submit=True):
    new_date = st.date_input("Select a Date of Service", datetime.date.today(), key="new_date_input")
    new_diagnosis = st.text_input("Enter Diagnosis (ICD 10)", key="new_diagnosis_input")
    add_service_submitted = st.form_submit_button("Add Service Date")
    
    if add_service_submitted:
        # Check for duplicate dates.
        duplicate = any(service["date"] == new_date for service in st.session_state['services'])
        if duplicate:
            st.error("This date is already added. Please choose a different date.")
        else:
            st.session_state['services'].append({"date": new_date, "diagnosis": new_diagnosis})
            st.success(f"Added service on {new_date.strftime('%Y-%m-%d')}.")

# ==============================================================================
# DISPLAY THE LIST OF SERVICES WITH OPTIONS TO EDIT OR REMOVE
# ------------------------------------------------------------------------------
st.subheader("Entered Service Dates & Diagnosis")
if st.session_state['services']:
    for idx, service in enumerate(st.session_state['services']):
        col1, col2, col3, col4 = st.columns([2, 3, 1, 1])
        col1.write(service["date"].strftime("%Y-%m-%d"))
        col2.write(f"Diagnosis: {service['diagnosis']}")
        if col3.button("Edit", key=f"edit_{idx}"):
            st.session_state['editing_index'] = idx
            st.session_state['edit_service'] = service.copy()
        if col4.button("Remove", key=f"remove_{idx}"):
            st.session_state['services'].pop(idx)
            st.rerun()  # Refresh immediately.
else:
    st.write("No service dates added yet.")

# ==============================================================================
# EDIT SERVICE ENTRY FORM (if applicable)
# ------------------------------------------------------------------------------
if st.session_state['editing_index'] is not None:
    st.subheader("Edit Service Date & Diagnosis")
    edit_index = st.session_state['editing_index']
    
    with st.form("edit_service_form"):
        edited_date = st.date_input(
            "Edit Date of Service",
            st.session_state['edit_service']["date"],
            key="edit_date_input"
        )
        edited_diagnosis = st.text_input(
            "Edit Diagnosis (ICD 10)",
            value=st.session_state['edit_service']["diagnosis"],
            key="edit_diagnosis_input"
        )
        edit_service_submitted = st.form_submit_button("Update Service")
        cancel_edit = st.form_submit_button("Cancel")
        
        if edit_service_submitted:
            # If the date is changed, ensure it's not a duplicate.
            if edited_date != st.session_state['services'][edit_index]["date"]:
                duplicate = any(
                    i != edit_index and s["date"] == edited_date 
                    for i, s in enumerate(st.session_state['services'])
                )
                if duplicate:
                    st.error("This date is already in the list. Please choose a different date.")
                else:
                    st.session_state['services'][edit_index] = {"date": edited_date, "diagnosis": edited_diagnosis}
                    st.success("Service updated!")
                    st.session_state['editing_index'] = None
                    st.session_state['edit_service'] = None
                    st.rerun()
            else:
                # Date unchanged; update only diagnosis.
                st.session_state['services'][edit_index]["diagnosis"] = edited_diagnosis
                st.success("Service updated!")
                st.session_state['editing_index'] = None
                st.session_state['edit_service'] = None
                st.rerun()
        elif cancel_edit:
            st.session_state['editing_index'] = None
            st.session_state['edit_service'] = None
            st.success("Edit cancelled.")
            st.rerun()

# ==============================================================================
# GENERATE INVOICE DOCUMENT
# ------------------------------------------------------------------------------
st.header("Generate Invoice Document")
if st.button("Generate Invoice"):
    invoice_date = datetime.date.today().strftime("%Y-%m-%d")
    patient_info = st.session_state['patient_info']
    
    # Billing table constants.
    cpt_code = "90837"
    charges = 225
    table_rows = ""
    for service in st.session_state['services']:
        table_rows += f"| {cpt_code} | {service['diagnosis']} | ${charges} | {service['date'].strftime('%Y-%m-%d')} |\n"
    total_charges = charges * len(st.session_state['services'])
    
    invoice_document = f"""
R U S S E L L  C O L L I N S ,  P S Y . D.
LICENSED MARRIAGE AND FAMILY THERAPIST
License Number: # 40797

Address: 1187 COAST VILLAGE ROAD #1-361
City, State, ZIP: SANTA BARBARA, CA 93108
Phone: 805.969.6370
Email: RUSSELL@COLLINSMEDIATION.COM

Date of Invoice: {invoice_date}

I N V O I C E

PATIENT INFORMATION:
- Name: {patient_info['name']}
- Address: {patient_info['address']}
- City, State, ZIP: {patient_info['city']}, {patient_info['state']}, {patient_info['zip']}
- Telephone: {patient_info['telephone']}
- Date of Birth: {patient_info['dob'].strftime("%Y-%m-%d") if patient_info['dob'] else ""}
- Gender: {patient_info['gender']}

PROVIDER DETAILS:
- NPI: 1033105911
- License: LMFT 40797
- Tax ID: 472027409

Billing Table:
| CPT CODE   | DIAGNOSIS (ICD 10) | CHARGES    | DATE OF SERVICE |
|------------|--------------------|------------|-----------------|
{table_rows}
TOTAL CHARGES: ${total_charges}
"""
    st.code(invoice_document, language="text")


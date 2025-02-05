import streamlit as st
import datetime

# ------------------------------------------------------------------------------
# Initialize session state variables if they don't already exist.
# - 'dates' will store our list of service dates.
# - 'editing_index' holds the index of the date currently being edited (if any).
# - 'edit_date' temporarily holds the value during an edit.
# ------------------------------------------------------------------------------
if 'dates' not in st.session_state:
    st.session_state['dates'] = []
if 'editing_index' not in st.session_state:
    st.session_state['editing_index'] = None
if 'edit_date' not in st.session_state:
    st.session_state['edit_date'] = None

# ------------------------------------------------------------------------------
# Title and instructions (this section is analogous to a header in a document)
# ------------------------------------------------------------------------------
st.title("Service Dates Input")
st.write("Enter the dates of service for your invoice below. This information "
         "can later be dynamically inserted into your Superbill/Invoice.")

# ------------------------------------------------------------------------------
# Form: Add a New Date of Service
# ------------------------------------------------------------------------------
with st.form("add_date_form", clear_on_submit=True):
    # The date input widget defaults to today's date.
    new_date = st.date_input("Select a Date of Service", datetime.date.today(), key="new_date_input")
    
    # The submit button for the form
    add_submitted = st.form_submit_button("Add Date")
    
    if add_submitted:
        # Validate: Prevent duplicate dates
        if new_date in st.session_state['dates']:
            st.error("This date is already added. Please choose a different date.")
        else:
            st.session_state['dates'].append(new_date)
            st.success(f"Added date: {new_date.strftime('%Y-%m-%d')}")

# ------------------------------------------------------------------------------
# Display the List of Entered Dates with Options to Edit or Remove
# ------------------------------------------------------------------------------
st.subheader("Entered Dates")
if st.session_state['dates']:
    # Loop through the dates list and create a row for each date
    for idx, date_val in enumerate(st.session_state['dates']):
        # Use columns to align the date text with action buttons.
        col1, col2, col3 = st.columns([2, 1, 1])
        col1.write(date_val.strftime("%Y-%m-%d"))
        # When "Edit" is clicked, set the editing index and initialize the edit date.
        if col2.button("Edit", key=f"edit_{idx}"):
            st.session_state['editing_index'] = idx
            st.session_state['edit_date'] = date_val
        # "Remove" button to delete the date from the list.
        if col3.button("Remove", key=f"remove_{idx}"):
            st.session_state['dates'].pop(idx)
            st.experimental_rerun()  # Rerun to immediately reflect changes.
else:
    st.write("No dates added yet.")

# ------------------------------------------------------------------------------
# If a date is being edited, display an Edit Form.
# ------------------------------------------------------------------------------
if st.session_state['editing_index'] is not None:
    st.subheader("Edit Date")
    edit_index = st.session_state['editing_index']
    
    with st.form("edit_date_form"):
        # Display a date input initialized with the date to be edited.
        edited_date = st.date_input("Edit Date", st.session_state['edit_date'], key="edit_date_input")
        edit_submitted = st.form_submit_button("Update Date")
        cancel_edit = st.form_submit_button("Cancel")
        
        if edit_submitted:
            # Validate: Ensure the edited date is not a duplicate (unless unchanged).
            if edited_date in st.session_state['dates'] and edited_date != st.session_state['dates'][edit_index]:
                st.error("This date is already in the list. Please choose a different date.")
            else:
                st.session_state['dates'][edit_index] = edited_date
                st.success(f"Updated date to: {edited_date.strftime('%Y-%m-%d')}")
                # Reset the editing state
                st.session_state['editing_index'] = None
                st.session_state['edit_date'] = None
                st.experimental_rerun()
        elif cancel_edit:
            # If editing is canceled, reset the editing state.
            st.session_state['editing_index'] = None
            st.session_state['edit_date'] = None
            st.success("Edit cancelled.")
            st.rerun()

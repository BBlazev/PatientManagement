import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from PIL import Image, ImageTk
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tembo import Patient, Base, Doctor, Appointment, Prescription

host = "gruesomely-playful-boxer.data-1.use1.tembo.io"
port = "5432"
username = "postgres"
password = "TTKYYqrKYk8dZZCC"
dbname = "app"
connection_string = f'postgresql://{username}:{password}@{host}:{port}/{dbname}'
engine = create_engine(connection_string)

Session = sessionmaker(bind=engine)
session = Session()

#---------------------------------------GUI------------------------------------------#

root = tk.Tk()
root.title("Medical Management System")
root.resizable(False,False)
root.geometry("600x550")
root.configure(bg="#f7f7f7")

def upload_patient_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        messagebox.showinfo("Image Selected", f"Selected image: {os.path.basename(file_path)}")
        return file_path  
    return None


def export_to_csv(data):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
    if file_path:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Patient Name', 'Appointment Type', 'Appointment Date',
                             'Doctor (Appointment)', 'Prescription', 'Prescription Date', 'Image Link'])
            for row in data:
                patient_name = row[0]
                appointment_type = row[1] or 'N/A'
                appointment_date = row[2].strftime('%Y-%m-%d') if row[2] else 'N/A'
                doctor_name_appointment = row[3] or 'N/A'
                prescription_name = row[4] or 'N/A'
                prescription_date = row[5].strftime('%Y-%m-%d') if row[5] else 'N/A'
                image_path = row[6] if row[6] else 'No Image'

                writer.writerow([patient_name, appointment_type, appointment_date,
                                 doctor_name_appointment, prescription_name, prescription_date, image_path])

        messagebox.showinfo("Export Successful", "Data exported successfully to CSV.")


def fetch_patient_data():
    query = session.query(
        Patient.name,
        Appointment.type,
        Appointment.date,
        Doctor.name,
        Prescription.medication_name,
        Prescription.prescription_date,
        Patient.image_path
    ).join(Appointment, Patient.id == Appointment.patient_id, isouter=True)\
     .join(Doctor, Doctor.id == Appointment.doctor_id, isouter=True)\
     .join(Prescription, Patient.id == Prescription.patient_id, isouter=True)\
     .all()
    return query
def parse_date(date_str):
    try:
        #
        return datetime.strptime(date_str, '%d.%m.%Y').date()
    except ValueError:
        messagebox.showerror("Invalid Date", "Please enter the date in DD.MM.YYYY format.")
        return None


def save_patient(name, medical_history, image_path=None):
    if not name or not medical_history:
        messagebox.showerror("Error", "Name and Medical History are required!")
        return None

    new_patient = Patient(name=name, medical_history=medical_history, image_path=image_path)
    session.add(new_patient)
    session.commit()
    patient_id = new_patient.id
    print(f"Patient saved with ID: {patient_id}")
    return patient_id
def save_doctor(name,specialty,contact):
    if not name or not specialty:
        print("All fields are required!")
        return None
    new_doctor = Doctor(name=name,specialty=specialty,contact_info=contact)
    session.add(new_doctor)
    session.commit()
    doctor_id = new_doctor.id
    return doctor_id

def get_doctors():
    return [doctor.name for doctor in session.query(Doctor).all()]
def get_patient():
    return [patient.name for patient in session.query(Patient).all()]
def get_prescription():
    return [f"{p.patient.name if p.patient else None} - {p.medication_name}" for p in session.query(Prescription).all()]
def get_appointment():
    return [f"{a.patient.name if a.patient else None} - {a.type}" for a in session.query(Appointment).all()]

#------------------------------DELETE---------------------------------------#
def update_dropdowns():
    patient_dropdown['values'] = get_patient()
    doctor_dropdown['values'] = get_doctors()
    prescription_dropdown['values'] = get_prescription()
    appointment_dropdown['values'] = get_appointment()
def delete_selected_patient(patient_name):
    patient = session.query(Patient).filter_by(name=patient_name).first()
    if patient:
        session.delete(patient)
        session.commit()
        messagebox.showinfo("Success", f"Patient '{patient_name}' and all related records have been deleted.")
        update_dropdowns()

def delete_selected_doctor(doctor_name):
    doctor = session.query(Doctor).filter_by(name=doctor_name).first()
    if doctor:
        session.delete(doctor)
        session.commit()
        messagebox.showinfo("Success", f"Doctor '{doctor_name}' and all related records have been deleted.")
        update_dropdowns()

def delete_selected_prescription(prescription_name):
    patient_name, medication_name = prescription_name.split(" - ")
    prescription = session.query(Prescription).join(Patient).filter(
        Prescription.medication_name == medication_name,
        Patient.name == patient_name
    ).first()
    if prescription:
        session.delete(prescription)
        session.commit()
        messagebox.showinfo("Success", f"Prescription '{medication_name}' for '{patient_name}' has been deleted.")
        update_dropdowns()

def delete_selected_appointment(appointment_name):
    patient_name, appointment_type = appointment_name.split(" - ")
    appointment = session.query(Appointment).join(Patient).filter(
        Appointment.type == appointment_type,
        Patient.name == patient_name
    ).first()
    if appointment:
        session.delete(appointment)
        session.commit()
        messagebox.showinfo("Success", f"Appointment '{appointment_type}' for '{patient_name}' has been deleted.")
        update_dropdowns()
def open_delete_form():
    delete_window = tk.Toplevel(root)
    delete_window.resizable(False,False)
    delete_window.title("Delete Records")
    delete_window.geometry("400x650")
    delete_window.configure(bg="#f7f7f7")

    tk.Label(delete_window, text="Delete Patient", font=("Arial", 14), bg="#f7f7f7").pack(pady=10)
    global patient_dropdown
    patient_dropdown = ttk.Combobox(delete_window, values=get_patient(), state="readonly")
    patient_dropdown.pack(pady=5)
    tk.Button(delete_window, text="Delete Patient", command=lambda: delete_selected_patient(patient_dropdown.get())).pack(pady=10)

    tk.Label(delete_window, text="Delete Doctor", font=("Arial", 14), bg="#f7f7f7").pack(pady=10)
    global doctor_dropdown
    doctor_dropdown = ttk.Combobox(delete_window, values=get_doctors(), state="readonly")
    doctor_dropdown.pack(pady=5)
    tk.Button(delete_window, text="Delete Doctor", command=lambda: delete_selected_doctor(doctor_dropdown.get())).pack(pady=10)

    tk.Label(delete_window, text="Delete Prescription", font=("Arial", 14), bg="#f7f7f7").pack(pady=10)
    global prescription_dropdown
    prescription_dropdown = ttk.Combobox(delete_window, values=get_prescription(), state="readonly")
    prescription_dropdown.pack(pady=5)
    tk.Button(delete_window, text="Delete Prescription", command=lambda: delete_selected_prescription(prescription_dropdown.get())).pack(pady=10)

    tk.Label(delete_window, text="Delete Appointment", font=("Arial", 14), bg="#f7f7f7").pack(pady=10)
    global appointment_dropdown
    appointment_dropdown = ttk.Combobox(delete_window, values=get_appointment(), state="readonly")
    appointment_dropdown.pack(pady=5)
    tk.Button(delete_window, text="Delete Appointment", command=lambda: delete_selected_appointment(appointment_dropdown.get())).pack(pady=10)

    # Back button
    tk.Button(delete_window, text="Back to Dashboard", command=delete_window.destroy).pack(pady=20)


def add_appointment(appointment_type, doctor, date_str, notes, patient_id):
    selected_doctor = session.query(Doctor).filter_by(name=doctor).first()
    appointment_date = parse_date(date_str)

    if appointment_date is None:
        return

    new_appointment = Appointment(type=appointment_type, patient_id=patient_id,
                                  doctor_id=selected_doctor.id, date=appointment_date,
                                  notes=notes)
    session.add(new_appointment)
    session.commit()
    print("Appointment added to the database")


def add_prescription(medication_name, dosage, doctor, date_str, notes, patient_id):
    selected_doctor = session.query(Doctor).filter_by(name=doctor).first()
    prescription_date = parse_date(date_str)

    if prescription_date is None:
        return

    new_prescription = Prescription(medication_name=medication_name, dosage=dosage,
                                    doctor_id=selected_doctor.id, prescription_date=prescription_date,
                                    notes=notes, patient_id=patient_id)
    session.add(new_prescription)
    session.commit()
    print("Prescription added to the database")

def delete_all_data():
    session.query(Appointment).delete()
    session.query(Prescription).delete()

    session.query(Patient).delete()
    session.query(Doctor).delete()

    session.commit()
    print("All patients, doctors, appointments, and prescriptions have been deleted.")

#---------------------------------------------GUI FORMS---------------------------------------------------------------#

def open_delete_confirmation():
    confirmation_window = tk.Toplevel(root)
    confirmation_window.title("Confirm Deletion")
    confirmation_window.geometry("300x150")
    confirmation_window.configure(bg="#f2dede")
    label = tk.Label(confirmation_window, text="Are you sure you want to delete all data?", font=("Arial", 12), bg="#f2dede")
    label.pack(pady=10)
    tk.Button(confirmation_window, text="Yes, Delete All", command=lambda: [delete_all_data(), confirmation_window.destroy()]).pack(pady=10)
    tk.Button(confirmation_window, text="No, Cancel", command=confirmation_window.destroy).pack(pady=10)


def open_patient_data_form():
    data_window = tk.Toplevel(root)
    data_window.title("Patient Data")
    data_window.geometry("900x400")

    tree = ttk.Treeview(data_window, columns=('Patient Name', 'Appointment Type', 'Appointment Date',
                                              'Doctor (Appointment)', 'Prescription', 'Prescription Date',
                                              'Image Path'), show='headings')

    tree.heading('Patient Name', text='Patient Name')
    tree.heading('Appointment Type', text='Appointment Type')
    tree.heading('Appointment Date', text='Appointment Date')
    tree.heading('Doctor (Appointment)', text='Doctor (Appointment)')
    tree.heading('Prescription', text='Prescription')
    tree.heading('Prescription Date', text='Prescription Date')
    tree.heading('Image Path', text='Image Path')

    # Define column widths
    tree.column('Patient Name', width=100)
    tree.column('Appointment Type', width=120)
    tree.column('Appointment Date', width=120)
    tree.column('Doctor (Appointment)', width=120)
    tree.column('Prescription', width=120)
    tree.column('Prescription Date', width=120)
    tree.column('Image Path', width=200)

    # Insert data into the table
    data = fetch_patient_data()
    for row in data:
        patient_name = row[0]
        appointment_type = row[1] or 'N/A'
        appointment_date = row[2].strftime('%Y-%m-%d') if row[2] else 'N/A'
        doctor_name_appointment = row[3] or 'N/A'
        prescription_name = row[4] or 'N/A'
        prescription_date = row[5].strftime('%Y-%m-%d') if row[5] else 'N/A'
        image_path = row[6] or 'No Image'

        tree.insert('', tk.END, values=(patient_name, appointment_type, appointment_date,
                                        doctor_name_appointment, prescription_name, prescription_date, image_path))

    tree.pack(fill='both', expand=True)
    tk.Button(data_window, text="Export to CSV", command=lambda: export_to_csv(data)).pack(pady=10)

    tk.Button(data_window, text="Back to Dashboard", command=data_window.destroy).pack(pady=10)

def open_patient_form():
    patient_window = tk.Toplevel(root)
    patient_window.title("Manage Patient")
    patient_window.geometry("600x400")

    patient_id = None
    selected_image_path = None

    tk.Label(patient_window, text="Patient Information", font=("Arial", 14)).pack(pady=10)

    tk.Label(patient_window, text="Name:").pack(pady=5)
    entry_name = tk.Entry(patient_window)
    entry_name.pack(pady=5)

    tk.Label(patient_window, text="Medical History:").pack(pady=5)
    entry_medical_history = tk.Entry(patient_window)
    entry_medical_history.pack(pady=5)

    def handle_upload_image():
        nonlocal selected_image_path
        selected_image_path = upload_patient_image()
        if selected_image_path:
            image_label.config(text=f"Image Selected: {os.path.basename(selected_image_path)}")
        else:
            image_label.config(text="No Image Selected")

    upload_button = tk.Button(patient_window, text="Upload Image", command=handle_upload_image)
    upload_button.pack(pady=10)

    image_label = tk.Label(patient_window, text="No Image Selected")
    image_label.pack(pady=5)

    def handle_save_patient():
        nonlocal patient_id
        patient_id = save_patient(entry_name.get(), entry_medical_history.get(), selected_image_path)
        if patient_id:
            print(f"Patient saved with ID {patient_id}")

    tk.Button(patient_window, text="Save Patient", command=handle_save_patient).pack(pady=10)

    tk.Button(patient_window, text="Back to Dashboard", command=patient_window.destroy).pack(pady=20)

def open_doctor_form():
    doctor_window = tk.Toplevel(root)
    doctor_window.title("Manage Doctors")
    doctor_window.geometry("400x300")

    tk.Label(doctor_window, text="Doctor Management", font=("Arial", 14)).pack(pady=10)
    tk.Label(doctor_window, text="Name:").pack(pady=5)
    entry_doctor_name = tk.Entry(doctor_window)
    entry_doctor_name.pack(pady=5)

    tk.Label(doctor_window, text="Specialty:").pack(pady=5)
    entry_doctor_specialty = tk.Entry(doctor_window)
    entry_doctor_specialty.pack(pady=5)

    tk.Label(doctor_window, text="Contact Info:").pack(pady=5)
    entry_doctor_contact_info = tk.Entry(doctor_window)
    entry_doctor_contact_info.pack(pady=5)

    def handle_save_doctor():
        save_doctor(entry_doctor_name.get(), entry_doctor_specialty.get(), entry_doctor_contact_info.get())

    tk.Button(doctor_window, text="Save Doctor", command=handle_save_doctor).pack(pady=10)
    tk.Button(doctor_window, text="Back to Dashboard", command=doctor_window.destroy).pack(pady=20)

def open_add_form():
    add_form_window = tk.Toplevel(root)
    add_form_window.title("Add Appointment/Prescription for Existing Patient")
    add_form_window.geometry("600x1000")

    image_path = None

    tk.Label(add_form_window, text="Select Patient:", font=("Arial", 14)).pack(pady=10)
    patient_combobox = ttk.Combobox(add_form_window, values=get_patient(), state="readonly")
    patient_combobox.pack(pady=5)

    tk.Label(add_form_window, text="Add Appointment", font=("Arial", 14)).pack(pady=10)

    tk.Label(add_form_window, text="Appointment Type:").pack(pady=5)
    entry_appointment_type = tk.Entry(add_form_window)
    entry_appointment_type.pack(pady=5)

    tk.Label(add_form_window, text="Select Doctor:").pack(pady=5)
    doctor_combobox = ttk.Combobox(add_form_window, values=get_doctors(), state="readonly")
    doctor_combobox.pack(pady=5)

    tk.Label(add_form_window, text="Appointment Date:").pack(pady=5)
    entry_appointment_date = tk.Entry(add_form_window)
    entry_appointment_date.pack(pady=5)

    tk.Label(add_form_window, text="Notes:").pack(pady=5)
    entry_appointment_notes = tk.Entry(add_form_window)
    entry_appointment_notes.pack(pady=5)

    def handle_add_appointment():
        selected_patient_name = patient_combobox.get()
        selected_patient = session.query(Patient).filter_by(name=selected_patient_name).first()
        add_appointment(entry_appointment_type.get(),
                        doctor_combobox.get(),
                        entry_appointment_date.get(),
                        entry_appointment_notes.get(),
                        selected_patient.id)

    tk.Button(add_form_window, text="Add Appointment", command=handle_add_appointment).pack(pady=10)

    # Divider Line
    tk.Label(add_form_window, text="-" * 50).pack(pady=10)

    # Prescription Section
    tk.Label(add_form_window, text="Add Prescription", font=("Arial", 14)).pack(pady=10)

    tk.Label(add_form_window, text="Medication Name:").pack(pady=5)
    entry_medication_name = tk.Entry(add_form_window)
    entry_medication_name.pack(pady=5)

    tk.Label(add_form_window, text="Dosage:").pack(pady=5)
    entry_dosage = tk.Entry(add_form_window)
    entry_dosage.pack(pady=5)

    tk.Label(add_form_window, text="Select Doctor:").pack(pady=5)
    doctor_combobox_prescription = ttk.Combobox(add_form_window, values=get_doctors(), state="readonly")
    doctor_combobox_prescription.pack(pady=5)

    tk.Label(add_form_window, text="Prescription Date:").pack(pady=5)
    entry_prescription_date = tk.Entry(add_form_window)
    entry_prescription_date.pack(pady=5)

    tk.Label(add_form_window, text="Notes:").pack(pady=5)
    entry_prescription_notes = tk.Entry(add_form_window)
    entry_prescription_notes.pack(pady=5)

    # Button to add the prescription
    def handle_add_prescription():
        selected_patient_name = patient_combobox.get()
        selected_patient = session.query(Patient).filter_by(name=selected_patient_name).first()
        add_prescription(entry_medication_name.get(),
                         entry_dosage.get(),
                         doctor_combobox_prescription.get(),
                         entry_prescription_date.get(),
                         entry_prescription_notes.get(),
                         selected_patient.id)

    tk.Button(add_form_window, text="Add Prescription", command=handle_add_prescription).pack(pady=10)

    def handle_upload_picture():
        nonlocal image_path
        image_path = upload_patient_image()

    upload_button = tk.Button(add_form_window, text="Upload Picture", command=handle_upload_picture)
    upload_button.pack(pady=10)

    tk.Button(add_form_window, text="Back to Dashboard", command=add_form_window.destroy).pack(pady=20)


def open_image_viewer():
    image_viewer_window = tk.Toplevel(root)
    image_viewer_window.title("View Patient Images")
    image_viewer_window.geometry("600x600")

    patients = session.query(Patient).all()

    tk.Label(image_viewer_window, text="Select Patient:").pack(pady=5)
    patient_combobox = ttk.Combobox(image_viewer_window, values=[patient.name for patient in patients])
    patient_combobox.pack(pady=5)

    image_label = tk.Label(image_viewer_window)
    image_label.pack(pady=10)

    medical_history_label = tk.Label(image_viewer_window, text="Medical History: ")
    medical_history_label.pack()

    medical_history_text = tk.Text(image_viewer_window, height=10,width=30, wrap="word")
    medical_history_text.pack()
    medical_history_text.config(state= tk.DISABLED)
    def show_patient_image():
        selected_patient_name = patient_combobox.get()
        if selected_patient_name:
            selected_patient = session.query(Patient).filter_by(name=selected_patient_name).first()
            if selected_patient and selected_patient.image_path and os.path.exists(selected_patient.image_path):
                img = Image.open(selected_patient.image_path)
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                img = ImageTk.PhotoImage(img)
                image_label.config(image=img)
                image_label.image = img
            else:
                image_label.config(text="No image found for this patient")

            if selected_patient and selected_patient.medical_history:
                medical_history_text.config(state=tk.NORMAL)
                medical_history_text.delete(1.0, tk.END)
                medical_history_text.insert(tk.END, selected_patient.medical_history)
                medical_history_text.config(state=tk.DISABLED)
            else:
                medical_history_text.config(state=tk.NORMAL)
                medical_history_text.delete(1.0, tk.END)
                medical_history_text.insert(tk.END, "No medical history available for this patient.")
                medical_history_text.config(state=tk.DISABLED)

    tk.Button(image_viewer_window, text="Show Image and Medical History", command=show_patient_image).pack(pady=10)

    tk.Button(image_viewer_window, text="Back to Dashboard", command=image_viewer_window.destroy).pack(pady=20)



def get_patient_count():
    return session.query(Patient).count()
def get_doctor_count():
    return  session.query(Doctor).count()
def get_appointment_count():
    return session.query(Appointment).count()

#------------------------------------MAIN DASHBOARD STUFF-------------------------------------------------------#

dashboard_frame = ttk.Frame(root)
dashboard_frame.pack(pady=10, padx=10, fill='both')

title_label = ttk.Label(root, text="Welcome to the Medical Management System", font=("Arial", 16))
title_label.pack(pady=10)

stats_frame = ttk.Frame(root)
stats_frame.pack(pady=10)

patient_count_label = ttk.Label(stats_frame, text=f"Total Patients: {session.query(Patient).count()}")
patient_count_label.grid(row=0, column=0, padx=20, pady=5)

doctor_count_label = ttk.Label(stats_frame, text=f"Total Doctors: {session.query(Doctor).count()}")
doctor_count_label.grid(row=0, column=1, padx=20, pady=5)

appointment_count_label = ttk.Label(stats_frame, text=f"Upcoming Appointments: {session.query(Appointment).count()}")
appointment_count_label.grid(row=0, column=2, padx=20, pady=5)

button_frame = ttk.Frame(root)
button_frame.pack(pady=20)

manage_patients_button = tk.Button(button_frame, text="Manage Patients", width=20, command=open_patient_form)
manage_patients_button.grid(row=0, column=0, padx=10, pady=10)

manage_doctors_button = tk.Button(button_frame, text="Manage Doctors", width=20, command=open_doctor_form)
manage_doctors_button.grid(row=0, column=1, padx=10, pady=10)

view_patient_data_button = tk.Button(root, text="View Patient Data", width=20, command=open_patient_data_form)
view_patient_data_button.pack(pady=10)

delete_data_button = tk.Button(root, text="Delete All Data", width=20, command=open_delete_confirmation)
delete_data_button.pack(pady=10)

delete_data_button = tk.Button(root, text="Delete Records", width=20, command=open_delete_form)
delete_data_button.pack(pady=10)

add_data_button = tk.Button(root, text="Add Appointment/Prescription", width=30, command=open_add_form)
add_data_button.pack(pady=10)

view_patient_images_button = tk.Button(root, text="View Patient Images", width=20, command=open_image_viewer)
view_patient_images_button.pack(pady=10)

root.mainloop()

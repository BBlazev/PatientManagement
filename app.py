import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from sqlalchemy import create_engine, or_, cast, String
from sqlalchemy.orm import sessionmaker
from tembo import (
    Base,
    Patient,
    Doctor,
    Appointment,
    Prescription,
)

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


APPOINTMENT_TYPES = [
    "GP - Opći tjelesni pregled",
    "KRV - Test krvi",
    "X-RAY - Rendgensko skeniranje",
    "CT - CT sken",
    "MR - MRI sken",
    "ULTRA - Ultrazvuk",
    "EKG - Elektrokardiogram",
    "ECHO - Ehokardiogram",
    "EYE - Pregled očiju",
    "DERM - Dermatološki pregled",
    "DENTA - Pregled zuba",
    "MAMMO - Mamografija",
    "NEURO - Neurološki pregled"
]


HOST = "gruesomely-playful-boxer.data-1.use1.tembo.io"
PORT = "5432"
USERNAME = "postgres"
PASSWORD = "TTKYYqrKYk8dZZCC"
DBNAME = "app"

connection_string = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
engine = create_engine(connection_string, echo=False)
Session = sessionmaker(bind=engine)
session = Session()



def fetch_all_patients():
    return session.query(Patient).all()

def fetch_patients_by_name(partial_name):
    return session.query(Patient).filter(
        Patient.name.ilike(f"%{partial_name}%")
    ).all()

def fetch_patients_by_oib(partial_oib):

    return session.query(Patient).filter(
        cast(Patient.OIB, String).ilike(f"%{partial_oib}%")
    ).all()

def fetch_appointments_for_patient(patient_id):
    return session.query(Appointment).filter_by(patient_id=patient_id).all()

def fetch_prescriptions_for_patient(patient_id):
    return session.query(Prescription).filter_by(patient_id=patient_id).all()




def build_patient_table(patients=None):

    if patients is None:
        patients = fetch_all_patients()


    for row in patient_table.get_children():
        patient_table.delete(row)

    for p in patients:
        appts = fetch_appointments_for_patient(p.id)
        appt_str = ", ".join([
            f"{a.type_of_appointment} @ {a.date or 'NoDate'}"
            for a in appts
        ]) if appts else "None"

        rx = fetch_prescriptions_for_patient(p.id)
        rx_str = ", ".join([r.medication_name for r in rx]) if rx else "None"

        med_hist_short = (
            p.medical_history[:50] + "..."
            if p.medical_history and len(p.medical_history) > 50
            else (p.medical_history or "No history")
        )

        def dt2str(d):
            return d.strftime("%Y-%m-%d") if d else ""

        patient_table.insert(
            "",
            tk.END,
            iid=p.id,
            values=(
                p.id,
                p.name or "",
                p.OIB or "",
                p.Sex or "",
                dt2str(p.Date_of_Birth),
                dt2str(p.Start_of_problems),
                dt2str(p.ENd_of_problems),
                med_hist_short,
                appt_str,
                rx_str
            )
        )

def refresh_table():
    build_patient_table(None)



def search_patients():
    search_term = entry_search.get().strip()
    search_by = combo_search_by.get()

    if not search_term:
        messagebox.showinfo("Info", "Please enter something to search.")
        return

    if search_by == "Name":
        matching = fetch_patients_by_name(search_term)
    elif search_by == "OIB":
        matching = fetch_patients_by_oib(search_term)
    else:
        matching = []

    build_patient_table(matching)

def clear_search():
    entry_search.delete(0, tk.END)
    combo_search_by.set("Name")
    refresh_table()




def open_add_patient_form():
    form = tk.Toplevel(root)
    form.title("Add New Patient")
    form.geometry("500x580")
    form.resizable(False, False)

    lf = ttk.LabelFrame(form, text="New Patient Details", padding=10)
    lf.pack(fill="both", expand=True, padx=10, pady=10)

    # Name
    ttk.Label(lf, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    entry_name = ttk.Entry(lf, width=30)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    # OIB
    ttk.Label(lf, text="OIB:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    entry_oib = ttk.Entry(lf, width=30)
    entry_oib.grid(row=1, column=1, padx=5, pady=5)

    # Sex
    ttk.Label(lf, text="Sex:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    combo_sex = ttk.Combobox(lf, values=["Male", "Female", "Other"], width=28, state="readonly")
    combo_sex.set("Male")
    combo_sex.grid(row=2, column=1, padx=5, pady=5)

    # Date of Birth
    ttk.Label(lf, text="Date of Birth (YYYY-MM-DD):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    entry_dob = ttk.Entry(lf, width=30)
    entry_dob.grid(row=3, column=1, padx=5, pady=5)

    # Start of Problems
    ttk.Label(lf, text="Start of Problems (YYYY-MM-DD):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
    entry_start = ttk.Entry(lf, width=30)
    entry_start.grid(row=4, column=1, padx=5, pady=5)

    # End of Problems
    ttk.Label(lf, text="End of Problems (YYYY-MM-DD):").grid(row=5, column=0, sticky="w", padx=5, pady=5)
    entry_end = ttk.Entry(lf, width=30)
    entry_end.grid(row=5, column=1, padx=5, pady=5)

    # Medical History
    ttk.Label(lf, text="Medical History:").grid(row=6, column=0, sticky="nw", padx=5, pady=5)
    txt_medhist = tk.Text(lf, width=30, height=3, wrap="word")
    txt_medhist.grid(row=6, column=1, padx=5, pady=5)

    # Image Path
    ttk.Label(lf, text="Image Path:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
    entry_imgpath = ttk.Entry(lf, width=30)
    entry_imgpath.grid(row=7, column=1, padx=5, pady=5)

    def browse_image():
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif"), ("All Files", "*.*")]
        )
        if path:
            entry_imgpath.delete(0, tk.END)
            entry_imgpath.insert(0, path)

    ttk.Button(lf, text="Browse...", command=browse_image).grid(row=7, column=2, padx=5)

    def submit_patient():
        oib_val = None
        if entry_oib.get().strip():
            try:
                oib_val = int(entry_oib.get().strip())
            except ValueError:
                messagebox.showerror("Invalid OIB", "OIB must be a numeric value.")
                return

        new_patient = Patient(
            name=entry_name.get().strip() or None,
            OIB=oib_val,
            Sex=combo_sex.get(),
            Date_of_Birth=entry_dob.get().strip() or None,
            Start_of_problems=entry_start.get().strip() or None,
            ENd_of_problems=entry_end.get().strip() or None,
            medical_history=txt_medhist.get("1.0", tk.END).strip() or "",
            image_path=entry_imgpath.get().strip() or None,
        )
        session.add(new_patient)
        session.commit()

        messagebox.showinfo("Success", "Patient added successfully!")
        form.destroy()
        refresh_table()

    ttk.Button(lf, text="Add Patient", command=submit_patient).grid(row=8, column=0, columnspan=2, pady=20)

def open_add_appointment_form():
    selected = patient_table.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a patient row first.")
        return

    patient_id = int(selected[0])
    patient = session.query(Patient).filter_by(id=patient_id).first()
    if not patient:
        messagebox.showerror("Error", "Selected patient not found in the database.")
        return

    form = tk.Toplevel(root)
    form.title(f"Add Appointment for {patient.name}")
    form.geometry("430x320")
    form.resizable(False, False)

    lf = ttk.LabelFrame(form, text="New Appointment", padding=10)
    lf.pack(fill="both", expand=True, padx=10, pady=10)

    ttk.Label(lf, text="Type of Appointment:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    combo_type = ttk.Combobox(lf, values=APPOINTMENT_TYPES, state="readonly", width=35)
    combo_type.set(APPOINTMENT_TYPES[0])
    combo_type.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(lf, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    entry_date = ttk.Entry(lf, width=37)
    entry_date.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(lf, text="Time (HH:MM):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    entry_time = ttk.Entry(lf, width=37)
    entry_time.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(lf, text="Notes (optional):").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
    txt_notes = tk.Text(lf, width=29, height=3)
    txt_notes.grid(row=3, column=1, padx=5, pady=5)

    def submit_appointment():
        selected_type = combo_type.get().strip()
        appt_date = entry_date.get().strip()
        appt_time = entry_time.get().strip()
        notes = txt_notes.get("1.0", tk.END).strip()

        new_appt = Appointment(
            patient_id=patient.id,
            type_of_appointment=selected_type,
            date=appt_date if appt_date else None,
            notes=f"{notes}\nTime: {appt_time}"
        )
        session.add(new_appt)
        session.commit()

        messagebox.showinfo("Success", "Appointment added successfully!")
        form.destroy()
        refresh_table()

    ttk.Button(lf, text="Add Appointment", command=submit_appointment).grid(
        row=4, column=0, columnspan=2, pady=15
    )

def open_add_prescription_form():
    selected = patient_table.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a patient row first.")
        return

    patient_id = int(selected[0])
    patient = session.query(Patient).filter_by(id=patient_id).first()
    if not patient:
        messagebox.showerror("Error", "Selected patient not found in the database.")
        return

    form = tk.Toplevel(root)
    form.title(f"Add Prescription for {patient.name}")
    form.geometry("430x390")
    form.resizable(False, False)

    lf = ttk.LabelFrame(form, text="New Prescription", padding=10)
    lf.pack(fill="both", expand=True, padx=10, pady=10)

    ttk.Label(lf, text="Medication Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    entry_med = ttk.Entry(lf, width=30)
    entry_med.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(lf, text="Dosage:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    entry_dosage = ttk.Entry(lf, width=30)
    entry_dosage.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(lf, text="Doctor Name (optional):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    entry_doctor = ttk.Entry(lf, width=30)
    entry_doctor.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(lf, text="Date (YYYY-MM-DD):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    entry_date = ttk.Entry(lf, width=30)
    entry_date.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(lf, text="Notes (optional):").grid(row=4, column=0, sticky="nw", padx=5, pady=5)
    txt_notes = tk.Text(lf, width=28, height=3)
    txt_notes.grid(row=4, column=1, padx=5, pady=5)

    def submit_prescription():
        med_name = entry_med.get().strip()
        dosage = entry_dosage.get().strip()
        doctor_name = entry_doctor.get().strip()
        rx_date = entry_date.get().strip()
        notes = txt_notes.get("1.0", tk.END).strip()

        doctor_obj = None
        if doctor_name:
            doctor_obj = session.query(Doctor).filter_by(name=doctor_name).first()
            if not doctor_obj:
                doctor_obj = Doctor(name=doctor_name, specialty="", contact_info="")
                session.add(doctor_obj)
                session.commit()

        new_rx = Prescription(
            patient_id=patient.id,
            doctor_id=doctor_obj.id if doctor_obj else None,
            medication_name=med_name or "N/A",
            dosage=dosage or "N/A",
            prescription_date=rx_date or None,
            notes=notes,
        )
        session.add(new_rx)
        session.commit()

        messagebox.showinfo("Success", "Prescription added successfully!")
        form.destroy()
        refresh_table()

    ttk.Button(lf, text="Add Prescription", command=submit_prescription).grid(
        row=5, column=0, columnspan=2, pady=15
    )




def export_all_to_pdf():

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf"), ("All Files", "*.*")]
    )
    if not file_path:
        return

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    x_margin = 50
    y_position = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x_margin, y_position, "All Patients Report")
    y_position -= 30

    patients = fetch_all_patients()

    c.setFont("Helvetica", 10)

    for p in patients:
        c.drawString(x_margin, y_position, f"Patient ID: {p.id}, Name: {p.name}, OIB: {p.OIB}, Sex: {p.Sex}")
        y_position -= 14

        c.drawString(x_margin, y_position, f"  DOB: {p.Date_of_Birth or 'N/A'},   Start: {p.Start_of_problems or 'N/A'},   End: {p.ENd_of_problems or 'N/A'}")
        y_position -= 14

        c.drawString(x_margin, y_position, f"  Medical History: {p.medical_history or 'None'}")
        y_position -= 14

        appts = fetch_appointments_for_patient(p.id)
        if appts:
            c.drawString(x_margin, y_position, "  Appointments:")
            y_position -= 14
            for a in appts:
                c.drawString(x_margin + 20, y_position, f"- {a.type_of_appointment} @ {a.date or 'NoDate'}, Notes: {a.notes or ''}")
                y_position -= 14
        else:
            c.drawString(x_margin, y_position, "  Appointments: None")
            y_position -= 14

        rx = fetch_prescriptions_for_patient(p.id)
        if rx:
            c.drawString(x_margin, y_position, "  Prescriptions:")
            y_position -= 14
            for r in rx:
                c.drawString(x_margin + 20, y_position, f"- {r.medication_name} ({r.dosage}), Date: {r.prescription_date or 'N/A'}")
                y_position -= 14
        else:
            c.drawString(x_margin, y_position, "  Prescriptions: None")
            y_position -= 14

        y_position -= 10


        if y_position < 100:
            c.showPage()
            y_position = height - 50
            c.setFont("Helvetica", 10)

    c.save()
    messagebox.showinfo("PDF Export", f"All patient data exported to:\n{os.path.basename(file_path)}")




root = tk.Tk()
root.title("Medical Management System")
root.geometry("1200x600")

style = ttk.Style(root)
style.theme_use("clam")
style.configure("TLabel", font=("Arial", 10))
style.configure("TButton", font=("Arial", 10))
style.configure("TEntry", font=("Arial", 10))

search_frame = ttk.Frame(root)
search_frame.pack(side=tk.TOP, fill="x", padx=10, pady=5)

lbl_search_by = ttk.Label(search_frame, text="Search by:")
lbl_search_by.pack(side=tk.LEFT, padx=(0, 5))

combo_search_by = ttk.Combobox(search_frame, values=["Name", "OIB"], state="readonly", width=10)
combo_search_by.set("Name")
combo_search_by.pack(side=tk.LEFT, padx=(0, 20))

entry_search = ttk.Entry(search_frame, width=20)
entry_search.pack(side=tk.LEFT, padx=(0, 10))

btn_do_search = ttk.Button(search_frame, text="Search", command=search_patients)
btn_do_search.pack(side=tk.LEFT)

btn_clear_search = ttk.Button(search_frame, text="Clear", command=clear_search)
btn_clear_search.pack(side=tk.LEFT, padx=(10, 0))

table_frame = ttk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=10)

table_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)

patient_table = ttk.Treeview(
    table_frame,
    columns=(
        "ID",
        "Name",
        "OIB",
        "Sex",
        "Date_of_Birth",
        "Start_of_problems",
        "End_of_problems",
        "Medical_History",
        "Appointments",
        "Prescriptions",
    ),
    show="headings",
    yscrollcommand=table_scrollbar.set
)
table_scrollbar.config(command=patient_table.yview)
table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
patient_table.pack(side=tk.LEFT, fill="both", expand=True)

patient_table.heading("ID", text="ID")
patient_table.heading("Name", text="Name")
patient_table.heading("OIB", text="OIB")
patient_table.heading("Sex", text="Sex")
patient_table.heading("Date_of_Birth", text="Birth Date")
patient_table.heading("Start_of_problems", text="Start of Problems")
patient_table.heading("End_of_problems", text="End of Problems")
patient_table.heading("Medical_History", text="Medical History")
patient_table.heading("Appointments", text="Appointments")
patient_table.heading("Prescriptions", text="Prescriptions")

patient_table.column("ID", width=40, anchor="center")
patient_table.column("Name", width=120)
patient_table.column("OIB", width=100)
patient_table.column("Sex", width=60, anchor="center")
patient_table.column("Date_of_Birth", width=100)
patient_table.column("Start_of_problems", width=100)
patient_table.column("End_of_problems", width=100)
patient_table.column("Medical_History", width=180)
patient_table.column("Appointments", width=200)
patient_table.column("Prescriptions", width=120)

build_patient_table()

buttons_frame = ttk.Frame(root)
buttons_frame.pack(pady=5)

btn_add_patient = ttk.Button(buttons_frame, text="Add Patient", command=open_add_patient_form)
btn_add_patient.grid(row=0, column=0, padx=10)

btn_add_appt = ttk.Button(buttons_frame, text="Add Appointment", command=open_add_appointment_form)
btn_add_appt.grid(row=0, column=1, padx=10)

btn_add_rx = ttk.Button(buttons_frame, text="Add Prescription", command=open_add_prescription_form)
btn_add_rx.grid(row=0, column=2, padx=10)

btn_refresh = ttk.Button(buttons_frame, text="Refresh Table", command=refresh_table)
btn_refresh.grid(row=0, column=3, padx=10)

btn_export_pdf = ttk.Button(buttons_frame, text="Export All to PDF", command=export_all_to_pdf)
btn_export_pdf.grid(row=0, column=4, padx=10)

root.mainloop()

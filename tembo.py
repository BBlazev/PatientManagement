import postgres
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import psycopg2

USER     = "postgres"
PASSWORD = "bartol3553"
HOST     = "aws-0-eu-west-3.pooler.supabase.com"
PORT     = 5432
DBNAME   = "postgres"

connection_string = (
    f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
)
engine = create_engine(connection_string, echo=False)

try:
    conn = engine.connect()
    print("Spojeno na Supabase PostgreSQL!")
    conn.close()
except Exception as e:
    print(" Ne mogu se spojiti:", e)
    raise

Base = declarative_base()

class Patient(Base):
    __tablename__ = "Patient"
    id = Column(Integer,primary_key = True)
    name = Column(String)
    medical_history = Column(String,  nullable=True)
    Start_of_problems = Column(Date)
    ENd_of_problems = Column(Date)
    image_path = Column(String)
    OIB = Column(sqlalchemy.BigInteger)
    Date_of_Birth = Column(Date)
    Sex = Column(String)

    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete")
    prescriptions = relationship("Prescription", back_populates="patient", cascade="all, delete")

class Doctor(Base):
    __tablename__ = "Doctor"
    id = Column(Integer, primary_key= True)
    name = Column(String)
    specialty = Column(String)
    contact_info = Column(String)
    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete")
    prescriptions = relationship("Prescription", back_populates="doctor", cascade="all, delete")

class Appointment(Base):
    __tablename__ = "Appointment"
    id = Column(Integer, primary_key=True)
    type_of_appointment = Column(String)
    patient_id = Column(Integer, ForeignKey('Patient.id'))
    doctor_id = Column(Integer, ForeignKey('Doctor.id'))
    date = Column(Date)
    notes = Column(String)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor",back_populates="appointments")
class Prescription(Base):
    __tablename__ = "Prescription"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('Patient.id'))
    doctor_id = Column(Integer, ForeignKey('Doctor.id'))
    medication_name = Column(String)
    dosage = Column(String)
    prescription_date = Column(Date)
    notes = Column(String)

    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("Doctor", back_populates="prescriptions")



print("Creating tables...")
#Base.metadata.drop_all(engine)

Base.metadata.create_all(engine)
print("Tables created successfully!")
Session = sessionmaker(bind=engine)
sessions = Session()

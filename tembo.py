import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import psycopg2

host = "gruesomely-playful-boxer.data-1.use1.tembo.io"
port = "5432"
username = "postgres"
password = "TTKYYqrKYk8dZZCC"
dbname = "postgres"

connection_string = f'postgresql://{username}:{password}@{host}:{port}/app'
engine = sqlalchemy.create_engine(connection_string)

try:
    connection = engine.connect()
    print("Connected successfully to Tembo PostgreSQL!")
    connection.close()
except Exception as e:
    print(f"Failed to connect: {e}")

Base = declarative_base()

class Patient(Base):
    __tablename__ = "Patient"
    id = Column(Integer,primary_key = True)
    name = Column(String)
    medical_history = Column(String,  nullable=True)
    image_path = Column(String)

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
    type = Column(String)
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

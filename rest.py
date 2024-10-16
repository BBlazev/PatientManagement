from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from tembo import Patient, Doctor, Appointment, Prescription, Base


host = "gruesomely-playful-boxer.data-1.use1.tembo.io"
port = "5432"
username = "postgres"
password = "TTKYYqrKYk8dZZCC"
dbname = "postgres"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@{host}:{port}/app'
db = SQLAlchemy()

db.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')

# Get all patients
@app.route('/patients', methods=['GET'])
def get_patients():
    patients = Patient.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'medical_history': p.medical_history, 'image_path': p.image_path} for p in patients])

# Add a new patient
@app.route('/patients', methods=['POST'])
def add_patient():
    data = request.json
    new_patient = Patient(name=data['name'], medical_history=data['medical_history'], image_path=data.get('image_path'))
    db.session.add(new_patient)
    db.session.commit()
    return jsonify({'message': 'Patient added successfully'}), 201

# Get all appointments
@app.route('/appointments', methods=['GET'])
def get_appointments():
    appointments = Appointment.query.all()
    return jsonify([{'id': a.id, 'type': a.type, 'date': a.date.strftime('%Y-%m-%d'), 'notes': a.notes} for a in appointments])

# Add a new appointment
@app.route('/appointments', methods=['POST'])
def add_appointment():
    data = request.json
    new_appointment = Appointment(type=data['type'], patient_id=data['patient_id'], doctor_id=data['doctor_id'], date=data['date'], notes=data['notes'])
    db.session.add(new_appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment added successfully'}), 201

# ---------------------------------- Run the Flask app ----------------------------------- #
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(debug=True)

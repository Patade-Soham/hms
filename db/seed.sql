USE hms;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE feedback;
TRUNCATE TABLE bills;
TRUNCATE TABLE prescriptions;
TRUNCATE TABLE medicines;
TRUNCATE TABLE admissions;
TRUNCATE TABLE rooms;
TRUNCATE TABLE appointments;
TRUNCATE TABLE doctors;
TRUNCATE TABLE departments;
TRUNCATE TABLE patients;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO users (user_id, name, email, password_hash, role, created_at) VALUES
(1, 'System Admin', 'admin@medicore.com', 'scrypt:32768:8:1$bNh0ZsTBlUzZxZfp$d9e3130d6d9149b2e3d4f29a9151f841cb29660de0acb55936cb12e6d1bc936fd4708dd0e21396ba0285fe7a4e587fa06aaca3c87d05a85e5af15e8c017394b0', 'admin', NOW()),
(2, 'Dr. Arjun Mehta', 'arjun.mehta@medicore.com', 'scrypt:32768:8:1$MA8LuN0IsaVLEe5z$6047929f54c6c8bd2f915da18c26d62b2542eaf8b3d14a0a2ae7caa3fee1980511e6fd055cd82895fd75eb460cc5c61637341b36d58e9f75fff3c4a1710fb78a', 'doctor', NOW()),
(3, 'Dr. Isha Verma', 'isha.verma@medicore.com', 'scrypt:32768:8:1$MA8LuN0IsaVLEe5z$6047929f54c6c8bd2f915da18c26d62b2542eaf8b3d14a0a2ae7caa3fee1980511e6fd055cd82895fd75eb460cc5c61637341b36d58e9f75fff3c4a1710fb78a', 'doctor', NOW()),
(4, 'Dr. Rahul Jain', 'rahul.jain@medicore.com', 'scrypt:32768:8:1$MA8LuN0IsaVLEe5z$6047929f54c6c8bd2f915da18c26d62b2542eaf8b3d14a0a2ae7caa3fee1980511e6fd055cd82895fd75eb460cc5c61637341b36d58e9f75fff3c4a1710fb78a', 'doctor', NOW()),
(5, 'Dr. Kavya Singh', 'kavya.singh@medicore.com', 'scrypt:32768:8:1$MA8LuN0IsaVLEe5z$6047929f54c6c8bd2f915da18c26d62b2542eaf8b3d14a0a2ae7caa3fee1980511e6fd055cd82895fd75eb460cc5c61637341b36d58e9f75fff3c4a1710fb78a', 'doctor', NOW()),
(6, 'Dr. Nikhil Rao', 'nikhil.rao@medicore.com', 'scrypt:32768:8:1$MA8LuN0IsaVLEe5z$6047929f54c6c8bd2f915da18c26d62b2542eaf8b3d14a0a2ae7caa3fee1980511e6fd055cd82895fd75eb460cc5c61637341b36d58e9f75fff3c4a1710fb78a', 'doctor', NOW()),
(7, 'Aarav Sharma', 'aarav.sharma@example.com', 'scrypt:32768:8:1$AwY5MwlZAFRDpqjJ$c807133c742f278791ab05bbe021db579ad85e47efcaf7135e31c99527a94e2b21bdfef061adaf7944e0e26427b633c35827af011868bf3669abcacb91786661', 'patient', NOW()),
(8, 'Meera Nair', 'meera.nair@example.com', 'scrypt:32768:8:1$AwY5MwlZAFRDpqjJ$c807133c742f278791ab05bbe021db579ad85e47efcaf7135e31c99527a94e2b21bdfef061adaf7944e0e26427b633c35827af011868bf3669abcacb91786661', 'patient', NOW()),
(9, 'Rohan Kapoor', 'rohan.kapoor@example.com', 'scrypt:32768:8:1$AwY5MwlZAFRDpqjJ$c807133c742f278791ab05bbe021db579ad85e47efcaf7135e31c99527a94e2b21bdfef061adaf7944e0e26427b633c35827af011868bf3669abcacb91786661', 'patient', NOW()),
(10, 'Ananya Das', 'ananya.das@example.com', 'scrypt:32768:8:1$AwY5MwlZAFRDpqjJ$c807133c742f278791ab05bbe021db579ad85e47efcaf7135e31c99527a94e2b21bdfef061adaf7944e0e26427b633c35827af011868bf3669abcacb91786661', 'patient', NOW()),
(11, 'Vikram Iyer', 'vikram.iyer@example.com', 'scrypt:32768:8:1$AwY5MwlZAFRDpqjJ$c807133c742f278791ab05bbe021db579ad85e47efcaf7135e31c99527a94e2b21bdfef061adaf7944e0e26427b633c35827af011868bf3669abcacb91786661', 'patient', NOW()),
(12, 'Neha Kulkarni', 'neha.kulkarni@example.com', 'scrypt:32768:8:1$AwY5MwlZAFRDpqjJ$c807133c742f278791ab05bbe021db579ad85e47efcaf7135e31c99527a94e2b21bdfef061adaf7944e0e26427b633c35827af011868bf3669abcacb91786661', 'patient', NOW()),
(13, 'Sahil Gupta', 'sahil.gupta@example.com', 'scrypt:32768:8:1$AwY5MwlZAFRDpqjJ$c807133c742f278791ab05bbe021db579ad85e47efcaf7135e31c99527a94e2b21bdfef061adaf7944e0e26427b633c35827af011868bf3669abcacb91786661', 'patient', NOW()),
(14, 'Priya Menon', 'priya.menon@example.com', 'scrypt:32768:8:1$AwY5MwlZAFRDpqjJ$c807133c742f278791ab05bbe021db579ad85e47efcaf7135e31c99527a94e2b21bdfef061adaf7944e0e26427b633c35827af011868bf3669abcacb91786661', 'patient', NOW()),
(15, 'Karan Patel', 'karan.patel@example.com', 'scrypt:32768:8:1$AwY5MwlZAFRDpqjJ$c807133c742f278791ab05bbe021db579ad85e47efcaf7135e31c99527a94e2b21bdfef061adaf7944e0e26427b633c35827af011868bf3669abcacb91786661', 'patient', NOW()),
(16, 'Diya Roy', 'diya.roy@example.com', 'scrypt:32768:8:1$AwY5MwlZAFRDpqjJ$c807133c742f278791ab05bbe021db579ad85e47efcaf7135e31c99527a94e2b21bdfef061adaf7944e0e26427b633c35827af011868bf3669abcacb91786661', 'patient', NOW());

INSERT INTO departments (dept_id, dept_name, head_doctor_id) VALUES
(1, 'Cardiology', NULL),
(2, 'Neurology', NULL),
(3, 'Orthopedics', NULL);

INSERT INTO doctors (
  doctor_id, user_id, dept_id, specialization, license_no, available_days, consultation_fee, phone, is_active, created_at
) VALUES
(1, 2, 1, 'Cardiologist', 'LIC-CARD-1001', 'Mon,Tue,Wed,Fri', 1200.00, '9001000001', 1, NOW()),
(2, 3, 2, 'Neurologist', 'LIC-NEUR-1002', 'Mon,Thu,Fri', 1500.00, '9001000002', 1, NOW()),
(3, 4, 3, 'Orthopedic Surgeon', 'LIC-ORTH-1003', 'Tue,Wed,Sat', 1800.00, '9001000003', 1, NOW()),
(4, 5, 1, 'Cardiac Electrophysiologist', 'LIC-CARD-1004', 'Mon,Wed,Thu', 2000.00, '9001000004', 1, NOW()),
(5, 6, 3, 'Sports Injury Specialist', 'LIC-ORTH-1005', 'Tue,Fri,Sat', 1400.00, '9001000005', 1, NOW());

UPDATE departments SET head_doctor_id = 1 WHERE dept_id = 1;
UPDATE departments SET head_doctor_id = 2 WHERE dept_id = 2;
UPDATE departments SET head_doctor_id = 3 WHERE dept_id = 3;

INSERT INTO patients (
  patient_id, user_id, patient_code, dob, gender, blood_group, phone, address, emergency_contact, is_active, created_at
) VALUES
(1, 7,  'PAT-0001', '1998-02-10', 'male',   'B+',  '9876500001', 'Pune',      '9876501001', 1, NOW()),
(2, 8,  'PAT-0002', '2001-08-21', 'female', 'O+',  '9876500002', 'Mumbai',    '9876501002', 1, NOW()),
(3, 9,  'PAT-0003', '1995-11-12', 'male',   'A+',  '9876500003', 'Nashik',    '9876501003', 1, NOW()),
(4, 10, 'PAT-0004', '1989-04-28', 'female', 'AB+', '9876500004', 'Nagpur',    '9876501004', 1, NOW()),
(5, 11, 'PAT-0005', '1992-01-17', 'male',   'O-',  '9876500005', 'Pune',      '9876501005', 1, NOW()),
(6, 12, 'PAT-0006', '2000-06-03', 'female', 'A-',  '9876500006', 'Solapur',   '9876501006', 1, NOW()),
(7, 13, 'PAT-0007', '1997-09-09', 'male',   'B-',  '9876500007', 'Kolhapur',  '9876501007', 1, NOW()),
(8, 14, 'PAT-0008', '1994-12-14', 'female', 'O+',  '9876500008', 'Sangli',    '9876501008', 1, NOW()),
(9, 15, 'PAT-0009', '1988-03-30', 'male',   'A+',  '9876500009', 'Satara',    '9876501009', 1, NOW()),
(10,16, 'PAT-0010', '2002-07-01', 'female', 'B+',  '9876500010', 'Aurangabad','9876501010', 1, NOW());

INSERT INTO rooms (room_id, room_number, type, floor, status, price_per_day) VALUES
(1, 'G-101', 'general', '1', 'available', 900.00),
(2, 'G-102', 'general', '1', 'occupied', 900.00),
(3, 'SP-201', 'semi_private', '2', 'occupied', 1800.00),
(4, 'SP-202', 'semi_private', '2', 'available', 1800.00),
(5, 'P-301', 'private', '3', 'available', 3200.00),
(6, 'P-302', 'private', '3', 'occupied', 3200.00),
(7, 'ICU-1', 'icu', 'ICU', 'occupied', 7500.00),
(8, 'ICU-2', 'icu', 'ICU', 'available', 7500.00);

INSERT INTO admissions (admission_id, patient_id, room_id, admitted_on, discharged_on) VALUES
(1, 2, 2, DATE_SUB(CURDATE(), INTERVAL 3 DAY), NULL),
(2, 4, 3, DATE_SUB(CURDATE(), INTERVAL 5 DAY), NULL),
(3, 5, 6, DATE_SUB(CURDATE(), INTERVAL 2 DAY), NULL),
(4, 9, 7, DATE_SUB(CURDATE(), INTERVAL 1 DAY), NULL);

INSERT INTO appointments (
  appt_id, patient_id, doctor_id, appt_date, appt_time, reason, status, notes, created_at, updated_at
) VALUES
(1, 1, 1, DATE_SUB(CURDATE(), INTERVAL 12 DAY), '10:00:00', 'Chest pain follow-up', 'completed', 'Stable vitals', NOW(), NOW()),
(2, 2, 2, DATE_SUB(CURDATE(), INTERVAL 9 DAY),  '11:30:00', 'Migraine', 'completed', 'MRI recommended', NOW(), NOW()),
(3, 3, 3, DATE_SUB(CURDATE(), INTERVAL 7 DAY),  '09:30:00', 'Knee pain', 'completed', 'Physiotherapy advised', NOW(), NOW()),
(4, 4, 1, DATE_SUB(CURDATE(), INTERVAL 1 DAY),  '14:00:00', 'ECG review', 'confirmed', '', NOW(), NOW()),
(5, 5, 4, CURDATE(),                            '10:30:00', 'Arrhythmia check', 'in_progress', '', NOW(), NOW()),
(6, 6, 5, CURDATE(),                            '12:00:00', 'Sports injury', 'pending', '', NOW(), NOW()),
(7, 7, 2, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '09:00:00', 'Headache consultation', 'pending', '', NOW(), NOW()),
(8, 8, 3, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '15:00:00', 'Shoulder pain', 'pending', '', NOW(), NOW()),
(9, 9, 1, DATE_ADD(CURDATE(), INTERVAL 3 DAY), '11:00:00', 'Routine cardiac check', 'confirmed', '', NOW(), NOW()),
(10,10,5, DATE_ADD(CURDATE(), INTERVAL 4 DAY), '16:00:00', 'Post-op review', 'pending', '', NOW(), NOW());

INSERT INTO medicines (medicine_id, name, quantity, price, expiry_date, is_active, created_at) VALUES
(1, 'Paracetamol 500mg', 120, 4.50,  '2027-06-30', 1, NOW()),
(2, 'Amoxicillin 250mg', 80, 12.00,  '2026-11-30', 1, NOW()),
(3, 'Atorvastatin 10mg', 65, 18.00,  '2027-02-28', 1, NOW()),
(4, 'Pantoprazole 40mg', 42, 9.75,   '2027-09-30', 1, NOW()),
(5, 'Metformin 500mg', 34, 7.60,     '2028-01-31', 1, NOW()),
(6, 'Ibuprofen 400mg', 8, 6.50,      '2026-12-31', 1, NOW()),
(7, 'Aspirin 75mg', 110, 3.20,       '2027-03-31', 1, NOW()),
(8, 'Vitamin D3', 6, 15.00,          '2027-08-31', 1, NOW());

INSERT INTO prescriptions (prescription_id, appt_id, medicine_id, dosage, duration, instructions, created_at) VALUES
(1, 1, 3, '1 tablet nightly', '30 days', 'After dinner', NOW()),
(2, 2, 4, '1 tablet before breakfast', '10 days', 'Empty stomach', NOW()),
(3, 3, 6, '1 tablet after meals', '5 days', 'Twice daily', NOW()),
(4, 4, 7, '1 tablet daily', '20 days', 'With water', NOW());

INSERT INTO bills (
  bill_id, patient_id, admission_id, consultation_fee, room_charges, medicine_charges,
  subtotal, tax, total, status, created_at, paid_at
) VALUES
(1, 1, NULL, 1200.00, 0.00, 18.00, 1218.00, 60.90, 1278.90, 'paid', DATE_SUB(NOW(), INTERVAL 10 DAY), DATE_SUB(NOW(), INTERVAL 9 DAY)),
(2, 2, 1,    1500.00, 3600.00, 9.75, 5109.75, 255.49, 5365.24, 'pending', DATE_SUB(NOW(), INTERVAL 1 DAY), NULL),
(3, 4, 2,    1200.00, 9000.00, 3.20, 10203.20, 510.16, 10713.36, 'pending', NOW(), NULL);

INSERT INTO feedback (feedback_id, user_id, message, submitted_at, status) VALUES
(1, 8, 'Appointment booking was smooth. Please add SMS alerts.', DATE_SUB(NOW(), INTERVAL 2 DAY), 'new'),
(2, 10, 'Room services were excellent.', DATE_SUB(NOW(), INTERVAL 1 DAY), 'reviewed');

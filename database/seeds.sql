-- =============================================
-- DATOS INICIALES / SEMILLA (SEED DATA)
-- =============================================

-- 1. Coberturas
INSERT INTO coberturas (nombre_cobertura) VALUES 
('Particular'),
('OSDE'),
('Swiss Medical'),
('Galeno');

-- 2. Especialidades
INSERT INTO especialidades (nombre_especialidad) VALUES 
('Cardiología'),
('Clínica Médica'),
('Dermatología'),
('Pediatría'),
('Traumatología');

-- 3. Consultorios
INSERT INTO consultorios (numero_consultorio, piso) VALUES 
('101', 'Planta Baja'),
('102', 'Planta Baja'),
('201', '1er Piso'),
('202', '1er Piso');
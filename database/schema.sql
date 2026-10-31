CREATE DATABASE IF NOT EXISTS centro_medico;
USE centro_medico;

-- 1. Tabla coberturas
CREATE TABLE IF NOT EXISTS coberturas(
  id_cobertura int auto_increment PRIMARY KEY,
  nombre_cobertura varchar(100)
);

-- 2. Tabla usuarios
CREATE TABLE IF NOT EXISTS usuarios(
  id_usuario int auto_increment PRIMARY KEY,
  rol_usuario enum('admin', 'recepcionista', 'paciente') NOT NULL,
  nombre_usuario varchar(100) NOT NULL,
  apellido_usuario varchar(100) NOT NULL,
  dni_usuario varchar(20) UNIQUE NOT NULL,
  email_usuario varchar(150) UNIQUE NOT NULL,
  password_hash varchar(255) NOT NULL,
  telefono_usuario varchar(20),
  id_cobertura int NULL,
  FOREIGN KEY (id_cobertura) references coberturas(id_cobertura)
);

-- 3. Tabla especialidades
CREATE TABLE IF NOT EXISTS especialidades(
  id_especialidad int auto_increment PRIMARY KEY,
  nombre_especialidad varchar(100) NOT NULL
);

-- 4. Tabla medicos
CREATE TABLE IF NOT EXISTS medicos(
    id_medico int auto_increment PRIMARY KEY,
    id_usuario int NOT NULL,
    id_especialidad int NOT NULL,
    matricula varchar(50) UNIQUE NOT NULL,
    FOREIGN KEY (id_usuario) references usuarios(id_usuario),
    FOREIGN KEY (id_especialidad) references especialidades(id_especialidad)
);

-- 5. Tabla consultorios
CREATE TABLE IF NOT EXISTS consultorios(
  id_consultorio int auto_increment PRIMARY KEY,
  numero_consultorio varchar(20) NOT NULL,
  piso varchar(20)
);

-- 6. Tabla agendas
CREATE TABLE IF NOT EXISTS agendas(
  id_agenda int auto_increment PRIMARY KEY,
  id_medico int NOT NULL,
  id_consultorio int NOT NULL,
  dia_semana int NOT NULL,
  hora_inicio time NOT NULL,
  hora_fin time NOT NULL,
  duracion_turno_minutos INT DEFAULT 60,
  FOREIGN KEY (id_medico) references medicos(id_medico),
  FOREIGN KEY (id_consultorio) references consultorios(id_consultorio)
);

-- 7. Tabla turnos
CREATE TABLE IF NOT EXISTS turnos(
  id_turno int AUTO_INCREMENT PRIMARY KEY,
  id_medico int NOT NULL,
  id_paciente int NULL,
  id_consultorio int NOT NULL,
  fecha_hora DATETIME NOT NULL,
  estado enum('disponible', 'reservado', 'confirmado', 'atendido', 'cancelado', 'ausente') NOT NULL DEFAULT 'disponible',
  token_qr varchar(255) UNIQUE NULL,
  fecha_hora_checkin DATETIME NULL,
  fecha_hora_cancelacion DATETIME NULL,
  FOREIGN KEY (id_medico) references medicos(id_medico),
  FOREIGN KEY (id_paciente) references usuarios(id_usuario),
  FOREIGN KEY (id_consultorio) references consultorios(id_consultorio)
);

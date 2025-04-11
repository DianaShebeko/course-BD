DROP TABLE IF EXISTS ApplicationItem;
DROP TABLE IF EXISTS Review;
DROP TABLE IF EXISTS Ad;
DROP TABLE IF EXISTS Application;
DROP TABLE IF EXISTS Manufacturer;
DROP TABLE IF EXISTS EquipmentType;
DROP TABLE IF EXISTS ApplicationStatus;
DROP TABLE IF EXISTS AppUser;  

CREATE TABLE AppUser (  
  Login VARCHAR PRIMARY KEY,
  Name VARCHAR NOT NULL,
  Phone VARCHAR CHECK (Phone ~ '^\+7\d{10}$'),
  Password VARCHAR NOT NULL CHECK (length(Password) >= 8)
);

CREATE TABLE ApplicationStatus (
  Name VARCHAR PRIMARY KEY
);

CREATE TABLE EquipmentType (
  Name VARCHAR PRIMARY KEY
);

CREATE TABLE Manufacturer (
  Name VARCHAR PRIMARY KEY
);

--������
CREATE TABLE Application (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  LandlordLogin VARCHAR NOT NULL,
  TenantLogin VARCHAR NOT NULL,
  RentStartDate DATE NOT NULL,
  RentEndDate DATE NOT NULL,
  ApplicationDate DATE NOT NULL DEFAULT CURRENT_DATE,
  StatusName VARCHAR NOT NULL,
  FOREIGN KEY (LandlordLogin) REFERENCES AppUser(Login) ON DELETE CASCADE,  
  FOREIGN KEY (TenantLogin) REFERENCES AppUser(Login), 
  FOREIGN KEY (StatusName) REFERENCES ApplicationStatus(Name),
  CHECK (RentStartDate <= RentEndDate)
);

--�������� ������������
CREATE TABLE Ad (
  id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  UserLogin VARCHAR,
  EquipmentTypeName VARCHAR,
  ManufacturerName VARCHAR,
  Title VARCHAR,
  Price DECIMAL(10, 2) CHECK (Price > 0),
  Description TEXT,
  FOREIGN KEY (UserLogin) REFERENCES AppUser(Login) ON DELETE CASCADE,  
  FOREIGN KEY (EquipmentTypeName) REFERENCES EquipmentType(Name),
  FOREIGN KEY (ManufacturerName) REFERENCES Manufacturer(Name)
);

--�����
CREATE TABLE Review (
  id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  AdId INTEGER NOT NULL,
  SenderLogin VARCHAR NOT NULL,
  Text TEXT NOT NULL,
  Rating INT CHECK (Rating BETWEEN 1 AND 5),
  PublishDate DATE NOT NULL DEFAULT CURRENT_DATE,
  FOREIGN KEY (AdId) REFERENCES Ad(id) ON DELETE CASCADE,
  FOREIGN KEY (SenderLogin) REFERENCES AppUser(Login)  
);

--������� ������
CREATE TABLE ApplicationItem (
  Number INTEGER NOT NULL,
  ApplicationId INTEGER NOT NULL,
  AdId INTEGER NOT NULL,
  EquipmentQuantity INT CHECK (EquipmentQuantity >= 1) DEFAULT 1,
  PRIMARY KEY (ApplicationId, AdId, Number),
  FOREIGN KEY (ApplicationId) REFERENCES Application(id) ON DELETE CASCADE,
  FOREIGN KEY (AdId) REFERENCES Ad(id) 
);

-- Insert into ApplicationStatus
INSERT INTO ApplicationStatus (Name) VALUES
    ('��������'),
    ('�� ������������'),
    ('�������'),
    ('���������');

-- Insert into EquipmentType
INSERT INTO EquipmentType (Name) VALUES
    ('������'),
    ('��������'),
    ('�������� ������'), 
    ('�������'),
    ('�������� �����'),
    ('������ ��� ������');

-- Insert into Manufacturer
INSERT INTO Manufacturer (Name) VALUES
    ('Sony'),
    ('Panasonic'),
    ('Sennheiser'),
    ('Canon'),
    ('Nikon'),
    ('Manfrotto'),
    ('Shure'),
    ('Atomos'),
    ('DJI');

-- Insert into AppUser
INSERT INTO AppUser VALUES
    ('user1@example.com', '���� ������', '+79991234567', 'password1'),
    ('user2@example.com', 'television-studio.com', '+79997654321', 'password2'),
    ('user3@example.com', '�����', '+79998765432', 'password3'),
    ('user4@example.com', '������� ���������', '+79998767462', 'password4');

-- Insert into Ad (UserLogin, EquipmentTypeName, ManufacturerName, Title, Price, Description)
INSERT INTO Ad (UserLogin, EquipmentTypeName, ManufacturerName, Title, Price, Description) VALUES
    ('user1@example.com', '������', 'Sony', 'Sony A7 III Full-frame ������ ��� ���������������� ���������� � �����', 2000.00, 'Full-frame camera for photo and video shooting'),
    ('user2@example.com', '��������', 'Sennheiser', 'Sennheiser EW 112P G4 Wireless Microphone System with Receiver and Transmitter', 1500.00, 'Wireless microphone system for clear audio capture in various environments'),
    ('user3@example.com', '�������� ������', 'Panasonic', 'Panasonic LED Panel for Studio and Outdoor Lighting, Adjustable Brightness and Color Temperature', 1000.00, 'Portable LED panel for filming with adjustable brightness and color temperature'),
    ('user1@example.com', '������ ��� ������', 'Manfrotto', 'Manfrotto Compact Action ������ ��� ������', 150.00, '���������� � ������ ������'),
    ('user4@example.com', '������', 'Canon', 'Canon EOS 5D Mark IV ������������� �������� ���������� ������ ��� ���������������� ���������� � �����������', 2500.00, '������������� DSLR ������ ��� ������������������ ���������� � �����������������');


-- Insert into Application
INSERT INTO Application (LandlordLogin, TenantLogin, RentStartDate, RentEndDate, StatusName) VALUES
    ('user1@example.com', 'user2@example.com', '2024-12-01', '2024-12-10', '�� ������������'),
    ('user2@example.com', 'user3@example.com', '2024-12-05', '2024-12-15', '�������'),
    ('user3@example.com', 'user1@example.com', '2024-12-10', '2024-12-20', '���������'),
    ('user1@example.com', 'user4@example.com', '2024-12-15', '2024-12-25', '�� ������������');

-- Insert into Review (AdId, SenderLogin, Text, Rating)
INSERT INTO Review (AdId, SenderLogin, Text, Rating) VALUES
    (1, 'user2@example.com', '��� ���� ��', 5),
    (2, 'user3@example.com', '������ ��������. � ��� ��� ���������', 4),
    (3, 'user1@example.com', '�������', 5);

-- Insert into ApplicationItem
INSERT INTO ApplicationItem (ApplicationId, AdId, Number, EquipmentQuantity) VALUES
    (1, 1, 1, 1),
    (2, 2, 1, 2),
    (3, 3, 1, 1),
    (1, 4, 2, 2);
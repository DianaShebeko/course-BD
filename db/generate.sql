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

--заявка
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

--карточка оборудования
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

--отзыв
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

--позиция заявки
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
    ('Черновик'),
    ('На рассмотрении'),
    ('Принята'),
    ('Отклонена');

-- Insert into EquipmentType
INSERT INTO EquipmentType (Name) VALUES
    ('Камера'),
    ('Микрофон'),
    ('Световой прибор'), 
    ('Тренога'),
    ('Звуковая карта'),
    ('Штатив для камеры');

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
    ('user1@example.com', 'Иван Иванов', '+79991234567', 'password1'),
    ('user2@example.com', 'television-studio.com', '+79997654321', 'password2'),
    ('user3@example.com', 'Мария', '+79998765432', 'password3'),
    ('user4@example.com', 'Дмитрий Гришковец', '+79998767462', 'password4');

-- Insert into Ad (UserLogin, EquipmentTypeName, ManufacturerName, Title, Price, Description)
INSERT INTO Ad (UserLogin, EquipmentTypeName, ManufacturerName, Title, Price, Description) VALUES
    ('user1@example.com', 'Камера', 'Sony', 'Sony A7 III Full-frame камера для профессиональной фотографии и видео', 2000.00, 'Full-frame camera for photo and video shooting'),
    ('user2@example.com', 'Микрофон', 'Sennheiser', 'Sennheiser EW 112P G4 Wireless Microphone System with Receiver and Transmitter', 1500.00, 'Wireless microphone system for clear audio capture in various environments'),
    ('user3@example.com', 'Световой прибор', 'Panasonic', 'Panasonic LED Panel for Studio and Outdoor Lighting, Adjustable Brightness and Color Temperature', 1000.00, 'Portable LED panel for filming with adjustable brightness and color temperature'),
    ('user1@example.com', 'Штатив для камеры', 'Manfrotto', 'Manfrotto Compact Action штатив для камеры', 150.00, 'Компактный и легкий штатив'),
    ('user4@example.com', 'Камера', 'Canon', 'Canon EOS 5D Mark IV полнокадровая цифровая зеркальная камера для профессиональной фотографии и видеосъемки', 2500.00, 'Полнокадровая DSLR камера для высококачественной фотографии и видеопроизводства');


-- Insert into Application
INSERT INTO Application (LandlordLogin, TenantLogin, RentStartDate, RentEndDate, StatusName) VALUES
    ('user1@example.com', 'user2@example.com', '2024-12-01', '2024-12-10', 'На рассмотрении'),
    ('user2@example.com', 'user3@example.com', '2024-12-05', '2024-12-15', 'Принята'),
    ('user3@example.com', 'user1@example.com', '2024-12-10', '2024-12-20', 'Отклонена'),
    ('user1@example.com', 'user4@example.com', '2024-12-15', '2024-12-25', 'На рассмотрении');

-- Insert into Review (AdId, SenderLogin, Text, Rating)
INSERT INTO Review (AdId, SenderLogin, Text, Rating) VALUES
    (1, 'user2@example.com', 'Все было ок', 5),
    (2, 'user3@example.com', 'Разъем расшатан. А так все нормально', 4),
    (3, 'user1@example.com', 'Спасибо', 5);

-- Insert into ApplicationItem
INSERT INTO ApplicationItem (ApplicationId, AdId, Number, EquipmentQuantity) VALUES
    (1, 1, 1, 1),
    (2, 2, 1, 2),
    (3, 3, 1, 1),
    (1, 4, 2, 2);
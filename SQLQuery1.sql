USE CarRentalSystem;

-- ─────────────────────────────────────────
--  CREATE TABLES
-- ─────────────────────────────────────────

CREATE TABLE Office (
    office_id    INT PRIMARY KEY IDENTITY(1,1),
    location     VARCHAR(100) NOT NULL,
    contact_info VARCHAR(100)
);
CREATE TABLE Car (
    car_id    INT PRIMARY KEY IDENTITY(1,1),
    office_id INT NOT NULL,
    model     VARCHAR(50)  NOT NULL,
    year      INT          NOT NULL,
    plate_id  VARCHAR(20)  NOT NULL UNIQUE,
    status    VARCHAR(20)  DEFAULT 'active' CHECK (status IN ('active', 'rented', 'out_of_service')),
    FOREIGN KEY (office_id) REFERENCES Office(office_id)
);

CREATE TABLE Customer (
    customer_id INT PRIMARY KEY IDENTITY(1,1),
    name        VARCHAR(100) NOT NULL,
    phone       VARCHAR(20),
    email       VARCHAR(100) UNIQUE,
    address     VARCHAR(200)
);

CREATE TABLE Reservation (
    reservation_id INT PRIMARY KEY IDENTITY(1,1),
    car_id         INT  NOT NULL,
    customer_id    INT  NOT NULL,
    start_date     DATE NOT NULL,
    end_date       DATE NOT NULL,
    status         VARCHAR(20) DEFAULT 'reserved' CHECK (status IN ('reserved', 'picked_up', 'returned', 'cancelled')),
    FOREIGN KEY (car_id)      REFERENCES Car(car_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

CREATE TABLE Payment (
    payment_id     INT PRIMARY KEY IDENTITY(1,1),
    reservation_id INT            NOT NULL UNIQUE,
    amount         DECIMAL(10, 2) NOT NULL,
    payment_date   DATE           NOT NULL,
    method         VARCHAR(20) DEFAULT 'cash' CHECK (method IN ('cash', 'credit_card', 'debit_card', 'online')),
    FOREIGN KEY (reservation_id) REFERENCES Reservation(reservation_id)
);
-- ─────────────────────────────────────────
--  SAMPLE DATA
-- ─────────────────────────────────────────

-- Offices
INSERT INTO Office (location, contact_info) VALUES
('Cairo — Nasr City',      '+20 2 1234 5678'),
('Alexandria — Smouha',    '+20 3 9876 5432'),
('Giza — Mohandessin',     '+20 2 5555 1010'),
('Luxor — City Center',    '+20 95 333 2222'),
('Sharm El-Sheikh — Naama','+20 69 777 8888');

-- Cars
INSERT INTO Car (office_id, model, year, plate_id, status) VALUES
(1, 'Toyota Corolla',   2022, 'ABC-1234', 'active'),
(1, 'Hyundai Elantra',  2021, 'XYZ-5678', 'rented'),
(2, 'Kia Sportage',     2023, 'DEF-9012', 'active'),
(2, 'Nissan Sunny',     2020, 'GHI-3456', 'out_of_service'),
(3, 'Honda Civic',      2022, 'JKL-7890', 'active'),
(3, 'Chevrolet Aveo',   2019, 'MNO-1122', 'rented'),
(4, 'Toyota Land Cruiser',2023,'PQR-3344','active'),
(4, 'Mitsubishi Lancer',2021, 'STU-5566', 'active'),
(5, 'Ford Escape',      2022, 'VWX-7788', 'rented'),
(5, 'BMW 320i',         2023, 'YZA-9900', 'active');

-- Customers
INSERT INTO Customer (name, phone, email, address) VALUES
('Ahmed Hassan',    '01001234567', 'ahmed.hassan@email.com',    'Cairo, Heliopolis'),
('Sara Mohamed',    '01112345678', 'sara.mohamed@email.com',    'Alexandria, Sidi Gaber'),
('Omar Ali',        '01223456789', 'omar.ali@email.com',        'Giza, Dokki'),
('Nour Ibrahim',    '01334567890', 'nour.ibrahim@email.com',    'Luxor, West Bank'),
('Mia Youssef',     '01445678901', 'mia.youssef@email.com',     'Sharm, Hadaba'),
('Khaled Samir',    '01556789012', 'khaled.samir@email.com',    'Cairo, Maadi'),
('Layla Fawzy',     '01667890123', 'layla.fawzy@email.com',     'Alexandria, Miami'),
('Youssef Tarek',   '01778901234', 'youssef.tarek@email.com',   'Cairo, 6th October'),
('Dina Ramzy',      '01889012345', 'dina.ramzy@email.com',      'Giza, Zamalek'),
('Karim Nader',     '01990123456', 'karim.nader@email.com',     'Hurghada, Downtown');

-- Reservations
INSERT INTO Reservation (car_id, customer_id, start_date, end_date, status) VALUES
(1,  1,  '2026-04-01', '2026-04-05', 'returned'),
(2,  2,  '2026-04-10', '2026-04-15', 'returned'),
(3,  3,  '2026-04-20', '2026-04-25', 'returned'),
(5,  4,  '2026-05-01', '2026-05-03', 'returned'),
(6,  5,  '2026-05-05', '2026-05-10', 'picked_up'),
(9,  6,  '2026-05-08', '2026-05-12', 'picked_up'),
(2,  7,  '2026-05-10', '2026-05-15', 'reserved'),
(7,  8,  '2026-05-15', '2026-05-20', 'reserved'),
(10, 9,  '2026-05-20', '2026-05-25', 'reserved'),
(1,  10, '2026-05-25', '2026-05-30', 'reserved');

-- Payments
INSERT INTO Payment (reservation_id, amount, payment_date, method) VALUES
(1,  500.00,  '2026-04-05', 'cash'),
(2,  750.00,  '2026-04-15', 'credit_card'),
(3,  600.00,  '2026-04-25', 'online'),
(4,  300.00,  '2026-05-03', 'debit_card'),
(5,  800.00,  '2026-05-10', 'cash'),
(6,  960.00,  '2026-05-12', 'credit_card');


-- ─────────────────────────────────────────
--  REQUIRED REPORTS
-- ─────────────────────────────────────────

-- ① All reservations within a specified period (with car + customer info)
SELECT
    r.reservation_id,
    r.start_date,
    r.end_date,
    r.status                  AS reservation_status,
    c.name                    AS customer_name,
    c.phone,
    c.email,
    ca.model                  AS car_model,
    ca.plate_id,
    ca.year,
    o.location                AS office_location
FROM Reservation r
JOIN Customer    c  ON r.customer_id = c.customer_id
JOIN Car         ca ON r.car_id      = ca.car_id
JOIN Office      o  ON ca.office_id  = o.office_id
WHERE r.start_date BETWEEN '2026-04-01' AND '2026-05-31'
ORDER BY r.start_date;

-- ② Status of all cars on a specific day (e.g. 2026-05-10)
SELECT
    ca.car_id,
    ca.model,
    ca.plate_id,
    ca.year,
    o.location AS office,
    CASE
        WHEN r.reservation_id IS NOT NULL
         AND r.status IN ('picked_up','reserved')
         AND '2026-05-10' BETWEEN r.start_date AND r.end_date
        THEN 'rented'
        ELSE ca.status
    END AS status_on_day
FROM Car    ca
JOIN Office  o ON ca.office_id = o.office_id
LEFT JOIN Reservation r
       ON ca.car_id = r.car_id
      AND r.status IN ('picked_up','reserved')
      AND '2026-05-10' BETWEEN r.start_date AND r.end_date
ORDER BY ca.car_id;

-- ③ All reservations of a specific customer (e.g. customer_id = 2)
SELECT
    r.reservation_id,
    r.start_date,
    r.end_date,
    r.status                 AS reservation_status,
    c.customer_id,
    c.name                   AS customer_name,
    c.phone,
    c.email,
    ca.model                 AS car_model,
    ca.plate_id
FROM Reservation r
JOIN Customer    c  ON r.customer_id = c.customer_id
JOIN Car         ca ON r.car_id      = ca.car_id
WHERE c.customer_id = 2
ORDER BY r.start_date;


-- ④ Daily payments within a specific period
SELECT
    p.payment_date,
    SUM(p.amount)                                    AS total_daily_revenue,
    COUNT(*)                                         AS number_of_payments,
    STRING_AGG(p.method, ', ') WITHIN GROUP (ORDER BY p.payment_id) AS payment_methods
FROM Payment p
WHERE p.payment_date BETWEEN '2026-04-01' AND '2026-05-31'
GROUP BY p.payment_date
ORDER BY p.payment_date;



-- ─────────────────────────────────────────
-- 1. Register a new car
-- ─────────────────────────────────────────
CREATE PROCEDURE RegisterCar
    @office_id INT,
    @model     VARCHAR(50),
    @year      INT,
    @plate_id  VARCHAR(20)
AS
BEGIN
    INSERT INTO Car (office_id, model, year, plate_id, status)
    VALUES (@office_id, @model, @year, @plate_id, 'active');
END;

-- ─────────────────────────────────────────
-- 2. Update car status
-- ─────────────────────────────────────────
CREATE PROCEDURE UpdateCarStatus
    @car_id INT,
    @status VARCHAR(20)
AS
BEGIN
    UPDATE Car
    SET status = @status
    WHERE car_id = @car_id;
END;

-- ─────────────────────────────────────────
-- 3. Create customer account
-- ─────────────────────────────────────────
CREATE PROCEDURE RegisterCustomer
    @name    VARCHAR(100),
    @phone   VARCHAR(20),
    @email   VARCHAR(100),
    @address VARCHAR(200)
AS
BEGIN
    INSERT INTO Customer (name, phone, email, address)
    VALUES (@name, @phone, @email, @address);
END;

-- ─────────────────────────────────────────
-- 4. Make a reservation
-- ─────────────────────────────────────────
create PROCEDURE MakeReservation
    @car_id      INT,
    @customer_id INT,
    @start_date  DATE,
    @end_date    DATE
AS
BEGIN
    -- Block if car is not active
    IF NOT EXISTS (
        SELECT 1 FROM Car
        WHERE car_id = @car_id
          AND status = 'active'
    )
    BEGIN
        RAISERROR('Car is not available (rented or out of service).', 16, 1);
        RETURN;
    END

    -- Block if car has overlapping reservation
    IF EXISTS (
        SELECT 1 FROM Reservation
        WHERE car_id = @car_id
          AND status IN ('reserved', 'picked_up')
          AND @start_date <= end_date
          AND @end_date   >= start_date
    )
    BEGIN
        RAISERROR('Car is already reserved on the selected dates.', 16, 1);
        RETURN;
    END

    INSERT INTO Reservation (car_id, customer_id, start_date, end_date, status)
    VALUES (@car_id, @customer_id, @start_date, @end_date, 'reserved');
END;

-- ─────────────────────────────────────────
-- 5. Pick up a car
-- ─────────────────────────────────────────
CREATE PROCEDURE PickUpCar
    @reservation_id INT
AS
BEGIN
    UPDATE Reservation
    SET status = 'picked_up'
    WHERE reservation_id = @reservation_id;

    -- Also update the car status to rented
    UPDATE Car
    SET status = 'rented'
    WHERE car_id = (
        SELECT car_id FROM Reservation
        WHERE reservation_id = @reservation_id
    );
END;

-- ─────────────────────────────────────────
-- 6. Return a car
-- ─────────────────────────────────────────
CREATE PROCEDURE ReturnCar
    @reservation_id INT
AS
BEGIN
    UPDATE Reservation
    SET status = 'returned'
    WHERE reservation_id = @reservation_id;

    -- Also update the car status back to active
    UPDATE Car
    SET status = 'active'
    WHERE car_id = (
        SELECT car_id FROM Reservation
        WHERE reservation_id = @reservation_id
    );
END;

-- ─────────────────────────────────────────
-- 7. Make a payment
-- ─────────────────────────────────────────
-- Fix MakePayment: block duplicate payment for same reservation

CREATE PROCEDURE MakePayment
    @reservation_id INT,
    @amount         DECIMAL(10,2),
    @payment_date   DATE,
    @method         VARCHAR(20)
AS
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Reservation WHERE reservation_id = @reservation_id)
    BEGIN
        RAISERROR('Reservation ID does not exist.', 16, 1);
        RETURN;
    END

    IF EXISTS (SELECT 1 FROM Payment WHERE reservation_id = @reservation_id)
    BEGIN
        RAISERROR('A payment already exists for this reservation.', 16, 1);
        RETURN;
    END

    INSERT INTO Payment (reservation_id, amount, payment_date, method)
    VALUES (@reservation_id, @amount, @payment_date, @method);
END;
GO

-- Fix UpdateCarStatus: block if car ID doesn't exist
DROP PROCEDURE IF EXISTS UpdateCarStatus;
GO
CREATE PROCEDURE UpdateCarStatus
    @car_id INT,
    @status VARCHAR(20)
AS
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Car WHERE car_id = @car_id)
    BEGIN
        RAISERROR('Car ID does not exist.', 16, 1);
        RETURN;
    END

    UPDATE Car SET status = @status WHERE car_id = @car_id;
END;
GO

-- ─────────────────────────────────────────
-- 8. Search available cars by specs
-- ─────────────────────────────────────────
CREATE PROCEDURE SearchCars
    @model      VARCHAR(50) = NULL,
    @year       INT         = NULL,
    @office_id  INT         = NULL
AS
BEGIN
    SELECT
        ca.car_id,
        ca.model,
        ca.year,
        ca.plate_id,
        ca.status,
        o.location AS office
    FROM Car ca
    JOIN Office o ON ca.office_id = o.office_id
    WHERe  (@model     IS NULL OR ca.model     LIKE '%' + @model + '%')
      AND (@year      IS NULL OR ca.year      = @year)
      AND (@office_id IS NULL OR ca.office_id = @office_id);
END;

-- ─────────────────────────────────────────
-- REPORT 1: All reservations in a period
-- ─────────────────────────────────────────
CREATE PROCEDURE ReportReservationsByPeriod
    @start_date DATE,
    @end_date   DATE
AS
BEGIN
    SELECT
        r.reservation_id,
        r.start_date,
        r.end_date,
        r.status              AS reservation_status,
        c.name                AS customer_name,
        c.phone,
        c.email,
        ca.model              AS car_model,
        ca.plate_id,
        ca.year,
        o.location            AS office_location
    FROM Reservation r
    JOIN Customer c  ON r.customer_id = c.customer_id
    JOIN Car      ca ON r.car_id      = ca.car_id
    JOIN Office   o  ON ca.office_id  = o.office_id
    WHERE r.start_date BETWEEN @start_date AND @end_date
    ORDER BY r.start_date;
END;

-- ─────────────────────────────────────────
-- REPORT 2: Status of all cars on a specific day
-- ─────────────────────────────────────────
CREATE PROCEDURE ReportCarStatusOnDay
    @day DATE
AS
BEGIN
    SELECT
        ca.car_id,
        ca.model,
        ca.plate_id,
        ca.year,
        o.location AS office,
        CASE
            WHEN r.reservation_id IS NOT NULL
            THEN 'rented'
            ELSE ca.status
        END AS status_on_day
    FROM Car ca
    JOIN Office o ON ca.office_id = o.office_id
    LEFT JOIN Reservation r
           ON ca.car_id = r.car_id
          AND r.status IN ('picked_up', 'reserved')
          AND @day BETWEEN r.start_date AND r.end_date
    ORDER BY ca.car_id;
END;

-- ─────────────────────────────────────────
-- REPORT 3: All reservations of a specific customer
-- ─────────────────────────────────────────
CREATE PROCEDURE ReportCustomerReservations
    @customer_id INT
AS
BEGIN
    SELECT
        r.reservation_id,
        r.start_date,
        r.end_date,
        r.status          AS reservation_status,
        c.customer_id,
        c.name            AS customer_name,
        c.phone,
        c.email,
        ca.model          AS car_model,
        ca.plate_id
    FROM Reservation r
    JOIN Customer c  ON r.customer_id = c.customer_id
    JOIN Car      ca ON r.car_id      = ca.car_id
    WHERE c.customer_id = @customer_id
    ORDER BY r.start_date;
END;

-- ─────────────────────────────────────────
-- REPORT 4: Daily payments within a period
-- ─────────────────────────────────────────
CREATE PROCEDURE ReportDailyPayments
    @start_date DATE,
    @end_date   DATE
AS
BEGIN
    SELECT
        p.payment_date,
        SUM(p.amount)  AS total_daily_revenue,
        COUNT(*)       AS number_of_payments,
        STRING_AGG(p.method, ', ') WITHIN GROUP (ORDER BY p.payment_id) AS payment_methods
    FROM Payment p
    WHERE p.payment_date BETWEEN @start_date AND @end_date
    GROUP BY p.payment_date
    ORDER BY p.payment_date;
END;


EXEC RegisterCar         2, 'Toyota Yaris', 2024, 'NEW-111';
EXEC UpdateCarStatus     1, 'out_of_service';
EXEC RegisterCustomer    'Ali Ahmed', '01012345678', 'ali@email.com', 'Cairo';
EXEC MakeReservation     1, 3, '2026-06-01', '2026-06-05';
EXEC PickUpCar           1;
EXEC ReturnCar           1;
EXEC MakePayment         1, 400.00, '2026-06-05', 'cash';
EXEC SearchCars          'Toyota', NULL, NULL;
EXEC ReportReservationsByPeriod '2026-04-01', '2026-05-31';
EXEC ReportCarStatusOnDay       '2026-05-10';
EXEC ReportCustomerReservations 2;
EXEC ReportDailyPayments        '2026-04-01', '2026-05-31';
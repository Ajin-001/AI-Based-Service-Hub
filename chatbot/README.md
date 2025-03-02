Command for creating database 

CREATE DATABASE `academic_project` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `academic_project`;

Command for creating location table 

CREATE TABLE `location_table` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `service_provider` VARCHAR(255) CHARACTER SET utf8mb4 NOT NULL,
    `location` VARCHAR(255) CHARACTER SET utf8mb4 NOT NULL,
    `place` VARCHAR(255) CHARACTER SET utf8mb4 NOT NULL,
    `center_name` VARCHAR(255) CHARACTER SET utf8mb4 NOT NULL,
    `google_map_link` TEXT CHARACTER SET utf8mb4 NOT NULL,
    `contact_number` VARCHAR(20) CHARACTER SET utf8mb4 NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


Command for creating appointment table

CREATE TABLE `appointments` (
    `appointment_id` VARCHAR(255) CHARACTER SET utf8mb4 NOT NULL,
    `place` VARCHAR(255) CHARACTER SET utf8mb4 NOT NULL,
    `service_provider` VARCHAR(255) CHARACTER SET utf8mb4 NOT NULL,
    `service` VARCHAR(255) CHARACTER SET utf8mb4 NOT NULL,
    `date` VARCHAR(255) CHARACTER SET utf8mb4 NOT NULL,
    `time` VARCHAR(255) CHARACTER SET utf8mb4 NOT NULL,
    `user_id` VARCHAR(255) CHARACTER SET utf8mb4 NOT NULL,
    PRIMARY KEY (`appointment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;




Step 1:

python -m venv venv

Step 2:

venv\Scripts\activate

Step 3:

pip install -r requirements.txt

Step 4:

uvicorn src.app.main:app 







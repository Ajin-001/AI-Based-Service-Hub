-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 15, 2025 at 09:31 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `chatbot_project`
--

-- --------------------------------------------------------

--
-- Table structure for table `appointments`
--

CREATE TABLE `appointments` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `service_center_id` int(11) NOT NULL,
  `time_slot` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `appointments`
--

INSERT INTO `appointments` (`id`, `user_id`, `service_center_id`, `time_slot`) VALUES
(8, 7, 1, '2025-03-16 09:00:00'),
(9, 7, 1, '2025-03-15 14:30:00');

-- --------------------------------------------------------

--
-- Table structure for table `auth`
--

CREATE TABLE `auth` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth`
--

INSERT INTO `auth` (`id`, `username`, `email`, `password_hash`) VALUES
(1, 'Ajin', 'ajin@rit.in', 'scrypt:32768:8:1$TFL0JMGBw4C8kXh9$c0a2d082c9e290243ddede58261dea807844d1b8eaa7ac617afdfdcf1bc62ea7f94e527c6a908622226d80bd5865de517b18282b45edec0694fbcacbfeba3a55'),
(7, 'Ajin M', '23mp2243@rit.ac.in', 'scrypt:32768:8:1$3NS0C7XXXt4hkRRo$1f82b20e6a1e0fc46d0933af3c22635dda1f4d9b87a59783ed817b7fa9710cf879bf1b5b5e1f5580eea7bbc7e034ad4068fd85a7ea394ec0790531e1c4593689');

-- --------------------------------------------------------

--
-- Table structure for table `chat_logs`
--

CREATE TABLE `chat_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `message` text NOT NULL,
  `response` text NOT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  `user_message` text NOT NULL,
  `bot_response` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `chat_logs`
--

INSERT INTO `chat_logs` (`id`, `user_id`, `message`, `response`, `timestamp`, `user_message`, `bot_response`) VALUES
(302, 7, '', '', '2025-03-15 13:14:55', 'hi', 'Hi there! How can I assist you today?\n'),
(303, 7, '', '', '2025-03-15 13:15:07', 'my phone is dim', 'Hi!  What phone model are you using?  Can you describe how dim the screen is?  How long has this been happening?\n'),
(304, 7, '', '', '2025-03-15 13:15:16', 'nokia c101', 'Hi!\n\nThanks for letting me know.  To help me assist you better with your Nokia C101\'s dim screen, could you please describe how dim the screen is?  Is it barely visible, or just slightly less bright than usual?  Also, how long has this been happening?\n'),
(305, 7, '', '', '2025-03-15 13:15:24', 'less than a day', 'Okay. Let\'s try some troubleshooting steps for your Nokia C101\'s dim screen.\n\n1. **Restart your phone:**  Turn it off completely, wait 30 seconds, then turn it back on.\n\n2. **Check brightness settings:** Make sure the brightness isn\'t set too low in your phone\'s settings.\n\nDid that help?\n'),
(306, 7, '', '', '2025-03-15 13:15:37', 'no', 'Okay. Let\'s try some further steps:\n\n3. **Check for software updates:** Go to your phone\'s settings and check for any available software updates. Installing updates sometimes fixes display issues.\n\n4. **Reset network settings:** This won\'t erase your data, but it might resolve software glitches affecting the display.  You can find this in your phone\'s settings under \"Network & internet\" or similar.\n\nDid any of these steps help?\n'),
(307, 7, '', '', '2025-03-15 13:15:43', 'no', 'Okay.  Since the problem persists, let\'s try a factory reset.  **Warning:** This will erase all data on your phone.  Back up anything important if possible.  If you\'re not comfortable with this, or if the problem continues after the reset, it might be a hardware issue requiring professional attention.  Would you like instructions on how to perform a factory reset, or would you prefer I help you locate an authorized Nokia service center?\n'),
(308, 7, '', '', '2025-03-15 13:15:51', 'Kochi', 'Please wait while I fetch the details. Redirecting you to the appointment page...'),
(309, 7, '', '', '2025-03-15 13:16:18', 'bye', 'Goodbye, Ajin M! Have a great day!');

-- --------------------------------------------------------

--
-- Table structure for table `reviews`
--

CREATE TABLE `reviews` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `service_center_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL CHECK (`rating` between 1 and 5),
  `comment` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `reviews`
--

INSERT INTO `reviews` (`id`, `user_id`, `service_center_id`, `rating`, `comment`) VALUES
(2, 7, 1, 4, 'good');

-- --------------------------------------------------------

--
-- Table structure for table `service_centers`
--

CREATE TABLE `service_centers` (
  `id` int(11) NOT NULL,
  `service_provider` varchar(100) NOT NULL,
  `place` varchar(100) NOT NULL,
  `center_name` varchar(255) NOT NULL,
  `name` varchar(100) NOT NULL,
  `location` varchar(255) NOT NULL,
  `google_map_link` text NOT NULL,
  `contact_number` varchar(20) NOT NULL,
  `rating` float DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `service_centers`
--

INSERT INTO `service_centers` (`id`, `service_provider`, `place`, `center_name`, `name`, `location`, `google_map_link`, `contact_number`, `rating`) VALUES
(1, 'Jio', 'Kochi', 'Jio Centre At Oberon Mall', '', 'Jio Centre At Oberon Mall, No. 195, Oberon Mall, 2nd Floor, NH-47 Byepass, Padivattom, Edappally, Kochi, Kerala 682024', 'https://www.google.com/maps/dir/10.0226529,76.2694425/Jio+Centre+At+Oberon+Mall', '1860 893 3333', 4);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `appointments`
--
ALTER TABLE `appointments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `service_center_id` (`service_center_id`);

--
-- Indexes for table `auth`
--
ALTER TABLE `auth`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `chat_logs`
--
ALTER TABLE `chat_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `reviews`
--
ALTER TABLE `reviews`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_center` (`user_id`,`service_center_id`),
  ADD KEY `service_center_id` (`service_center_id`);

--
-- Indexes for table `service_centers`
--
ALTER TABLE `service_centers`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `appointments`
--
ALTER TABLE `appointments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `auth`
--
ALTER TABLE `auth`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `chat_logs`
--
ALTER TABLE `chat_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=310;

--
-- AUTO_INCREMENT for table `reviews`
--
ALTER TABLE `reviews`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `service_centers`
--
ALTER TABLE `service_centers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `appointments`
--
ALTER TABLE `appointments`
  ADD CONSTRAINT `appointments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `auth` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `appointments_ibfk_2` FOREIGN KEY (`service_center_id`) REFERENCES `service_centers` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `chat_logs`
--
ALTER TABLE `chat_logs`
  ADD CONSTRAINT `chat_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `auth` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `reviews`
--
ALTER TABLE `reviews`
  ADD CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `auth` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`service_center_id`) REFERENCES `service_centers` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

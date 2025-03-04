-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 04, 2025 at 12:44 PM
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
-- Database: `em8database_surveillanceguardian`
--

-- --------------------------------------------------------

--
-- Table structure for table `cameras`
--

CREATE TABLE `cameras` (
  `camera_id` varchar(255) NOT NULL,
  `device_id` int(11) NOT NULL,
  `camera_name` varchar(255) NOT NULL,
  `camera_status` varchar(255) NOT NULL,
  `check_date` date NOT NULL,
  `check_time` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `changelog`
--

CREATE TABLE `changelog` (
  `changelog_id` int(11) NOT NULL,
  `device_id` int(11) NOT NULL,
  `changelog_desc` varchar(500) NOT NULL,
  `previous_status` varchar(255) NOT NULL,
  `current_status` varchar(255) NOT NULL,
  `changelog_date` date NOT NULL,
  `changelog_time` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sg_devices`
--

CREATE TABLE `sg_devices` (
  `device_id` int(11) NOT NULL,
  `device_type` int(11) NOT NULL,
  `iccid` bigint(20) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sg_device_types`
--

CREATE TABLE `sg_device_types` (
  `device_type` int(11) NOT NULL,
  `device_type_desc` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sg_pi`
--

CREATE TABLE `sg_pi` (
  `iccid` varchar(23) NOT NULL,
  `site_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `imei` bigint(20) UNSIGNED NOT NULL,
  `eth_address` varchar(56) NOT NULL,
  `ppp_address` varchar(255) NOT NULL,
  `activate_status` tinyint(1) NOT NULL,
  `suspend_status` tinyint(1) NOT NULL,
  `install_date` date NOT NULL,
  `version_no` varchar(48) NOT NULL,
  `check_date` date NOT NULL,
  `check_time` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sg_storage`
--

CREATE TABLE `sg_storage` (
  `device_id` int(11) NOT NULL,
  `storage_id` varchar(255) NOT NULL,
  `storage_name` varchar(255) NOT NULL,
  `storage_status` varchar(255) NOT NULL,
  `check_date` date NOT NULL,
  `check_time` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sg_system`
--

CREATE TABLE `sg_system` (
  `system_id` varchar(255) NOT NULL,
  `device_id` int(11) NOT NULL,
  `system_name` varchar(255) NOT NULL,
  `system_status` varchar(255) NOT NULL,
  `system_firmware` varchar(255) NOT NULL,
  `system_datetime` tinyint(1) NOT NULL,
  `check_date` date NOT NULL,
  `check_time` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sites`
--

CREATE TABLE `sites` (
  `site_id` int(11) NOT NULL,
  `site_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cameras`
--
ALTER TABLE `cameras`
  ADD PRIMARY KEY (`camera_id`);

--
-- Indexes for table `sg_devices`
--
ALTER TABLE `sg_devices`
  ADD PRIMARY KEY (`device_id`);

--
-- Indexes for table `sg_pi`
--
ALTER TABLE `sg_pi`
  ADD PRIMARY KEY (`iccid`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

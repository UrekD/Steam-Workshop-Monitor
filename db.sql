-- --------------------------------------------------------
-- Host:                         172.22.2.22
-- Server version:               8.0.31 - MySQL Community Server - GPL
-- Server OS:                    Linux
-- HeidiSQL Version:             12.1.0.6557
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for workshop
DROP DATABASE IF EXISTS `workshop`;
CREATE DATABASE IF NOT EXISTS `workshop` /*!40100 DEFAULT CHARACTER SET utf8mb3 COLLATE utf8mb3_bin */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `workshop`;

-- Dumping structure for table workshop.guilds
DROP TABLE IF EXISTS `guilds`;
CREATE TABLE IF NOT EXISTS `guilds` (
  `GuildID` bigint NOT NULL,
  `GuildName` varchar(50) DEFAULT NULL,
  `ChID` bigint NOT NULL,
  `RID` bigint NOT NULL,
  `Count` int NOT NULL DEFAULT '20',
  PRIMARY KEY (`GuildID`),
  KEY `ChID` (`ChID`),
  KEY `RID` (`RID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf32;

-- Dumping data for table workshop.guilds: ~16 rows (approximately)
DELETE FROM `guilds`;

-- Dumping structure for table workshop.link
DROP TABLE IF EXISTS `link`;
CREATE TABLE IF NOT EXISTS `link` (
  `GuildID` bigint NOT NULL,
  `ModID` bigint NOT NULL,
  PRIMARY KEY (`GuildID`,`ModID`),
  KEY `FK_link_guilds` (`ModID`) USING BTREE,
  KEY `FK_link_mods` (`GuildID`) USING BTREE,
  CONSTRAINT `FK_link_guilds` FOREIGN KEY (`GuildID`) REFERENCES `guilds` (`GuildID`) ON DELETE CASCADE,
  CONSTRAINT `FK_link_mods` FOREIGN KEY (`ModID`) REFERENCES `mods` (`ModID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf32;

-- Dumping data for table workshop.link: ~1.323 rows (approximately)
DELETE FROM `link`;

-- Dumping structure for table workshop.mods
DROP TABLE IF EXISTS `mods`;
CREATE TABLE IF NOT EXISTS `mods` (
  `ModID` bigint NOT NULL DEFAULT '0',
  `ModName` varchar(99) DEFAULT NULL,
  `ModUpdated` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ModID`),
  KEY `ModUpdated` (`ModUpdated`)
) ENGINE=InnoDB DEFAULT CHARSET=utf32;

-- Dumping data for table workshop.mods: ~763 rows (approximately)
DELETE FROM `mods`;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

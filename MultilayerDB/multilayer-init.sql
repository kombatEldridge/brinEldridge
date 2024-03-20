USE `multilayer`;
DROP TABLE IF EXISTS `results`;
DROP TABLE IF EXISTS `conditions`;
CREATE TABLE `conditions` (
  `expID` int NOT NULL,
  `coreSize` double DEFAULT NULL,
  `sio2Size` double DEFAULT NULL,
  `shellSize` double DEFAULT NULL,
  `outerBoolean` text,
  PRIMARY KEY (`expID`)
);

CREATE TABLE `results` (
  `expID` int DEFAULT NULL,
  `lambda` double DEFAULT NULL,
  `qEXT` double DEFAULT NULL,
  `qSCA` double DEFAULT NULL,
  `qABS` double DEFAULT NULL,
  `eSQU` double DEFAULT NULL,
  `eSQUdev` double DEFAULT NULL,
  `eSQUQ1` double DEFAULT NULL,
  `eSQUQ3` double DEFAULT NULL,
  `eSQUavg` double DEFAULT NULL,
  `eSQUmin` double DEFAULT NULL,
  `eSQUmax` double DEFAULT NULL,
  KEY `expID` (`expID`),
  CONSTRAINT `results_ibfk_1` FOREIGN KEY (`expID`) REFERENCES `conditions` (`expID`)
);


CREATE TABLE `Place` (
  `Id` int(10) NOT NULL,
  `Name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `Latitude` double NOT NULL,
  `Longitude` double NOT NULL,
  `Country` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `Weather_Forecast` (
  `Id` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `PlaceId` int(10) NOT NULL,
  `Weather_TypeId` int(10) NOT NULL,
  `Wind_DirId` int(10) NOT NULL,
  `Date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Temperature` double NOT NULL,
  `Temperature_Max` double DEFAULT NULL,
  `Temperature_Min` double DEFAULT NULL,
  `Cloud_cover` double DEFAULT NULL,
  `Humidity_percent` double DEFAULT NULL,
  `Pressure_mb` double DEFAULT NULL,
  `Wind_speed` double DEFAULT NULL,
  `IsForecast` binary(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `Weather_Type` (
  `Id` int(10) NOT NULL,
  `Main` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `Description` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `Wind_Direction` (
  `Id` int(10) NOT NULL,
  `Direction` varchar(5) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

ALTER TABLE `Place`
  ADD PRIMARY KEY (`ID`);

ALTER TABLE `Weather_Forecast`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `FKWeather_Fo421185` (`PlaceId`),
  ADD KEY `FKWeather_Fo124478` (`Wind_DirId`),
  ADD KEY `FKWeather_Fo581646` (`WeatherTypeId`);

ALTER TABLE `Weather_Type`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `Main` (`Main`);

ALTER TABLE `Wind_Direction`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `Direction` (`Direction`);

ALTER TABLE `Place`
  MODIFY `Id` int(10) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Weather_Type`
  MODIFY `Id` int(10) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Wind_Direction`
  MODIFY `Id` int(10) NOT NULL AUTO_INCREMENT;

ALTER TABLE `Weather_Forecast`
  ADD CONSTRAINT `FKWeather_Fo124478` FOREIGN KEY (`Wind_DirId`) REFERENCES `Wind_Direction` (`Id`),
  ADD CONSTRAINT `FKWeather_Fo421185` FOREIGN KEY (`PlaceId`) REFERENCES `Place` (`Id`),
  ADD CONSTRAINT `FKWeather_Fo581646` FOREIGN KEY (`Weather_TypeId`) REFERENCES `Weather_Type` (`Id`);
COMMIT;

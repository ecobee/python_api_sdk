-- Run this crate to use a database token storage

CREATE TABLE `API_KEYS` (
  `identifier` varchar(12) NOT NULL,
  `access_token` varchar(32) DEFAULT NULL,
  `refresh_token` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`Identifier`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1

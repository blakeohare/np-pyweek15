-- phpMyAdmin SQL Dump
-- version 3.4.10.1
-- http://www.phpmyadmin.net
--
-- Host: blakepyweek.db
-- Generation Time: Sep 16, 2012 at 12:05 AM
-- Server version: 5.3.7
-- PHP Version: 5.3.10-nfsn2

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `pyweek15`
--

-- --------------------------------------------------------

--
-- Table structure for table `bad_start_location`
--

CREATE TABLE IF NOT EXISTS `bad_start_location` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sector` varchar(15) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=7 ;

-- --------------------------------------------------------

--
-- Table structure for table `bots`
--

CREATE TABLE IF NOT EXISTS `bots` (
  `user_id` int(11) NOT NULL,
  `type_a` int(11) NOT NULL,
  `type_b` int(11) NOT NULL,
  `type_c` int(11) NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `event`
--

CREATE TABLE IF NOT EXISTS `event` (
  `event_id` int(11) NOT NULL AUTO_INCREMENT,
  `sector_xy` varchar(15) NOT NULL,
  `client_token` varchar(50) NOT NULL,
  `user_id` int(11) NOT NULL,
  `data` text NOT NULL,
  PRIMARY KEY (`event_id`),
  UNIQUE KEY `client_token` (`client_token`),
  KEY `sector_xy` (`sector_xy`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

--
-- Table structure for table `heist`
--

CREATE TABLE IF NOT EXISTS `heist` (
  `user_id` int(11) NOT NULL,
  `attacked_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`,`attacked_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `research_unlocked`
--

CREATE TABLE IF NOT EXISTS `research_unlocked` (
  `user_id` int(11) NOT NULL,
  `type` varchar(30) NOT NULL,
  PRIMARY KEY (`user_id`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `resource_status`
--

CREATE TABLE IF NOT EXISTS `resource_status` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `last_poll` int(11) NOT NULL,
  `food` double NOT NULL,
  `water` double NOT NULL,
  `aluminum` double NOT NULL,
  `copper` double NOT NULL,
  `silicon` double NOT NULL,
  `oil` double NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

--
-- Table structure for table `structure`
--

CREATE TABLE IF NOT EXISTS `structure` (
  `structure_id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(20) NOT NULL,
  `sector_xy` varchar(15) NOT NULL,
  `loc_xy` varchar(15) NOT NULL,
  `user_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `data` varchar(100) NOT NULL,
  PRIMARY KEY (`structure_id`),
  KEY `sector_xy` (`sector_xy`,`loc_xy`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE IF NOT EXISTS `user` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `login_id` varchar(30) NOT NULL,
  `name` varchar(30) NOT NULL,
  `password` varchar(32) NOT NULL,
  `hq_sector` varchar(10) NOT NULL,
  `hq_loc` varchar(10) NOT NULL,
  `research` int(11) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `login_id` (`login_id`),
  UNIQUE KEY `hq_sector` (`hq_sector`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

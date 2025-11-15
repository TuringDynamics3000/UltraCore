ALTER TABLE `price_history` ADD `timestamp` timestamp NOT NULL;--> statement-breakpoint
ALTER TABLE `price_history` ADD `currency` varchar(10) DEFAULT 'USD' NOT NULL;--> statement-breakpoint
ALTER TABLE `price_history` ADD `interval` varchar(10) DEFAULT '1d' NOT NULL;
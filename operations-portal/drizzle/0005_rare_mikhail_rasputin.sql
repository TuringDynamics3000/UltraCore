CREATE TABLE `kafka_events` (
	`id` varchar(128) NOT NULL,
	`topic` varchar(255) NOT NULL,
	`key` varchar(255) NOT NULL,
	`value` json NOT NULL,
	`partition` int NOT NULL DEFAULT 0,
	`offset` bigint NOT NULL,
	`timestamp` timestamp NOT NULL,
	`created_at` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `kafka_events_id` PRIMARY KEY(`id`)
);

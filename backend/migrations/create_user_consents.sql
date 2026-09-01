-- Migration: create_user_consents.sql
-- Creates a table to store user consent records (dataConsent and gdprConsent)
-- Compatible with MySQL / TiDB

CREATE TABLE IF NOT EXISTS user_consents (
  id VARCHAR(64) PRIMARY KEY,
  user_id VARCHAR(64) NOT NULL,
  data_consent TINYINT(1) NOT NULL DEFAULT 0,
  gdpr_consent TINYINT(1) NOT NULL DEFAULT 0,
  consent_version VARCHAR(64),
  consent_ts DATETIME,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Alternative (JSON payload) if you prefer to store raw consent payloads:
-- CREATE TABLE IF NOT EXISTS user_consents_json (
--   id VARCHAR(64) PRIMARY KEY,
--   user_id VARCHAR(64) NOT NULL,
--   payload JSON,
--   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--   INDEX idx_user_id_json (user_id)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

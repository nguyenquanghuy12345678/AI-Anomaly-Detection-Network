-- Initialize TimescaleDB extension for time-series data
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create hypertable for network_traffic
SELECT create_hypertable('network_traffic', 'timestamp', if_not_exists => TRUE);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity);
CREATE INDEX IF NOT EXISTS idx_anomalies_status ON anomalies(status);
CREATE INDEX IF NOT EXISTS idx_anomalies_source_ip ON anomalies(source_ip);

CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);

CREATE INDEX IF NOT EXISTS idx_connections_timestamp ON connections(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_connections_source_ip ON connections(source_ip);
CREATE INDEX IF NOT EXISTS idx_connections_is_active ON connections(is_active);

CREATE INDEX IF NOT EXISTS idx_model_metrics_timestamp ON model_metrics(timestamp DESC);

-- Create data retention policies (keep data for 30 days)
SELECT add_retention_policy('network_traffic', INTERVAL '30 days', if_not_exists => TRUE);

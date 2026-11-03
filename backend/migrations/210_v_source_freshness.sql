-- Update v_source_freshness to separate never_synced from is_stale
CREATE OR REPLACE VIEW v_source_freshness AS
SELECT sh.*,
       (sh.last_success_at IS NOT NULL AND now() - sh.last_success_at > make_interval(secs => sh.ttl_seconds)) AS is_stale,
       (sh.last_success_at IS NULL) AS never_synced
FROM source_health sh;


#!/bin/bash
set -e
superset fab create-admin --username admin --firstname Admin --lastname User --email admin@example.com --password admin
superset db upgrade
superset init
sleep 5
superset set-database-uri --database-name siem --uri postgresql+psycopg2://airflow:airflow@postgres:5432/siem || true
superset import-datasources -p /app/superset-setup/dashboards/security_alerts.json || true
superset import-dashboards -p /app/superset-setup/dashboards/security_alerts_dashboard.json || true
#!/bin/bash
set -e
superset fab create-admin --username $SUPERSET_USERNAME --firstname Admin --lastname User --email admin@example.com --password $SUPERSET_PASSWORD
superset db upgrade
superset init
sleep 5
superset set-database-uri --database-name siem --uri postgresql+psycopg2://airflow:airflow@sink-postgres:5432/siem || true
superset import-datasources -p /app/superset-setup/siem_datasources.zip || true
superset import-dashboards -u admin -p /app/superset-setup/siem_dashboards.zip || true

/bin/sh -c /usr/bin/run-server.sh

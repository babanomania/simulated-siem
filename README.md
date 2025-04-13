# Simulated SIEM 🛡️
A fully automated real-time SIEM (Security Information & Event Management) stack using Kafka, Flink, Airflow, PostgreSQL, and Superset.

---

## 🚀 Features

- 🔁 Synthetic data generation via Airflow DAG
- 📡 Kafka streaming of network events
- ⚙️ Apache Flink for real-time anomaly detection (brute-force login detection)
- 🔗 Kafka Connect for PostgreSQL sink (no manual consumers needed)
- 📊 Apache Superset dashboard with auto-generated time series chart
- ⚡ Fully dockerized & zero-config bootstrapped

---

## 📦 Stack

| Component       | Role                         |
|----------------|------------------------------|
| Kafka + Zookeeper | Event streaming            |
| Kafka Connect  | Sink anomalies to Postgres   |
| Flink          | Detect login failure spikes  |
| Airflow        | Schedule synthetic log events|
| PostgreSQL     | Store detected anomalies     |
| Superset       | Visualize alerts dashboard   |

---

## 📂 Folder Structure

```
.
├── airflow-dags/                          # Airflow DAG for generating events
├── superset-setup/               # Superset init scripts + dashboards
│   ├── dashboards/
│   │   ├── security_alerts.json
│   │   └── security_alerts_dashboard.json
│   ├── init_superset.sh
│   └── superset_config.py
├── connect-plugins/              # PostgreSQL JDBC driver jar (add manually)
├── kafka-connect-setup/
│   └── postgres-sink.json        # Kafka Connect config for PostgreSQL
├── docker-compose.yml
```

---

## 🛠️ Setup Instructions

1. **Add JDBC driver**

   Download [PostgreSQL JDBC driver](https://jdbc.postgresql.org)  
   and place the `.jar` file into:

   ```bash
   ./connect-plugins/
   ```

2. **Start Everything**

   ```bash
   docker-compose up --build
   ```

3. **Visit the UI**

| Service       | URL                     | Login              |
|---------------|-------------------------|--------------------|
| Superset      | http://localhost:8088   | `admin / admin`    |
| Airflow       | http://localhost:8080   | `admin / admin`    |
| Kafka         | http://localhost:8081   |                    |
| Kafka Connect | http://localhost:8082   |                    |

---

## 📊 Dashboard Preview

Superset will automatically include:
- 📈 Time-series chart of alerts per hour
- 🔍 Queryable `security_alerts` dataset

---

## 🧪 Alert Logic

> Detected by Flink every 10 seconds

- 5+ `LOGIN_FAILED` events from same `source_ip` = 🚨 Brute-force alert

---

## 📜 License

MIT License

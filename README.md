SEPTA Real-Time Data Collector
==============================

Set up the database
-------------------

Run the following SQL:

```sql
CREATE TABLE measurements (route TEXT, data JSON, measured_at TIMESTAMP WITH TIME ZONE);
```
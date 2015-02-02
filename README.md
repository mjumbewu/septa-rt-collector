SEPTA Real-Time Data Collector
==============================

Set up the database
-------------------

Run the following SQL:

```sql
CREATE TABLE measurements (route TEXT, data JSON, measured_at TIMESTAMP WITH TIME ZONE);
```

Purpose
-------

Ideally, at some point, this can be used to collect a training set to build a model for fairly accurate bus arrival time prediction. Some useful guiding questions might be:

- How long does the bus take to complete it's route at a given time of day (maybe even mix in the weather from https://developer.forecast.io/)?
- What's the expected speed of the bus between any two stops?
- What's the expected time between any to points along a given route?

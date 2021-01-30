# Udacity Project: Data Lake

## Purpose
The music streaming company Sparkify wants to load their data from their data warehouse into a data lake.
Therefore an ETL pipeline is build which extract song data and user activity data from S3 to Spark.
After that the data are loaded back to S3 as spark parquet files.
The analytical goals are to further understand what their users most like.

## Database schema design and ETL pipeline
The database consists of one fact table "songplays" and four dimensional tables "users", "songs", "artists" and "time".
It is designed as star schema and processed for OLAP operations.
This makes it possible to perform further analysis.
With the ETL pipeline the data gets transformed to the target tables. 

## Files
1. etl.py -> Script to retrieve data into S3, transform the data into fact and dimensional tables and insert tables into S3
2. dl.cfg -> AWS keys

## Instructions
1. Create an AWS S3 bucket and add the login data to dl.cfg
2. Run etl.py in the terminal


import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format, dayofweek


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['AWS']['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS']['AWS_SECRET_ACCESS_KEY']

input_data = "s3a://udacity-dend/"

def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    # get filepath to song data file
    # song_data = 'data/song_data/A/A/A/TRAAAAW128F429D538.json'
    song_data = f'{input_data}/song_data/*/*/*/*.json'
    
    # read song data file
    df = spark.read.json(song_data)

    # extract columns to create songs table
    songs_table = df['song_id', 'title', 'artist_id', 'year', 'duration']
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.partitionBy('year', 'artist_id').mode('overwrite').parquet(os.path.join(output_data, 'songs'))

    # extract columns to create artists table
    artists_table = df['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']
    
    # write artists table to parquet files
    artists_table.write.mode('overwrite').parquet(os.path.join(output_data, 'artists'))


def process_log_data(spark, input_data, output_data):
    # get filepath to log data file
    # log_data = 'data/log-data/2018-11-01-events.json'
    log_data = '{input_data}/log_data/'

    # read log data file
    df = spark.read.json(log_data)
    
    # filter by actions for song plays
    df = df.filter(df.page=='NextSong')

    # extract columns for users table    
    users_table = df['userId', 'firstName', 'lastName', 'gender', 'level']
    
    # write users table to parquet files
    users_table.write.mode('overwrite').parquet(os.path.join(output_data, 'users'))

    # create timestamp column from original timestamp column
    get_timestamp = udf(lambda x:  datetime.fromtimestamp(x/1000).strftime('%Y-%m-%d %H:%M:%S'))
    df = df.withColumn("timestamp", get_timestamp(df.ts))
    
    # create datetime column from original timestamp column
    get_datetime = udf(lambda x: datetime.fromtimestamp(x/1000).strftime('%Y-%m-%d'))
    df = df.withColumn("datetime", get_datetime(df.ts))
    
    # extract columns to create time table
    time_table = df.select('timestamp').drop_duplicates() \
        .withColumn('hour', hour(col('timestamp'))) \
        .withColumn('day', dayofmonth(col('timestamp'))) \
        .withColumn('week', weekofyear(col('timestamp'))) \
        .withColumn('month', month(col('timestamp'))) \
        .withColumn('year', year(col('timestamp'))) \
        .withColumn('weekday', dayofweek(col('timestamp')))
    
    #time_table.show(5)
    
    # write time table to parquet files partitioned by year and month
    time_table.write.partitionBy('year', 'month').mode('overwrite').parquet(os.path.join(output_data, 'time'))

    # read in song data to use for songplays table
    song_df = spark.read\
                .format("parquet")\
                .option("basePath", os.path.join(output_data, "songs/"))\
                .load(os.path.join(output_data, "songs/*/*/"))

    # extract columns from joined song and log datasets to create songplays table 
    songplays_table = df.join(song_df, (df.song == song_df.title) & (df.artist == song_df.artist_id) & (df.length == song_df.duration), 'left_outer')\
            .select(
                df.timestamp,
                col("userId").alias('user_id'),
                df.level,
                song_df.song_id,
                song_df.artist_id,
                col("sessionId").alias("session_id"),
                df.location,
                col("useragent").alias("user_agent"),
                year('datetime').alias('year'),
                month('datetime').alias('month')
    )

    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.partitionBy('year', 'month').mode('overwrite').parquet(os.path.join(output_data, 'songplays'))


def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    #output_data = "output"
    output_data = "s3a://XXX/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()

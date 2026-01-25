# SparkSession is the primary entry point for working with Spark SQL and DataFrames.
# Without SparkSession, we cannot create DataFrames, read/write data, or
# perform Spark SQL queries.

from pyspark.sql import SparkSession

# This function creates (or gets) a SparkSession.
# app_name: str → Spark application name (string).
def create_spark_session(app_name: str):
    return (
        SparkSession.builder # builder is a factory object for setting Spark configuration before creating a session.
        .appName(app_name) # Spark app name to be shown in the Spark web UI.
        .config(
            "spark.jars.packages", # spark.jars.packages = configuration for automatic Maven dependency download.
            "org.postgresql:postgresql:42.6.0" # PostgreSQL JDBC driver version 42.6.0.
            )
        .getOrCreate()
        # If a SparkSession already exists, use that one.
        # If it doesn't exist, create a new one.
        # You don't create multiple SparkSessions in one JVM (Java Virtual Machine).
    )

# Explanation:

# Since Spark is JVM-based, all additional libraries are usually in JAR format.
# Spark cannot "talk" or connect directly to PostgreSQL without a JDBC driver.
# Dependency = additional library.
# Maven = Java library repo system.
# JDBC = Java Database Connectivity (Java API for connecting to databases).

# org.postgresql:postgresql
# This library:
# Translates Java/Spark commands into the PostgreSQL protocol.

# If we don't use:
# .config("spark.jars.packages", "org.postgresql:postgresql:42.6.0"),
# then we need to:
# - Download the PostgreSQL JDBC .jar file manually.
# - Copy it to the Spark container.
# - Add it to the Spark classpath.

# Behind the scenes:
# - Spark uses the JDBC API.
# - The JDBC API uses the PostgreSQL driver.
# - The driver sends queries to the database.

# So, this code:
# - Creates a SparkSession.
# - Names the application.
# - Adds a PostgreSQL JDBC driver.
# - Safe to call multiple times.
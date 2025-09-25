"""
Big Data Analytics Course - PySpark Configuration (Pip-based)
Compatible with Ubuntu 25.04 and Python 3.13.3
No full Spark installation required
"""
import findspark
import os

# Configure for pip-installed PySpark (no SPARK_HOME needed)
os.environ['PYSPARK_PYTHON'] = '/usr/bin/python3'
os.environ['PYSPARK_DRIVER_PYTHON'] = '/usr/bin/python3'

# Initialize findspark to find pip-installed PySpark
findspark.init()

print("🎓 Big Data Analytics Course Environment (PySpark-only)")
print(f"✅ Python: {os.environ.get('PYSPARK_PYTHON')}")
print("✅ PySpark ready for labs!")

# Test PySpark functionality
try:
    from pyspark import SparkContext
    print("✅ SparkContext import successful")
except ImportError as e:
    print(f"❌ PySpark import error: {e}")

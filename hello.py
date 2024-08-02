import pymysql as MySQLdb

# Open database connection
db = MySQLdb.Connection(host='localhost',user='root',password='Sunny.1218',port=3306,database='test')

# prepare a cursor object using cursor() method
cursor = db.cursor()

# execute SQL query using execute() method.
cursor.execute("show tables")

# Fetch a single row using fetchone() method.
data = cursor.fetchall()
print (data)

# disconnect from server
db.close()
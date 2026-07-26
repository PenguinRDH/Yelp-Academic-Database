import json
from pickle import TRUE
import psycopg2

def cleanStr4SQL(s):
    return s.replace("'","`").replace("\n"," ")

def escape_sql(value):
    return value.replace("'", "''")

def getAttributes(attributes):
    L = []
    for (attribute, value) in list(attributes.items()):
        if isinstance(value, dict):
            L += getAttributes(value)
        elif value != False and value != None:
            L.append((attribute,value))
    return L

def createBusinessSQLFile():
    #reading the JSON file
    print("Parsing businesses...")
    with open('.\yelp_business.JSON','r') as f:   
        outfile =  open('./yelp_insertstatements.sql', 'w')  
        line = f.readline()
        count_line = 0

        while line:
            data = json.loads(line)
            sql_str = "INSERT INTO business (business_id, name, address,state,city,zipcode,stars,review_count,numCheckins) " \
                      "VALUES ('" + cleanStr4SQL(data['business_id']) + "','" + cleanStr4SQL(data["name"]) + "','" + cleanStr4SQL(data["address"]) + "','" + \
                      cleanStr4SQL(data["state"]) + "','" + cleanStr4SQL(data["city"]) + "','" + cleanStr4SQL(data["postal_code"]) + "'," + str(data["stars"]) + "," + str(data["review_count"]) + ",0);\n"
            
            outfile.write(sql_str)

            line = f.readline()
            count_line +=1


    print(count_line)
    outfile.close() 
    f.close()

def createCheckinSQLFile():
    print("Parsing checkins...")
    #reading the JSON file
    with open('./yelp_checkin.JSON','r') as f:  # Assumes that the data files are available in the current directory. If not, you should set the path for the yelp data files.
        outfile =  open('./yelp_insertstatements.sql', 'a')
        line = f.readline()
        count_line = 0
        
        while line:
            data = json.loads(line)
            business_id = data['business_id']
            for (dayofweek,time) in data['time'].items():
                for (hour,count) in time.items():
                    hourInt = hour.split(':')[0]
                    sql_str = "INSERT INTO Checkin (business_id, day_of_week, hour, count)" + " VALUES (\'" + business_id + "\',\'" + dayofweek + "\'," + hourInt + "," + str(count) + ");\n"
                    outfile.write(sql_str)
            line = f.readline()
            count_line +=1
        print(count_line)
    outfile.close()
    f.close()

def createBusinessCategoryAttributeSQLFiles():
    print("Parsing categories and attributes...")
    with open('./yelp_business.JSON','r') as f:
        outfile =  open('./yelp_insertstatements.sql', 'a')
        delete = open('./yelp_attributesCategories.sql', 'w')
        line = f.readline()
        count_line = 0
        #read each JSON abject and extract data
        while line:
            data = json.loads(line)
            business = data['business_id'] #business id
            
            # process business categories
            for category in data['categories']:
                category = escape_sql(category)
                category_str = "'" + business + "','" + category + "'"
                sql_str = "INSERT INTO belongsto (business_id, category_name) VALUES (" + category_str + ");\n"
                delete.write(sql_str)
                outfile.write(sql_str)
        
            #process business attributes
            for (attr,value) in getAttributes(data['attributes']):
                attr_str = "'" + business + "','" + str(attr) + "'"
                sql_str = "INSERT INTO hasattribute (business_id, attribute_name) VALUES (" + attr_str + ");\n"
                delete.write(sql_str)
                outfile.write(sql_str)

            line = f.readline()
            count_line +=1
    print(count_line)
    outfile.close()
    delete.close()
    f.close()

def createReviewSQLFile():
    print("Parsing reviews...")
    #reading the JSON file
    with open('./yelp_review.JSON','r') as f:
        outfile =  open('./yelp_insertstatements.sql', 'a')
        line = f.readline()
        count_line = 0
        while line:
            data = json.loads(line)
            review_str = "'" + data['review_id'] + "'," + \
                         str(data['stars']) + "," + \
                        "'" + cleanStr4SQL(data['text']) + "'," +  \
                         "'" + data['date'] + "'," + \
                         str(data['useful'])
            sql_str = "INSERT INTO REVIEW (review_id, stars, text, date, useful) VALUES (" + review_str+ ");\n"
            outfile.write(sql_str)
            sql_str = "INSERT INTO receives (review_id, business_id) VALUES ('" + data['review_id'] + "','" + data['business_id'] + "');\n"
            outfile.write(sql_str)

            line = f.readline()
            count_line +=1

    print(count_line)
    outfile.close()
    f.close()

createBusinessSQLFile()
createCheckinSQLFile()
createBusinessCategoryAttributeSQLFiles()
createReviewSQLFile()
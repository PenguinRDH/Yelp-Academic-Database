import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QTableWidget,QTableWidgetItem,QVBoxLayout
from PyQt6 import uic, QtCore
from PyQt6.QtGui import QIcon, QPixmap, QAction
import psycopg2

qtCreatorFile = "milestone3App.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class milestone2(QMainWindow):
    style = "::section {background-color: #f3f3f3; }"
    DATABASE = "Milestone2DB"
    PASSCODE = "gardner"
    def __init__(self):
        super(milestone2, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.load_state_list()
        self.ui.state_list.currentTextChanged.connect(self.state_changed)
        self.ui.city_list.itemSelectionChanged.connect(self.city_changed)
        self.ui.zipcode_list.itemSelectionChanged.connect(self.zipcode_changed)
        self.ui.search_button.clicked.connect(self.search_categories)
        self.ui.refresh_button.clicked.connect(self.refresh_business)
        self.ui.popular_successful_button.clicked.connect(self.search_popular_sucessful_business_button)
        self.ui.update_button.clicked.connect(self.update_business_statistics)

    def execute_query(self, sql_str):
        try:
            conn = psycopg2.connect("dbname='" + self.DATABASE + "' user='postgres' host='localhost' password='" + self.PASSCODE + "'")
        except:
            print("Unable to connect to the database.")
        cur = conn.cursor()
        cur.execute(sql_str)
        conn.commit()
        result = cur.fetchall()
        conn.close()
        return result

    def clear_zipcode_statistics(self):
        self.ui.median_income.setText("")
        self.ui.average_income.setText("")
        self.ui.total_population.setText("")
        self.ui.number_of_business.setText("")

    def update_category_table(self, sql_str):
        results = self.execute_query(sql_str)
        self.ui.category_table.horizontalHeader().setStyleSheet(self.style) 
        self.ui.category_table.setColumnCount(len(results[0]))
        self.ui.category_table.setRowCount(len(results))           
        self.ui.category_table.setHorizontalHeaderLabels(['# of\nBusinesses', 'Category'])
                
        currentRowCount = 0
        for row in results:
            for colCount in range(0,len(results[0])):
                self.ui.category_table.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
            currentRowCount += 1
        self.ui.category_table.resizeColumnsToContents() 

    def load_businesses(self, sql_str):
        for i in reversed(range(self.ui.business_list.rowCount())):
            self.ui.business_list.removeRow(i)
        try:         
            results = self.execute_query(sql_str)

            self.ui.business_list.horizontalHeader().setStyleSheet(self.style) 
            self.ui.business_list.setColumnCount(len(results[0]))
            self.ui.business_list.setRowCount(len(results))           
            self.ui.business_list.setHorizontalHeaderLabels(['Business Name',  'City', 'Address', 'Business\nRating', 'Stars', '# of\nReviews', 'Total\nCheck ins'])
            self.ui.business_list.resizeColumnsToContents()
            self.ui.business_list.setColumnWidth(0,150)  
            self.ui.business_list.setColumnWidth(1,75)  
            self.ui.business_list.setColumnWidth(2,150)          
            currentRowCount = 0
            for row in results:
                for colCount in range(0,len(results[0])):
                    self.ui.business_list.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                currentRowCount += 1
        except Exception as e:
            print("Error in updating businesses table - ", e)

    def update_business_statistics(self):
        sql_str = "UPDATE business b\
                    SET numcheckins = c.total\
                    FROM (SELECT business_id, SUM(COUNT) AS total FROM checkin\
                            GROUP BY business_id) c\
                    WHERE b.business_id = c.business_id;\
                    UPDATE business b\
                    SET review_count = r.review_count \
                    FROM (SELECT COUNT(*) AS review_count, business_id FROM review\
                            NATURAL JOIN receives\
                            GROUP BY business_id) r\
                    WHERE b.business_id = r.business_id;\
                    UPDATE business b\
                    SET reviewrating = (sum.starsum / b.review_count)\
                    FROM (SELECT SUM(stars) as starsum, business_id FROM review\
                        NATURAL JOIN receives\
                        GROUP BY business_id) sum\
                    WHERE b.business_id = sum.business_id AND b.review_count > 0;"
        try:
            conn = psycopg2.connect("dbname='" + self.DATABASE + "' user='postgres' host='localhost' password='" + self.PASSCODE + "'")
        except:
            print("Unable to connect to the database.")
        cur = conn.cursor()
        cur.execute(sql_str)
        conn.commit()
        conn.close()
        print("updated business stats")

    def load_state_list(self):
        self.ui.state_list.clear()
        sql_str = "SELECT distinct state From business ORDER BY state;"
        try:
            results = self.execute_query(sql_str)
            for row in results:
                self.ui.state_list.addItem(row[0])
        except Exception as e:
            print("can't load state list", e)
        self.ui.state_list.setCurrentIndex(-1)
        self.ui.state_list.clearEditText()

    def state_changed(self):
        state = self.ui.state_list.currentText()
        if (self.ui.state_list.currentIndex() == -1):
            return
        sql_str = "SELECT DISTINCT city FROM business WHERE state = '" + state + "' ORDER BY city;"
        self.clear_zipcode_statistics()
        try:
            self.ui.city_list.clear()
            results = self.execute_query(sql_str)
            for row in results:
                self.ui.city_list.addItem(row[0])
            sql_str = "SELECT COUNT(*) AS business_count, c.category_name AS category FROM belongsto c\
                    INNER JOIN business b ON c.business_id = b.business_id\
                    WHERE state = '" + state + "'\
                    GROUP BY category_name ORDER BY count(*) DESC;"
            self.update_category_table(sql_str)
        except Exception as e:
            print("stateChanged() error- should be listing cities in the state", e)

        sql_str = "SELECT name, city, address, reviewrating, stars, review_count, numcheckins FROM business WHERE state = '" + state + "' ORDER BY name;"
        self.load_businesses(sql_str)

    def city_changed(self):
        try:
            city = self.ui.city_list.selectedItems()[0].text()
        except Exception as e:
            print("cityChanged() error - city not selected", e)
            return
        state = self.ui.state_list.currentText()
        self.clear_zipcode_statistics()
        if (city == "" or state == ""):
            return
        zipcode_str = "SELECT DISTINCT zipcode FROM business WHERE city = '" + city + "' AND state = '" + state + "' ORDER BY zipcode;"
        try:
            self.ui.zipcode_list.clear()
            results = self.execute_query(zipcode_str)
            for row in results:
                self.ui.zipcode_list.addItem(row[0])    
        except Exception as e:
            print("cityChanged() error- should be listing zips in the city - ", e)

        try: 
            sql_str = "SELECT count(*) AS business_count, c.category_name AS category FROM belongsto c\
                    INNER JOIN business b ON c.business_id = b.business_id\
                    WHERE state = '" + state + "' AND city = '" +city+"' \
                    GROUP BY category_name ORDER BY count(*) DESC;"
            self.update_category_table(sql_str)
        except Exception as e:
            print("Failed to update category table with city info - ", e)

        sql_str = "SELECT name, city, address, reviewrating, stars, review_count, numcheckins FROM business WHERE state = '" + state +"' AND city = '" + city + "' ORDER BY name;"
        self.load_businesses(sql_str)

    def zipcode_changed(self):
        try:
            zipcode = self.ui.zipcode_list.selectedItems()[0].text()
            city = self.ui.city_list.selectedItems()[0].text()
        except Exception as e:
            print("zipcodeChanged() error - zipcode not selected",e )
            return
        state = self.ui.state_list.currentText()
        if (zipcode == "" or state == "" or city == ""):
            return
       
        try:         
            results = self.execute_query("SELECT medianincome, meanincome, population, count(business_id) \
                                        from business, zipcode WHERE business.zipcode = zipcode.code AND \
                                        zipcode.code = '" + zipcode + "' GROUP BY zipcode.code")
            self.ui.median_income.setText(str(results[0][0]))
            self.ui.average_income.setText(str(results[0][1]))
            self.ui.total_population.setText(str(results[0][2]))
            self.ui.number_of_business.setText(str(results[0][3]))
        except Exception as e:
            print("zipcodeChanged() error - second try except block", e)
        ## counting number of businesses in each category 
        sql_str = "SELECT COUNT(*) AS business_count, c.category_name AS category FROM belongsto c\
                    INNER JOIN business b ON c.business_id = b.business_id\
                    WHERE zipcode = '" + zipcode + "'\
                    GROUP BY category_name ORDER BY count(*) DESC;"
        try:        
            self.update_category_table(sql_str)
            
           
        except Exception as e:
            print("zipcodeChanged() error - second try except block - top category list:", e)

        sql_str = "SELECT name, city, address, reviewrating, stars, review_count, numcheckins FROM business WHERE zipcode = '" + zipcode + "' ORDER BY name;"
        self.load_businesses(sql_str)
        category_sql = "SELECT category_name FROM business b INNER JOIN belongsto bt ON bt.business_id = b.business_id\
                        WHERE zipcode = '" + zipcode + "' GROUP BY category_name ORDER BY category_name;"
        try:
            self.ui.category_selection_list.clear()
            results = self.execute_query(category_sql)
            for row in results:
                self.ui.category_selection_list.addItem(row[0])    
        except Exception as e:
            print("error filling out category selection list", e)

    def search_categories(self):
        try:
            zipcode = self.ui.zipcode_list.selectedItems()[0].text()
            category = self.ui.category_selection_list.selectedItems()[0].text()
        except Exception as e:
            print("error from search button", e)
            return
        if (zipcode == '' or category == ''):
            return
        sql_str = "SELECT name, city, address, reviewrating, stars, review_count, numcheckins FROM business b\
             INNER JOIN belongsto bt ON bt.business_id = b.business_id WHERE zipcode = '" + zipcode +"' AND\
             category_name = '" +category+ "' ORDER BY name;"
        self.load_businesses(sql_str)

    def refresh_business(self):
        try:
            zipcode = self.ui.zipcode_list.selectedItems()[0].text()
        except Exception as e:
            print("zipcode not selected",e )
            return
        if (zipcode == ""):
            return

        sql_str = "SELECT name, city, address, reviewrating, stars, review_count, numcheckins FROM business WHERE zipcode = '" + zipcode + "' ORDER BY name;"
        self.load_businesses(sql_str)
        category_sql = "SELECT category_name FROM business b INNER JOIN belongsto bt ON bt.business_id = b.business_id\
                        WHERE zipcode = '" + zipcode + "' GROUP BY category_name;"
        try:
            self.ui.category_selection_list.clear()
            results = self.execute_query(category_sql)
            for row in results:
                self.ui.category_selection_list.addItem(row[0])    
        except Exception as e:
            print("error filling out category selection list", e)

    def get_popular_businesses(self, sql_str):
        for i in reversed(range(self.ui.popular_business_list.rowCount())):
            self.ui.popular_business_list.removeRow(i)
        try:         
            results = self.execute_query(sql_str)

            self.ui.popular_business_list.horizontalHeader().setStyleSheet(self.style) 
            self.ui.popular_business_list.setColumnCount(len(results[0])-1)
            self.ui.popular_business_list.setRowCount(len(results))           
            self.ui.popular_business_list.setHorizontalHeaderLabels(['Business Name', 'Business\nRating', 'Stars', '# of\nReviews', 'Total\nCheck ins'])
            self.ui.popular_business_list.resizeColumnsToContents()
            self.ui.popular_business_list.setColumnWidth(0,150)          
            currentRowCount = 0
            for row in results:
                for colCount in range(0,len(results[0])-1):
                    self.ui.popular_business_list.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                currentRowCount += 1
        except Exception as e:
            print("Error in updating popular businesses table - ", e)

    def get_successful_businesses(self, sql_str):
        for i in reversed(range(self.ui.successful_business_list.rowCount())):
            self.ui.successful_business_list.removeRow(i)
        try:         
            results = self.execute_query(sql_str)

            self.ui.successful_business_list.horizontalHeader().setStyleSheet(self.style) 
            self.ui.successful_business_list.setColumnCount(len(results[0]))
            self.ui.successful_business_list.setRowCount(len(results))           
            self.ui.successful_business_list.setHorizontalHeaderLabels(['Business Name', 'Business\nRating', 'Stars', '# of\nReviews', 'Total\nCheck ins'])
            self.ui.successful_business_list.resizeColumnsToContents()
            self.ui.successful_business_list.setColumnWidth(0,150)          
            currentRowCount = 0
            for row in results:
                for colCount in range(0,len(results[0])):
                    self.ui.successful_business_list.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                currentRowCount += 1
        except Exception as e:
            print("Error in updating successful businesses table - ", e)


    def search_popular_sucessful_business_button(self):
        try:
            zipcode = self.ui.zipcode_list.selectedItems()[0].text() 
            sql_str = "SELECT name, reviewrating, stars, review_count, numcheckins, reviewrating*review_count AS popularity_rating FROM business b\
                    INNER JOIN zipcodecategorystatistics z ON z.zipcode = b.zipcode\
                    INNER JOIN belongsto bt ON b.business_id = bt.business_id\
                    WHERE z.zipcode = '" + zipcode + "' AND numcheckins > average_checkins*1.50\
                    GROUP BY name, stars, reviewrating, review_count, numcheckins, popularity_rating\
                    ORDER BY popularity_rating desc;"
            self.get_popular_businesses(sql_str)    
            sql_str = "SELECT name, reviewrating, stars, review_count, numcheckins FROM\
                    (SELECT name, reviewrating, stars, review_count, numcheckins, b.business_id FROM business b\
                        INNER JOIN zipcodecategorystatistics z ON z.zipcode = b.zipcode\
                        INNER JOIN belongsto bt ON b.business_id = bt.business_id\
                        WHERE z.zipcode = '" + zipcode + "' AND numcheckins > average_checkins) p\
                    INNER JOIN \
                    (SELECT business.business_id\
                        FROM review INNER JOIN receives ON receives.review_id = review.review_id\
                        INNER JOIN business ON business.business_id = receives.business_id\
                        WHERE zipcode = '" + zipcode + "'\
                        GROUP BY business.business_id\
                        HAVING COUNT(DISTINCT extract(year from date))/(MAX(extract(year from date)) - MIN(extract(year from date)) + 1) = 1\
                        AND MAX(extract(year from date)) - MIN(extract(year from date)) + 1> 5) l\
                    ON l.business_id = p.business_id\
                    GROUP BY name, reviewrating, stars, review_count, numcheckins\
                    ORDER BY numcheckins DESC;"
            self.get_successful_businesses(sql_str)
        except Exception as e:
            print("zipcode not selected - ", e)
       


## running app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = milestone2()
    window.show()
    sys.exit(app.exec())
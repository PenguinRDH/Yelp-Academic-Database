import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QTableWidget,QTableWidgetItem,QVBoxLayout
from PyQt6 import uic, QtCore
from PyQt6.QtGui import QIcon, QPixmap, QAction
import psycopg2

qtCreatorFile = "milestone1App.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class milestone1(QMainWindow):
    def __init__(self):
        super(milestone1, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.loadStateList()
        self.ui.stateList.currentTextChanged.connect(self.stateChanged)
        self.ui.cityList.itemSelectionChanged.connect(self.cityChanged)
        self.ui.businessNameSearch.textChanged.connect(self.getBusinessNames)
        self.ui.searchResults.itemSelectionChanged.connect(self.displayBusinessCity)

    def executeQuery(self, sql_str):
        try:
            conn = psycopg2.connect("dbname='Milestone1DB' user='postgres' host='localhost' password='DB_PASSWORD'")
        except:
            print("Unable to connect to the database.")
        cur = conn.cursor()
        cur.execute(sql_str)
        conn.commit()
        result = cur.fetchall()
        conn.close()
        return result


    def loadStateList(self):
        self.ui.stateList.clear()
        sql_str = "SELECT distinct state From business ORDER BY state;"
        try:
            results = self.executeQuery(sql_str)
            for row in results:
                self.ui.stateList.addItem(row[0])
        except:
            print("oof")
        self.ui.stateList.setCurrentIndex(-1)
        self.ui.stateList.clearEditText()

    def stateChanged(self):
        state = self.ui.stateList.currentText()
        if (self.ui.stateList.currentIndex() == -1):
            return
        sql_str = "SELECT distinct city FROM business WHERE state = '" + state + "' ORDER BY city;"
        ##print(sql_str)
        try:
            self.ui.cityList.clear()
            results = self.executeQuery(sql_str)
            for row in results:
                self.ui.cityList.addItem(row[0])
            ##print(results)
        except:
            print("stateChanged() error- should be listing cities in the state")

        for i in reversed(range(self.ui.businessList.rowCount())):
            self.ui.businessList.removeRow(i)
        sql_str = "SELECT name, city, state FROM business WHERE state = '" + state +"' ORDER BY name;"
        try:         
            results = self.executeQuery(sql_str)
            style = "::section {background-color: #f3f3f3; }"
            
            self.ui.businessList.horizontalHeader().setStyleSheet(style) 
            self.ui.businessList.setColumnCount(len(results[0]))
            self.ui.businessList.setRowCount(len(results))           
            self.ui.businessList.setHorizontalHeaderLabels(['Business Name', 'City', 'State'])
            self.ui.businessList.resizeColumnsToContents()
            self.ui.businessList.setColumnWidth(0,235)
            self.ui.businessList.setColumnWidth(1,90)
            self.ui.businessList.setColumnWidth(2,50)           
            currentRowCount = 0
            for row in results:
                for colCount in range(0,len(results[0])):
                    self.ui.businessList.setItem(currentRowCount, colCount, QTableWidgetItem(row[colCount]))
                currentRowCount += 1
            print(results)
        except: 
            print("stateChanged() error - second try except block")

    def cityChanged(self):
        try:
            city = self.ui.cityList.selectedItems()[0].text()
        except:
            print("cityChanged() error - city not selected")
            return
        state = self.ui.stateList.currentText()
        if (city == "" or state == ""):
            return
        sql_str = "SELECT name, city, state FROM business WHERE city = '" + city + "' AND state = '" + state + "' ORDER BY name;"
        ##print(sql_str)
        for i in reversed(range(self.ui.businessList.rowCount())):
            self.ui.businessList.removeRow(i)
        try:         
            results = self.executeQuery(sql_str)
            style = "::section {background-color: #f3f3f3; }"
            
            self.ui.businessList.horizontalHeader().setStyleSheet(style) 
            self.ui.businessList.setColumnCount(len(results[0]))
            self.ui.businessList.setRowCount(len(results))           
            self.ui.businessList.setHorizontalHeaderLabels(['Business Name', 'City', 'State'])
            self.ui.businessList.resizeColumnsToContents()
            self.ui.businessList.setColumnWidth(0,235)
            self.ui.businessList.setColumnWidth(1,90)
            self.ui.businessList.setColumnWidth(2,50)           
            currentRowCount = 0
            for row in results:
                for colCount in range(0,len(results[0])):
                    self.ui.businessList.setItem(currentRowCount, colCount, QTableWidgetItem(row[colCount]))
                currentRowCount += 1
            ##print(results)
        except: 
            print("cityChanged() error - first try except block")

    def getBusinessNames(self):
        businessName = self.ui.businessNameSearch.text()
        sql_str = "SELECT name FROM business WHERE name LIKE '%"+ businessName +"%' ORDER BY name;"
        try:         
            results = self.executeQuery(sql_str)
            style = "::section {background-color: #f3f3f3; }"
            self.ui.searchResults.clear()
            for row in results:
                self.ui.searchResults.addItem(row[0])
        except: 
            print("getBusinessNames() error - first try except block")

    def displayBusinessCity(self):
        if (len(self.ui.searchResults.selectedItems()) > 0):
            businessName = self.ui.searchResults.selectedItems()[0].text()
            sql_str = "SELECT city FROM business WHERE name = '" + businessName + "';"
            try:
                results = self.executeQuery(sql_str)
                print(results)
                self.ui.searchResultCity.setText(results[0][0])
            except:
                print("displayBusinessCity() error - first try except block")
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = milestone1()
    window.show()
    sys.exit(app.exec())

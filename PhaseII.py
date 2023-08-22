from pandas import DataFrame
import plotly.express as px
import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
import numpy as np
import json
import pandas as pd

laborstats_data = json.load(open("HTMLLaborStatistics.json", 'r'))
notinlaborforce = laborstats_data['Not in Labor Force Percent']
employed = laborstats_data['Employed Percent']
unemployment = laborstats_data['Unemployment Percent']

educ_data = json.load(open("EducationAttainment.json", 'r'))
lessthan9th = educ_data['Less Than 9th Percent']
highschool = educ_data['High School Graduate Percent']
bachelor = educ_data['Bachelor Degree Percent']

with open("economic_data.json") as econ:
    econ_dataframe = pd.read_json(econ)
    econ_dataframe = econ_dataframe.transpose()
    econ_dataframe.sort_index(inplace = True, axis = 0)
    #print(econ_dataframe.loc["Mcintosh", :])
    POP = list(econ_dataframe[" Population (Persons)  (Number Of Persons)"])
    PCNE = list(econ_dataframe[" Per Capita Net Earnings  (Dollars)"])
    NEBPR = list(econ_dataframe[" Net Earnings By Place Of Residence (Thousands Of Dollars)"])
    PCPI = list(econ_dataframe[" Per Capita Personal Income  (Dollars)"])
    PCPCTR = list(econ_dataframe[" Per Capita Personal Current Transfer Receipts  (Dollars)"])
    PCIMB = list(econ_dataframe["  Per Capita Income Maintenance Benefits  (Dollars)"])
    PCUIC = list(econ_dataframe["  Per Capita Unemployment Insurance Compensation  (Dollars)"])
    PCRO = list(econ_dataframe["  Per Capita Retirement And Other  (Dollars)"])

opioiddata = json.load(open("opioid_dat.json", 'r'))
opioid = {}
for key in opioiddata:
    opioid[key] = opioiddata[key]['total_claims']

popdata = json.load(open("economic_data.json", 'r'))
pop = {}
counties = []

for key in popdata:
    pop[key] = popdata[key][' Population (Persons)  (Number Of Persons)']
    counties.append(key)
counties.sort()
opioidrate = []
for key in counties:
    if opioid[key] and pop[key]:
        opioidrate.append(opioid[key]/pop[key])
    else:
        opioidrate.append(0)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scatter Graph Generator")

        self.label1 = QLabel("X-Axis:")
        self.label1.setAlignment(QtCore.Qt.AlignCenter)
        self.label2 = QLabel("Y-Axis:")
        self.label2.setAlignment(QtCore.Qt.AlignCenter)

        self.cb = QComboBox()
        self.cb.addItems(["","Unemployment Rate", "Not in Labor Force Rate", "Employed Rate", "Percentage with Less than 9th Grade Education", "Percentage that Graduated Highschool"])
        self.cb.addItems(["Percentage with Bachelor's Degree", "Per Capita Net Earnings (Dollars)", "Net Earnings By Place Of Residence (Thousands Of Dollars)", "Per Capita Personal Income (Dollars)"])
        self.cb.addItems(["Per Capita Personal Current Transfer Receipts (Dollars)", "Per Capita Income Maintenance Benefits (Dollars)", "Per Capita Unemployment Insurance Compensation (Dollars)", "Per Capita Retirement And Other (Dollars)"])
        self.cb.activated[str].connect(self.generate)

        self.cb1 = QComboBox()
        self.cb1.addItems(["", "Opioid Prescription Rate                                                                     "])
        self.cb1.activated[str].connect(self.generate)

        self.button = QtWidgets.QPushButton('Generate Graph!', self)
        self.browser = QtWebEngineWidgets.QWebEngineView(self)
        self.infobutton = QPushButton("Instructions")


        layout = QVBoxLayout()

        vlayout = QVBoxLayout()
        vlayout.addWidget(self.button, alignment=QtCore.Qt.AlignHCenter)
        vlayout.addWidget(self.browser)
        self.button.clicked.connect(self.creategraph)
        self.resize(1000,800)

        hbox = QHBoxLayout()
        hbox.addWidget(self.label1)
        hbox.addWidget(self.cb)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.label2)
        hbox2.addWidget(self.cb1)

        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.infobutton)
        self.infobutton.clicked.connect(self.info)

        layout.addLayout(hbox4)
        layout.addLayout(hbox)
        layout.addLayout(hbox2)
        layout.addLayout(vlayout)

        self.setLayout(layout)

    def generate(self):
        if self.cb.currentText() and self.cb1.currentText():
            self.button.setEnabled(True)
            self.button.clicked.connect(self.creategraph)
        else:
            pass

    def creategraph(self):
        if self.cb.currentText() == "" or self.cb1.currentText()=="":
            self.button.setEnabled(False)
            pass
        elif self.cb.currentText() == "Employed Rate":
            df = pd.DataFrame({"opioidrate":opioidrate, "employed":employed, 'counties':counties},index=counties)
            df = df[df["opioidrate"] != 0]

            a = np.array(df['employed'])
            b = np.array(df['opioidrate'])
            c = np.array(df['counties'])

            df = px.data.tips()
            fig = px.scatter(x = a, y = b, trendline="ols", title="<b>Employed Percentage v.s. # of Prescriptions Per Person</b>", \
                labels={"x": "Employed Percentage","y": "# of Prescriptions Per Person"}, hover_name=c, opacity=0.7)
            fig.data[1].update(line_color='red')
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        elif self.cb.currentText() == "Unemployment Rate":
            df = pd.DataFrame({"opioidrate":opioidrate, "unemployment":unemployment, 'counties':counties},index=counties)
            df = df[df["opioidrate"] != 0]

            a = np.array(df['unemployment'])
            b = np.array(df['opioidrate'])
            c = np.array(df['counties'])

            df = px.data.tips()
            fig = px.scatter(x = a, y = b, trendline="ols", title="<b>Unemployment Rate (%) v.s. # of Prescriptions Per Person</b>", \
                labels={"x": "Unemployment Rate (%)","y": "# of Prescriptions Per Person"}, hover_name=c, opacity=0.7)
            fig.data[1].update(line_color='red')
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        elif self.cb.currentText() == "Not in Labor Force Rate":
            df = pd.DataFrame({"opioidrate":opioidrate, "notinlaborforce":notinlaborforce, 'counties':counties},index=counties)
            df = df[df["opioidrate"] != 0]

            a = np.array(df['notinlaborforce'])
            b = np.array(df['opioidrate'])
            c = np.array(df['counties'])

            df = px.data.tips()
            fig = px.scatter(x = a, y = b, trendline="ols", title="<b>Not in Labor Force Rate (%) v.s. # of Prescriptions Per Person</b>", \
                labels={"x": "Not in Labor Force Rate (%)","y": "# of Prescriptions Per Person"}, hover_name=c, opacity=0.7)
            fig.data[1].update(line_color='red')
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        elif self.cb.currentText() == "Percentage with Less than 9th Grade Education":
            df = pd.DataFrame({"opioidrate":opioidrate, "lessthan9th":lessthan9th, 'counties':counties},index=counties)
            df = df[df["opioidrate"] != 0]

            a = np.array(df['lessthan9th'])
            b = np.array(df['opioidrate'])
            c = np.array(df['counties'])

            df = px.data.tips()
            fig = px.scatter(x = a, y = b, trendline="ols", title="<b>Percentage with Less than 9th Grade Education (%) v.s. # of Prescriptions Per Person</b>", \
                labels={"x": "Percentage with Less than 9th Grade Education (%)","y": "# of Prescriptions Per Person"}, hover_name=c, opacity=0.7)
            fig.data[1].update(line_color='red')
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        elif self.cb.currentText() == "Percentage that Graduated Highschool":
            df = pd.DataFrame({"opioidrate":opioidrate, "highschool":highschool, 'counties':counties},index=counties)
            df = df[df["opioidrate"] != 0]

            a = np.array(df['highschool'])
            b = np.array(df['opioidrate'])
            c = np.array(df['counties'])

            df = px.data.tips()
            fig = px.scatter(x = a, y = b, trendline="ols", title="<b>Percentage that Graduated Highschool (%) v.s. # of Prescriptions Per Person</b>", \
                labels={"x": "Percentage that Graduated Highschool (%)","y": "# of Prescriptions Per Person"}, hover_name=c, opacity=0.7)
            fig.data[1].update(line_color='red')
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        elif self.cb.currentText() == "Percentage with Bachelor's Degree":
            df = pd.DataFrame({"opioidrate":opioidrate, "bachelor":bachelor, 'counties':counties},index=counties)
            df = df[df["opioidrate"] != 0]

            a = np.array(df['bachelor'])
            b = np.array(df['opioidrate'])
            c = np.array(df['counties'])

            df = px.data.tips()
            fig = px.scatter(x = a, y = b, trendline="ols", title="<b>Percentage with Bachelor's Degree (%) v.s. # of Prescriptions Per Person</b>", \
                labels={"x": "Percentage with Bachelor's Degree (%)","y": "# of Prescriptions Per Person"}, hover_name=c, opacity=0.7)
            fig.data[1].update(line_color='red')
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        elif self.cb.currentText() == "Per Capita Net Earnings (Dollars)":
            df = pd.DataFrame({"opioidrate":opioidrate, "PCNE":PCNE, 'counties':counties},index=counties)
            df = df[df["opioidrate"] != 0]

            a = np.array(df['PCNE'])
            b = np.array(df['opioidrate'])
            c = np.array(df['counties'])

            df = px.data.tips()
            fig = px.scatter(x = a, y = b, trendline="ols", title="<b>Per Capita Net Earnings (Dollars) v.s. # of Prescriptions Per Person</b>", \
                labels={"x": "Per Capita Net Earnings (Dollars)","y": "# of Prescriptions Per Person"}, hover_name=c, opacity=0.7)
            fig.data[1].update(line_color='red')
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        elif self.cb.currentText() == "Net Earnings By Place Of Residence (Thousands Of Dollars)":
            df = pd.DataFrame({"opioidrate":opioidrate, "NEBPR":NEBPR, 'counties':counties},index=counties)
            df = df[df["opioidrate"] != 0]

            a = np.array(df['NEBPR'])
            b = np.array(df['opioidrate'])
            c = np.array(df['counties'])

            df = px.data.tips()
            fig = px.scatter(x = a, y = b, trendline="ols", title="<b>Net Earnings By Place Of Residence (Thousands Of Dollars) v.s. # of Prescriptions Per Person</b>", \
                labels={"x": "Net Earnings By Place Of Residence (Thousands Of Dollars)","y": "# of Prescriptions Per Person"}, hover_name=c, opacity=0.7)
            fig.data[1].update(line_color='red')
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        elif self.cb.currentText() == "Per Capita Personal Income (Dollars)":
            df = pd.DataFrame({"opioidrate":opioidrate, "PCPI":PCPI, 'counties':counties},index=counties)
            df = df[df["opioidrate"] != 0]

            a = np.array(df['PCPI'])
            b = np.array(df['opioidrate'])
            c = np.array(df['counties'])

            df = px.data.tips()
            fig = px.scatter(x = a, y = b, trendline="ols", title="<b>Per Capita Personal Income (Dollars) v.s. # of Prescriptions Per Person</b>", \
                labels={"x": "Per Capita Personal Income (Dollars)","y": "# of Prescriptions Per Person"}, hover_name=c, opacity=0.7)
            fig.data[1].update(line_color='red')
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        elif self.cb.currentText() == "Per Capita Personal Current Transfer Receipts (Dollars)":
            df = pd.DataFrame({"opioidrate":opioidrate, "PCPCTR":PCPCTR, 'counties':counties},index=counties)
            df = df[df["opioidrate"] != 0]

            a = np.array(df['PCPCTR'])
            b = np.array(df['opioidrate'])
            c = np.array(df['counties'])

            df = px.data.tips()
            fig = px.scatter(x = a, y = b, trendline="ols", title="<b>Per Capita Personal Current Transfer Receipts (Dollars) v.s. # of Prescriptions Per Person</b>", \
                labels={"x": "Per Capita Personal Current Transfer Receipts (Dollars)","y": "# of Prescriptions Per Person"}, hover_name=c, opacity=0.7)
            fig.data[1].update(line_color='red')
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        elif self.cb.currentText() == "Per Capita Income Maintenance Benefits (Dollars)":
            df = pd.DataFrame({"opioidrate":opioidrate, "PCIMB":PCIMB, 'counties':counties},index=counties)
            df = df[df["opioidrate"] != 0]

            a = np.array(df['PCIMB'])
            b = np.array(df['opioidrate'])
            c = np.array(df['counties'])

            df = px.data.tips()
            fig = px.scatter(x = a, y = b, trendline="ols", title="<b>Per Capita Income Maintenance Benefits (Dollars) v.s. # of Prescriptions Per Person</b>", \
                labels={"x": "Per Capita Income Maintenance Benefits (Dollars)","y": "# of Prescriptions Per Person"}, hover_name=c, opacity=0.7)
            fig.data[1].update(line_color='red')
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        elif self.cb.currentText() == "Per Capita Unemployment Insurance Compensation (Dollars)":
            df = pd.DataFrame({"opioidrate":opioidrate, "PCUIC":PCUIC, 'counties':counties},index=counties)
            df = df[df["opioidrate"] != 0]

            a = np.array(df['PCUIC'])
            b = np.array(df['opioidrate'])
            c = np.array(df['counties'])

            df = px.data.tips()
            fig = px.scatter(x = a, y = b, trendline="ols", title="<b>Per Capita Unemployment Insurance Compensation (Dollars) v.s. # of Prescriptions Per Person</b>", \
                labels={"x": "Per Capita Unemployment Insurance Compensation (Dollars)","y": "# of Prescriptions Per Person"}, hover_name=c, opacity=0.7)
            fig.data[1].update(line_color='red')
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        elif self.cb.currentText() == "Per Capita Retirement And Other (Dollars)":
            df = pd.DataFrame({"opioidrate":opioidrate, "PCRO":PCRO, 'counties':counties},index=counties)
            df = df[df["opioidrate"] != 0]

            a = np.array(df['PCRO'])
            b = np.array(df['opioidrate'])
            c = np.array(df['counties'])

            df = px.data.tips()
            fig = px.scatter(x = a, y = b, trendline="ols", title="<b>Per Capita Retirement And Other (Dollars) v.s. # of Prescriptions Per Person</b>", \
                labels={"x": "Per Capita Retirement And Other (Dollars)","y": "# of Prescriptions Per Person"}, hover_name=c, opacity=0.7)
            fig.data[1].update(line_color='red')
            self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))


    def info(self):
        self.messbox = QMessageBox()
        self.messbox.setIcon(QMessageBox.Information)
        self.messbox.setText("Instructions")
        self.messbox.setInformativeText("After selecting the axis values, press 'Generate Graph!' to create the desired scatter graph. Please wait as it takes a few seconds for the graph to load :)")
        self.messbox.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

"""
python GUI.py
"""

import csv
import os


def csv_to_arff(csv_name):
    fileToRead = f"{csv_name}"  # csv file name or absolute path to be open.
    fileToWrite = "bod_training_data.arff"  # name as how you'll save your arff file.
    relation = "tweets"  # how you'll like to call your relation as.

    columnsTemp = []  # Temporary stores each column of csv file except the attributes
    uniqueTemp = []  # Temporary Stores each data cell unique of each column
    uniqueOfColumn = []  # Stores each data cell unique of each column

    writeFile = open(fileToWrite, 'w', encoding="utf8")

    # Opening and Reading a CSV file
    f = open(fileToRead, 'r', encoding="utf8")
    reader = csv.reader(f)
    allData = list(reader)
    attributes = allData[0]
    totalCols = len(attributes)
    totalRows = len(allData)
    f.close()

    # Add a '0' for each empty cell
    for j in range(0, totalCols):
        for i in range(0, totalRows):
            if 0 == len(allData[i][j]):
                allData[i][j] = "0"
                print("0 added)")

    # check for comams or blanks and adds single quotes
    for j in range(0, totalCols):
        for i in range(1, totalRows):
            allData[i][j] = allData[i][j].lower()
            if "\r" in allData[i][j] or '\r' in allData[i][j] or "\n" in allData[i][j] or '\n' in allData[i][j]:
                allData[i][j] = allData[i][j].rstrip(os.linesep)
                allData[i][j] = allData[i][j].rstrip("\n")
                allData[i][j] = allData[i][j].rstrip("\r")
                allData[i][j] = allData[i][j].strip()
            try:
                if allData[i][j] == str(float(allData[i][j])) or allData[i][j] == str(int(allData[i][j])):
                    pass
            except ValueError as e:
                allData[i][j] = "\"" + allData[i][j] + "\""

    # fin gives unique cells for nominal and numeric
    for j in range(0, totalCols):
        for i in range(1, totalRows):
            columnsTemp.append(allData[i][j])
        for item in columnsTemp:
            if not (item in uniqueTemp):
                uniqueTemp.append(item)
        uniqueOfColumn.append("{" + ','.join(uniqueTemp) + "}")
        uniqueTemp = []
        columnsTemp = []

    # Show Relation
    writeFile.write("@relation " + "'" + relation + "'" + "\n")

    # Show Attributes

    writeFile.write("@attribute" + " " + " tweet" + " string" + "\n")
    writeFile.write("@attribute" + " " + " class" + " string" + "\n")

    # Show Data
    writeFile.write("@data\n")
    for i in range(2, totalRows):
        writeFile.write(','.join(allData[i]) + "\n")

    print(fileToRead + " was converted to " + fileToWrite)


csv_to_arff("Initial Training Data.csv") # INPUT NAME OF LABELLED DATA SET

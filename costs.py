#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 02:02:07 2019

@author: richard
"""

### 
### for f in *; do xlsx2csv "$f/Table_5_06_A.xlsx" "$f/Table_5_06_A.csv"; done 
### for f in *; do xlsx2csv "$f/epmxlfile5_6_a.xls" "$f/epmxlfile5_6_a.csv"; done
###
import pandas as pd
from dateutil import parser
import os
import glob
import xlrd, csv
import datetime
from statsmodels.tsa.seasonal import seasonal_decompose

months = ['null', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

### newer data
path = '/Users/richard/Documents/RMI/coop/state costs/EIA data new/*'
dirs = [os.path.join(dir, 'Table_5_06_A.csv') for dir in glob.glob(path)]

#initialize
df_or = pd.read_csv(dirs[0])
df = df_or.iloc[3:65, [0,9]]
df.columns = ['State', df_or.iloc[2, 1]]

#build df
for dir in dirs[1:]:
    data = pd.read_csv(dir)
    if (df.iloc[:, 0] == data.iloc[3:65, 0]).all():
        # all sectors
        df[data.iloc[2, 1]] = data.iloc[3:65, 9]
    else:
        print(data.iloc[2,1])

df.columns = ['State'] + [parser.parse(month, default=datetime.datetime(2016, 1, 1, 0, 0)).date() for month in df.columns[1:]]
df.reset_index(drop=True, inplace=True)







# convert xls to csv for older data
def csv_from_excel(excel_file):
    workbook = xlrd.open_workbook(excel_file)
    worksheet = workbook.sheet_by_index(0)
    with open(excel_file[:-4] + '.csv', 'w') as your_csv_file:
        wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
        for rownum in range(worksheet.nrows):
            wr.writerow([str(entry) for entry in worksheet.row_values(rownum)])

### older data
path = '/Users/richard/Documents/RMI/coop/state costs/EIA data old/*'
dirs = []
possible_filenames = ['epmxlfile5_6_a.xls', 'EPMXLFile 5_6_A.xls', 'EPMXLFile 5_6_A_OLD.xls']
for dir in glob.glob(path):
    for fi in possible_filenames:
        if os.path.exists(os.path.join(dir, fi)):
            dirs.append(os.path.join(dir, fi))
#[csv_from_excel(dir) for dir in dirs]

for dir in dirs:
    dir = dir[:-4] + '.csv'
    data = pd.read_csv(dir)
    if 'Table' in data.iloc[0,0]:
        data = data[1:].reset_index(drop=True)
    if (df.iloc[:, 0] == data.iloc[5:67, 0]).all():
        # all sectors
        date = datetime.date.fromordinal(693594 + int(float(data.iloc[4, 1])))
        df[date] = data.iloc[5:67, 9].reset_index(drop=True)
    else:
        print(dir)
    
    
#cleanup
df.set_index('State', inplace=True)
df = df.astype('float')
df.columns = pd.to_datetime(df.columns)
df=df.reindex(columns=sorted(df.columns))



# TRENDS
states = ['Kentucky', 'West Virginia', 'Indiana', 'Iowa', 'U.S. Total']
trends = pd.DataFrame()
for state in states:
    s = seasonal_decompose(df.loc[state], model='additive')
    trends[state] = s.trend

##### PROBLEM FILES MANUALLY EDITED:
#04 09: removed footnotes (LA TX Total)
#0104 and 0204: removed footnotes (MD CA)
#1004: changed date (38169, 37803)
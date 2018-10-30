import pandas as pd
import sys
import os
import re

#helper function for get_sheetnames
#check if the sheet name is found in excel
def is_found(find_reg_str,str):
    prog = re.compile(find_reg_str,re.IGNORECASE)
    m = prog.findall(str)
    if m:
        return True
    else:
        return False

#The function to get all the sheetnames within the excel file
#input: string: file_name
#return: []: list of sheets
def get_sheetnames(file_name):
    filter_sheet_reg='\w+(_|\s*)\d{4}'  #only match the regexp sheet name then will process. e.g. April 2018
    abs_name = os.path.abspath(file_name)
    df = pd.read_excel(abs_name, sheet_name=None)
    return filter(lambda x: is_found(filter_sheet_reg, x) == True, list(df.keys()))

# To run this file: python get_sheetname.py excel_file_name
if __name__=='__main__':
    if len(sys.argv) >= 2:
        sheet_lst = get_sheetnames(sys.argv[1])
        for sheet in sheet_lst:
            print(sheet)
    else:
        print("not enough arguments! exit.", file=sys.stderr)

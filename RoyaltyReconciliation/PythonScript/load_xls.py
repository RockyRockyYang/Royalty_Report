from os.path import join, dirname, abspath
import xlrd
import cx_Oracle
import os
import datetime,time 
import sys
from xlrd.sheet import ctype_text
import codecs
import operator
import argparse
from sys import stdin
import re
import csv

#########################################################################
# Coding by Wayne Liu on 06/04/2018
# Purpose: Maker project. http://wiki.imo-online.com:8090/display/DEV/Vendor+Report+Processing-Overview
#         1. upload xls files data into Oracle DB
#         2. Call procedure copy temp table data into ECW_ROYALTY_REPORT
########################################################################

#pip install cx_Oracle
#pip install xlrd


filter_sheet_reg='\w+(_|\s*)\d{4}'  #only match the regexp sheet name then will process. e.g. April 2018
table_name_prefix='ECW_'  #table name prefix 
filter_str="[\n!%&'*+,-./:;<=>?@\^`~\]\(\)\{\}\|\\\\[\]\" ]|^[#$0123456789_]*"  #oracle table name or column name invalid character.

db=''
connection = None
curs =None
insert_bind_sql="xxxxx"
ctas_sql="xxx"
table_name="xxxx"
current_processing_file_name=''

#use for shink column length. 
modify_length='''
DECLARE
  lv_len NUMBER;
BEGIN
  FOR i IN
  (
         SELECT 'select max(length('
                       ||column_name
                       ||')) from '
                       ||table_name AS exe_sql ,
                table_name ,
                column_name
         FROM   USER_TAB_COLUMNS
         WHERE  table_name = Upper( :p_table_name ) )
  LOOP
    begin
        EXECUTE IMMEDIATE i.exe_sql INTO lv_len;
        IF lv_len<4000-3 THEN
          lv_len:=lv_len+2;
        END IF;
        EXECUTE IMMEDIATE 'alter table '
        ||i.table_name
        ||' modify('
        ||i.column_name
        ||' varchar('
        ||lv_len
        ||'))';
    exception when others then
      dbms_output.put_line(i.table_name||'.'||i.column_name||sqlerrm);
    end;
  END LOOP;
END;
'''

#generate to file base upon sql.
def gen_csv( sql,fileName):   
    curs.execute( sql )
    csv_name=fileName.split('.')[0]+'_output.csv'
    row_count=0
    try:
        with open(csv_name , "w", newline='\n') as csv_file:
            csv.register_dialect('tabdelimiter',dialect="excel")
            csv_writer = csv.writer(csv_file, 'tabdelimiter' ,escapechar='"',lineterminator='\n')        
            csv_writer.writerow([i[0] for i in curs.description]) # write headers        
            for row in curs:
                row_count=row_count+1
                l=list(row)
                for i in range(0,len(l)):
                    if '\n' in str(l[i]):
                        l[i] = l[i].replace('\n',' ')                    
                csv_row_data=tuple(l)
                csv_writer.writerow(csv_row_data)
    except PermissionError: # if file is being opened, will got this error. 
        print('\nERROR:'+csv_name+' is is being opened, can not write data, close the file and try again.\n', file=sys.stderr)
    print('Total %s rows wrote in %s'%('{0:,}'.format(row_count),csv_name))
    return csv_name

#regexp replace string        
def reg_replace(reg_from,to,str):
    cmd_line=str
    insensitive_hippo = re.compile(reg_from, re.IGNORECASE)
    cmd_line=insensitive_hippo.sub(to, cmd_line)
    return cmd_line

#regexp find string
def is_found(find_reg_str,str):
    prog = re.compile(find_reg_str,re.IGNORECASE)
    m = prog.findall(str)
    if m:
        return True
    else:
        return False
    
#Interactive with use
def input(prompt_msg,limit_to=None):
    userinput=''    
    if limit_to==None:        
        while eq(userinput,''):
            sys.stdout.write(prompt_msg+' =>')
            sys.stdout.flush()
            userinput = stdin.readline()
    else:
        lt=limit_to.split(',')
        while userinput=='' or( userinput.rstrip().upper() not in lt):
            sys.stdout.write(prompt_msg+' =>')
            sys.stdout.flush()
            userinput = stdin.readline()
    return userinput.strip()


#return file name from full path
def get_file_name(full_name):
    return os.path.basename(full_name)

#Compare 2 string is equal or not. default ignore case. here '' equal None
def eq(p1,p2,i=True): 
    if p1 == None and p2=='':
        return True
    if p1 == '' and p2==None:
        return True
    if p1 == None and p2!=None:
        return False
    if p1 != None and p2==None:
        return False
    if p1 == None and p2==None:
        return True
    if type(p1)==int:
        p1=str(p1)
    if type(p2)==int:
        p2=str(p2)
        
    if i:
        if p1.upper().strip()==p2.upper().strip():
            return True
        else:
            return False
    else:
        if p1.strip()==p2.strip():
            return True
        else:
            return False

#return current path from current console        
def current_path(filename="",sub_folder=""):
    if filename=="" and sub_folder=="":
        return os.getcwd()
    if filename!="" and sub_folder=="":
        return os.getcwd()+"\\"+ filename
    if  sub_folder!="":
        new_path=os.getcwd()+"\\"+sub_folder
        if not os.path.exists(new_path):
           os.makedirs(new_path)
        if filename!="":
            return new_path+"\\"+filename
        else:
            return new_path    

#read config from current path    
def read_config():
    config_file=[]
    try:
        with open(current_path("column_head.txt")) as f:        
            config_file = f.readlines()
    except :
        pass
    return config_file

#generate insert statement, using for move excel data into db
def gen_bind_sql(table_name,file_column_list):
    s='INSERT INTO '+table_name+'('
    c='line_number,'
    b=':line_number,'
    for c1 in file_column_list:
        c1=get_valid_name(c1)
        b=b+':'+c1+ ','+'\n'
        c=c+' '+c1+ ','+'\n'
    c=c.rstrip(',\n')+') values ('    
    return (s+c+b).rstrip(',\n')+')'

#generate create table statement. 
def gen_ctas_sql(table_name,file_column_list):        
    s='CREATE TABLE '+table_name+'( line_number number,'
    c=''
    for c1 in file_column_list:
        c1=get_valid_name(c1)
        c=c+c1+ ' VARCHAR2(4000),'+'\n'
    return (s+c).rstrip(',\n')+')'
        

def execute_insert(db,list_sql,v):            
    try:
        curs.execute(list_sql,v)
        print('Successfully')
    except Exception as e:
        print(str(e), file=sys.stderr)
        print(list_sql, file=sys.stderr)
        print(v, file=sys.stderr)
    

def execute_sql(db,list_sql):
    r=""
    found=False    
    try:
        curs.execute(list_sql)
        found=True
        #print('Done: ['+list_sql+']')
        
    except cx_Oracle.DatabaseError as e:
        error, = e.args        
        if error.code == 955:
            print('Table already exists, ignore create statement.')
            
    except Exception as e:        
        print('execute_sql:'+str(e), file=sys.stderr)
    return found

#batch insert data into db
def execute_inserts_batch(db,list_sql,vs):
    try:
        curs.prepare(list_sql)
        curs.executemany(None,vs)
        print('Successfully completed insert %s records' %((len(vs))))      
        return True
    except Exception as e:        
        if is_found('ORA-01036',str(e)): #will not happen if load xls into db, only TAB file will has such problem.
            print('File contain TAB in string', file=sys.stderr) 
        else:
            print(str(e), file=sys.stderr)
        return False
    
#insert data into db by single record
def execute_inserts(db,list_sql,vs):            
    c=0
    for v in vs:
        try:
            curs.execute(list_sql,v)
            c+=1
            if (c%1000)==0:
                print('Completed %s'%(c))
        except Exception as e:
            print(str(e), file=sys.stderr)
            print(list_sql, file=sys.stderr)
            print(v, file=sys.stderr)
            break
    
    print('Total insert '+str(c))
    

   
#get the valid table name for column name.
#Some character can't be table name or column name .e.g. ? %    
def get_valid_name(str):
    x=reg_replace(filter_str,"",str).replace(" ","")
    return x.strip('_').replace('__','_')

def slipt_str(str):
    ll=[]
    for i in str.split('\t'):
        i=get_valid_name(i)
        ll.append(i.upper());
    if len(ll)<=1:
         for i in str.split(' '):
            i=get_valid_name(i)
            ll.append(i.upper());
    return ll

def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

#Get excel heading index. the heading not always at line 0
#check column_head.txt setting first. 
def get_first_column_row(fname,sheet_name):
    column_cfg=read_config()  
    #print('config:'+str(column_cfg))
    xl_workbook = xlrd.open_workbook(fname,on_demand = True)
    xl_sheet = xl_workbook.sheet_by_name(sheet_name)    
    # xl_sheet = xl_workbook.sheet_by_index(sheet_index) #using sheet_index to local the sheet that need to process.
    column_name_row_index=0
    cell_idx=dict()    
    config_list=[]
    found_by_config=False
    for row_idx in range(0, xl_sheet.nrows):
        #list_list_values.append([ str(v.value).rstrip('.0') for v in xl_sheet.row(row_idx) ])        
        text_count=0
        value_list=[]
        for i in xl_sheet.row(row_idx):
            #print('Type:%s'%(i.ctype)) # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
            if i.ctype==1 and not eq(i.value,''): #search cell type is text and not null, then put it into list               
                value_list.append(str(i.value).upper())
                text_count=text_count+1
        cell_idx[row_idx]=text_count
        cc=[]        
        for col_list in column_cfg:
            col_split_list=slipt_str(col_list)
            cc=intersection(col_split_list,value_list) #compare the xls and config, see how many intersection. 
            if len(cc)>0: #if found the intersecton then make this row as heading
                if len(col_split_list)-len(cc)<=2:
                    column_name_row_index=row_idx
                    found_by_config=True
        if row_idx>=25: #only search fist 25 rows. 
            break
    if not found_by_config:    #if heading can not be found from config file. then search row with longest text value.
        first_time=True
        old_key=10000
        for key, value in sorted(cell_idx.items(), key=lambda item: (item[1], item[0]),reverse=True):        
            if first_time:
                text_count=value
                first_time=False
            if text_count==value and key<=old_key:
                column_name_row_index=key
            old_key=key
        
    xl_workbook.release_resources()
    del xl_workbook
    return column_name_row_index

def convert_cell( cell, sheet,line_num):
        value = cell.value
        try:
            if cell.ctype == 3: #date data type
                if value == 0:
                    return None                
                x=datetime.datetime(*xlrd.xldate_as_tuple(value, sheet.book.datemode)).strftime('%Y-%m-%d')  #default cover date to yyyy-mm-dd format.            
                return str(x)
        except Exception as e:
            #print('convert_cell error at line %s :%s value is %s'%(line_num,str(e),str(value)))
            #print(cell)
            pass
        return str(value)

def process_xls_by_sheet1(fname,sheet_name):    
    first_column_row=get_first_column_row(fname,sheet_name)    #get xls heading first.
    global insert_bind_sql,ctas_sql,table_name
    xl_workbook = xlrd.open_workbook(fname)
    # List sheet names, and pull a sheet by name    
    sheet_names = xl_workbook.sheet_names()
    print('Processing sheet Names=[ %s ]'%(sheet_name))
    #xl_sheet = xl_workbook.sheet_by_name(sheet_names[sheet_index])
    # grab the sheet by index     
    xl_sheet = xl_workbook.sheet_by_name(sheet_name)    
    # Pull the row by index    
    row = xl_sheet.row(first_column_row)  # 1st  data row, it contain heading information    
    file_column_list=[]
    db_column_list=[]
    file_miss_columns=[]
    column_list_chk={}
    for idx, cell_obj in enumerate(row):
        cell_type_str = ctype_text.get(cell_obj.ctype, 'unknown type')     
        cv=reg_replace('\s+',' ',str(cell_obj.value).strip())
        excel_column=cv.replace(' ','_').upper()
        for i in range(1,10):
            if excel_column in column_list_chk:
               excel_column=excel_column+str(i)
            else:
                break        
        column_list_chk[excel_column]="Y"
        file_column_list.append(excel_column)
    db_column_list=[]
    

    table_name=''+sheet_name.upper().replace(' ','_')
    table_name=get_valid_name(table_name)
    table_name=table_name_prefix+get_valid_name(table_name)
    
    ctas_sql=gen_ctas_sql(table_name,file_column_list) 
    insert_bind_sql=gen_bind_sql(table_name,file_column_list)
    #print(ctas_sql)
    #print(insert_bind_sql)          
  
    num_cols = xl_sheet.ncols   # Number of columns, not use so far.
    list_list_values=[]
    #notes = xl_sheet.cell_note_map
    #print(notes)
    #for key in notes.keys():
    #     print(notes[key].text)
    
    #for row_idx in range(0, xl_sheet.nrows):    # Iterate through rows
    for row_idx in range(first_column_row+1, xl_sheet.nrows): #start from heading row+1 to sheet end row
        v_list=[]
        v_list.append(row_idx+1)        
        for v in xl_sheet.row(row_idx):  #loop by rows v here is cell object            
            v1=v.value #cell value
            #print(v.Comment.Text())
            if v.ctype==3 and ( not eq(str(v.value),'')): #cell type is date and not empty
                v1=convert_cell(v,xl_sheet,row_idx+1)                            
            v_list.append(reg_replace('\.0$','',str(v1))) #remove the .0 at the end. e.g. 134.0 should be 134                       
        list_list_values.append(v_list)  #append row values into list for next step.          
        #list_list_values.append([ str(v.value).rstrip('.0') for v in xl_sheet.row(row_idx) ])
    xl_workbook.release_resources()
    del xl_workbook
    return list_list_values

#call oracle procedure
#proc => procedure name
#*para, use comma seperate mult parameters e.g. call_proc(db,'sp_copy_data','ECW','MARCH_2018')
def call_proc(db,proc,*para):
    found=False
    curs=None
    connection=None
    print('Processing procedure '+proc)
    if para!=None :        
        connection = cx_Oracle.Connection(db)
        try:            
            curs = connection.cursor()
            curs.callproc("dbms_output.enable", (None,)) # enable output, if procedure has dbms_output.put_line, the message will output as well
            #return_val=curs.callfunc( para[0],cx_Oracle.STRING,para[1:]) #This for call oracle function. 
            curs.callproc(proc,para)
            statusVar = curs.var(cx_Oracle.NUMBER)
            lineVar = curs.var(cx_Oracle.STRING)
            while True:
              curs.callproc("dbms_output.get_line", (lineVar, statusVar))
              if statusVar.getvalue() != 0:
                break
              outmsg=(lineVar.getvalue())
              print('MSG From %s => %s'%(proc,outmsg))                          
        except Exception as e:
           connection.rollback()
           print('call_proc:'+str(e), file=sys.stderr)
        finally:
            if curs!=None:
               curs.close()
            if connection!=None:
                connection.commit()
                connection.close()        

def inset_data_to_db(vals):
    tab_file=False
    print('DB:'+db+' Table Name: '+table_name.upper())
    print('\n==[STEP 1] Upload xls into db')
    if execute_inserts_batch(db,insert_bind_sql,vals):      
        connection.commit()
        try:
            curs.execute(modify_length, p_table_name=table_name) # (3)
        except: 
            pass
        print('\n==[STEP 2] Copy temp table data into ECW_ROYALTY_REPORT')
        call_proc(db,'ECW_COPY_DATA',table_name)
        
        ############# Below will generate ROYALTY_REPORT to csv  ########
        print('\n==[STEP 3] Generating ROYALTY_REPORT')
        call_proc(db,'RUN_ECW_ROYALTY_REPORT')
        csv_name=gen_csv('select * from ROYALTY_REPORT order by ERROR_CODE',current_processing_file_name)
        # subprocess.Popen(csv_name, shell=True);
        #################################################################
    else:
        connection.rollback() #issues happen above, rollback data
        print('Check which records has issue', file=sys.stderr)        
        execute_inserts(db,insert_bind_sql,vals) #check which row have problem
        connection.rollback()
      

def insert_data_from_xls(fname,sheet_index):
    
    vals=process_xls_by_sheet1(fname,sheet_index)
    execute_sql(db,'drop table '+table_name+' purge')
    execute_sql(db,ctas_sql)    
    print('Inserting data into temp table:'+table_name)
    inset_data_to_db(vals)   

def process_files(fname):
    global  current_processing_file_name
    print('[ %s ] is being processed......'%(fname))
    current_processing_file_name=fname
    vals=[]
    tab_file=False
    valid_sheet_is_found=False
            
    if is_found('\.xls',fname):
        try:
            xl_workbook = xlrd.open_workbook(fname)
        except xlrd.XLRDError as e:
            #It could be auto remove password from file using excel Application lib. but this moment, just prompt message. 
            print('\nERROR: %s is password protected, pleases remove password protect from file first.'%(fname), file=sys.stderr) 
            sys.exit(1)
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(1)
            
        sheet_names = xl_workbook.sheet_names()
        xl_workbook.release_resources()
        del xl_workbook
##        for i in range(0,len(sheet_names)):   #load all sheets into db
##            if is_found(filter_sheet_reg,sheet_names[i]): #for ecw, only import Month_yyyy sheet, filter_sheet_reg will filter this             
##                insert_data_from_xls(fname,i)
        
        target_sheet = sys.argv[2]
        #below just load max period into db, and the period format must follow regexpress filter_sheet_reg setting           
        if is_found(filter_sheet_reg, target_sheet) and (target_sheet in sheet_names): #for ecw, only import Month_yyyy sheet, filter_sheet_reg will filter this
            valid_sheet_is_found=True
        if valid_sheet_is_found:
            insert_data_from_xls(fname, target_sheet)
            print('\n==[DONE] for file => %s \n\n'%(fname))
    if not valid_sheet_is_found:
        print('\nERROR: Not a valid xls or not contain valid sheet', file=sys.stderr)
        print('       File should be xlsx format and the sheet name should conform regexp '+filter_sheet_reg, file=sys.stderr)
        
#load_xls.py parameters will be set from here.
def get_args():
    parser = argparse.ArgumentParser(description='Marker Project, load xls into db')
    parser.add_argument('-db',           type=str, help='Connection string e.g. smoke/xxxx@imodev', required=False, default='smoke/change_12@imodev' )
    parser.add_argument('-encoding',     type=str, help='utf-8 or else', required=False, default=None)
    parser.add_argument('-file',         type=str, help='Excel file name that need to load into DB', required=False, default=None)
    parser.add_argument('-table_prefix', type=str, help='Table prefix for temp table', required=False, default=None)    
    args = parser.parse_args()    
    return  args


# sys.argv[1] is the file name and sys.argv[2] is the sheet name
if __name__ == '__main__':
    # args=get_args() #get parameter from the console   
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    filelist={}
    fileinfo={}
    filenum=1
    # change this permantly when get a new database
    db='maker/maker@BIREPORA1D.imo-online.com'
    print('Import DB is: '+db)
    # if not eq(sys.argv[2], ''):
    #     table_name_prefix=sys.argv[2]

    if eq(sys.argv[1],'') :           
        for f in files:
         if is_found('\.xls',f):
            filelist[filenum]=f    
            b = os.path.getsize(f)
            file_ctime=os.path.getmtime(f)                        
            b = int(round(b/1024))
            filesizeformat=("{:,}".format(b)).rjust(11," ")+" KB"
            date_=str(datetime.datetime.fromtimestamp(file_ctime))
            fileinfo[filenum]=f.ljust(50," ")+date_[0:19]+' ['+filesizeformat+']'
            filenum=filenum+1            
        print('='*100)
        file_name_for_choise=''
        for k,v in(fileinfo.items()):
            print('%s : %s'%(k,v))
            file_name_for_choise=file_name_for_choise+str(k)+','
        print('='*100)
        print("\r\n")    
        choise=input('Which excel file you whant to load? key in number('+file_name_for_choise+')\r\nq to exit')
        if choise.upper() in ["Q","QUIT","EXIT"]:
            sys.exit(0)
            
    
    connection=None    
    # if args.encoding!=None and is_found('UTF',args.encoding):        
    #     os.environ["NLS_LANG"] = "AMERICAN_AMERICA.UTF8"    
    connection = cx_Oracle.Connection(db)
    curs = connection.cursor()
    index_=0
    filelist[0]=sys.argv[1]
    if not eq(sys.argv[1],''):
      process_files(sys.argv[1])  
    else:
        if eq(choise,'*'):
            choise=file_name_for_choise
        
        for i in filelist:        
            for z in choise.split(','):
                if not eq(z+'',''):
                    if int(z)==i:
                        process_files(filelist[i])
            index_=index_+1;        
    curs.close()
    connection.commit()
    connection.close()
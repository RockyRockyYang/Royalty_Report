# Royalty Reconciliation

## Need to be Installed
    - Python 3.6
    - Oracle JDBC Driver
    
---
## Setting Up Royalty Reconciliation 
0. Clone repository on TFS to obtain all RoyaltyReconciliation files
0. Make sure when cloning the repsitory it is stored in 'C:\Users\'YOURUSERNAME'\source\repos'
0. Once repository cloned open:
    - Visual Studio
    - Visual Studio Code

---
## In Visual Studio
0. Go to 'Controllers' and select the ForkController.cs and the uploadController.cs
0. Make sure you change the path of the files to the path that you stored the files so that application will run correctly.

---
## Running Royalty Reconciliation in Visual Studio Code
0. Open the projects entire folder in Visual Studio Code
> NOTE: Need to have authorization token before compiling correctly
0. Once authorized type 'npm install' to compile application
0. After packeges have been installed, type 'ng serve --open' to open up application in localhost:4200

---
## Using Royalty Reconciliation
0. Upload any eCW Quarterly Report that has to be .xls or .xlsx in order to upload the workbook.
0. It will upload the file and you can choose between each month from that quarter. (Summary and Bundle Missing orgIDs for eCW report will be excluded)
0. Once excel sheet is selected the Looker website will appear with the data displayed from the excel sheet with numbers on the side which are the "Business Rules".
> - These business rules can be found here: http://wiki.imo-online.com:8090/display/DEV/eCW+Business+Rules

#### NOTE: 
- We  turned off the cach settings in order for the webpage to automatically reload when selecting a different sheet from the drop down menu.
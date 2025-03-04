"""Configuration file for the validation framework"""

# please copy the files to Testdata directory
# copy the pipeline file path in output
OUTPUTPATH = "Test_Data/Microsoft_Pipeline_Output.xlsx"

# copy the Groundtruth file path
GTPATH = "Test_Data/Ground_Truth_Software_Microsoft.xlsx"

# TO Check the business level logics enter the file path
FILE_TO_CHECK_BUSINESS_LOGIC = "Test_Data/tbs_flat_file.xlsx"

# Enter the key values to generate a pseudo key
# while selecting the key columns please select the columns are text, avoid float dtype columns
KEYS = ['Product_Service_SKU_Name_Original','Level 5 Category']

# in order to ease access of data sorting the values by column
COLUMN_VALUE_TO_SORTBY = "Product_Service_SKU_Name_Original"

# reports highlighted and summary stored in this path
REPORTPATH = "Reports"

#stored the output pipeline and Gt output for manual verification
OUTPUTFILE = REPORTPATH+"/final_report_output.xlsx"

# Intermediate data reports are stored here for debug purpose.
VALIDATIONREPORT = "ValidationData"

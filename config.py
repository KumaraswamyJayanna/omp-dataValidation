
OUTPUTPATH = "Test_Data/Microsoft_PipelineOutput.xlsx"
GTPATH = "Test_Data/Software _Microsoft_Ground_Truth.xlsx"
REPORTPATH = "Reports"
VALIDATIONREPORT = "ValidationData"
SUMMARYREPORT = "Reports"
cols_for_primary_key = ['File_Name', 'Product_Service_SKU_Name_Original']
validationdata1 = "ValidationData/pipelineValidationData_result_Software _Micr2025-02-12.xlsx"
validationdata2 = "ValidationData/groundtruthValidationData_result_Software _Micr2025-02-12.xlsx"
KEYS = ["Product_Service_SKU_Name_Original", "File_Name", "Level 5 Category"]
COLUMN_VALUE_TO_SORTBY = "Product_Service_SKU_Name_Original"

OUTPUTFILE = REPORTPATH+"/final_report_output.xlsx"
# Threshold for file-level accuracy (adjust as needed)
ACCURACYTHRESHOLD = 90

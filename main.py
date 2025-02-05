from data_preprocess import DataCleaning
from generatereport import ExcelReport
from config import OUTPUTPATH, GTPATH


if __name__ == "__main__":
    data_preprocess = DataCleaning(OUTPUTPATH, GTPATH)
    extra_columns = data_preprocess.check_column_difference()
    print(f"Extra columns : {extra_columns}")
    structured_baseline_df, structured_compare_df = data_preprocess.filter_columns()
    data_preprocess.check_column_difference()
    print("Create a validation report after pre-processing the Data")
    data_preprocess.check_row_wise_in_dataframe()
    print("Get the mismatches column wise")
    out, preprocess_pipeline, preprocess_gt = data_preprocess.compare_and_highlight_excel()
    print("Highlights report is generating")
    report_generator = ExcelReport(file1_path=preprocess_pipeline, file2_path=preprocess_gt)
    report_generator.generate_report()

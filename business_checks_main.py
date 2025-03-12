from validate_general_checks import Report
from conditional_checks import ConditionalChecks
import subprocess
import main
import logging as logger


if __name__ == "__main__":
    # pipeline_data_file = input("Enter the pipeline file path : ")
    pipeline_data_file = "C:/Users/kumaraswamy.jaya/Documents/Businnesslogicverification/tbs_flat_file.xlsx"
    condition = input("Do you want to run Business-Level Validation (Type Y/N) : ")
    if condition.lower() == "y" or condition.lower() == "yes":
        lookup_file = "C:/Users/kumaraswamy.jaya/Documents/Businnesslogicverification/lookup_file.xlsx"
        conditional_lookup_file = lookup_file
        # conditional_lookup_file = input("Enter the conditional lookup file : ")
        genearte_report =  Report(pipeline_data_file, lookup_file, "TreasuryBanking")
        conditional_checks = ConditionalChecks()
        genearte_report.create_logger()
        logger.info(f'Create a logger report')
        logger.info(f'Find the missing Columns in the datafile')
        missing_columns = genearte_report.check_columns_missing()
        logger.info(f'Get the mandatory columns details')
        mandatory_columns = genearte_report.get_mandatory_columns()
        logger.info(f'Generate a report file')
        report_sheet = genearte_report.create_report_sheet()
        logger.info(f'Verify the fields which are all null values')
        all_null_fields = genearte_report.verify_for_all_null_values()
        logger.info(f"Verify the mandatory column's/Fields are null")
        mandatory_null_fields = genearte_report.mandatory_columns_null_values(mandatory_columns)
        # Highlight the cells in light blue
        genearte_report.highlight_complete_column(report_sheet, columns=mandatory_null_fields, color="C8B6FC")
        logger.info(f"Verify the d-type of the fields")
        verify_dtype = genearte_report.verify_dtype()
        # highlight the cells in light green
        genearte_report.highlight_complete_column(report_sheet, columns=verify_dtype, color="CFE3D9")
        logger.info(f'Verify the conditional checks')
        logger.info(f"Verify the datasheet data contains the expected values")
        conditional_checks.verify_original_name_data(report_sheet)
        logger.info(f'Verifying for the negative values')
        conditional_checks.verify_for_non_negative(report_sheet)
        print(f"Reports Generated here {report_sheet}")
        logger.info("Execution completed")

    elif condition.lower() == "n" or condition.lower() == "no":
        verify_with_groundtruth = input("Do you have GT File and compare with the Groundtruth (Type Y/N):")
        if verify_with_groundtruth == 'y' or verify_with_groundtruth == 'yes':
            groundtruth_file = input("Enter the Groundtruth File path : ")
            subprocess.run(main.py)
        else:
            print("closing the execution")
            quit()
    else:
        print("Verify your input")


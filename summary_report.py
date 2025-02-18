"""To generate a category level and file level summary reports"""
import os.path
import re
from datetime import datetime

import pandas as pd

from config import ACCURACYTHRESHOLD, GTPATH, OUTPUTPATH, REPORTPATH

output_path = OUTPUTPATH
gt_path = GTPATH
val = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = REPORTPATH + f'/summary_report_{val}.xlsx'
# Threshold for file-level accuracy (adjust as needed)
accuracy_threshold = ACCURACYTHRESHOLD

cols_for_primary_key = ['File_Name', 'Product_Service_SKU_Name_Original']


def clean_column(value):
    """ Remove special characters and spaces, convert to lowercase"""
    return re.sub(r'[^a-zA-Z0-9]', '', value).lower()

def find_mismatches(df1, df2):

    """Finding the true mismatches counts"""
    mismatches = {}
    df1, df2 = df1.astype(str), df2.astype(str)
    columns_to_compare = list(df1.columns)
    for column in columns_to_compare:
        try:
            merged_df = df1.merge(df2, suffixes=('_df1', '_df2'), how='outer')
            mismatch_column = f'{column}_Mismatch'
            merged_df[mismatch_column] = merged_df[f'{column}'] != merged_df[f'{column}']
            true_mismatches = merged_df[mismatch_column].sum()
            false_mismatches = (~merged_df[mismatch_column]).sum()
            true_value = round((true_mismatches / (true_mismatches + false_mismatches)) * 100, 2)
            mismatches[column] = 100 - float(true_value)
        except Exception as e:
            df_res[column] = "NA"
            print(f"{column} is unable to merge due to different dtype", e)
    return mismatches

def generate_primary_key(df, columns):
    """Generate primary key by concatenating cleaned values row-wise, &
    Remove non-alphanumeric characters and lowercase
    """
    # Ensure the columns exist in the DataFrame
    if not all(col in df.columns for col in columns):
        raise ValueError("Some columns in the list are not present in the DataFrame.")

    primary_key = df[columns].apply(
        lambda row: ''.join(
            ''.join(filter(str.isalnum, str(row[col]))).lower()
            for col in columns
        ),
        axis=1
    )

    return primary_key


df_output = pd.read_excel(output_path)
df_gt = pd.read_excel(gt_path)

df_result = pd.DataFrame()

files = df_gt['File_Name'].unique()
df_result['File_Name'] = files

df_result['Total Rows per File as per GT'] = (
    df_result['File_Name'].map(df_gt.groupby('File_Name')['File_Name'].count()))

df_gt['Product_Service_SKU_Name_Original'] = (
    df_gt['Product_Service_SKU_Name_Original'].apply(clean_column))
df_output['Product_Service_SKU_Name_Original'] = (
    df_output['Product_Service_SKU_Name_Original'].apply(clean_column))

df_output.insert(0,
                 "Primary_key_output",
                 generate_primary_key(df_output, cols_for_primary_key))
df_gt.insert(0,
             "Primary_key_gt",
             generate_primary_key(df_gt, cols_for_primary_key))

df_merged = df_gt.merge(df_output,
                        left_on="Primary_key_gt",
                        right_on="Primary_key_output",
                        how="outer")

mapping_sku_absence_in_output = df_merged.groupby('File_Name_x')['Primary_key_output'].apply(
    lambda x: x.isnull().sum()).to_dict()
df_result['Missing Extractions (Complete Row)'] = (df_result['File_Name']
                                                   .map(mapping_sku_absence_in_output)
                                                   .fillna(0).astype(int))

mapping_extra_extraction = df_merged.groupby('File_Name_x')['Primary_key_gt'].apply(
    lambda x: x.isnull().sum()).to_dict()
df_result['Extra Extractions (Not Present in Ground Truth)'] = df_result['File_Name'].map(
    mapping_extra_extraction).fillna(0).astype(int)

df_result["Duplicates Extraction"] = df_merged.duplicated()
pipeline_duplicate_rows = df_merged.duplicated(keep=False)
true_duplicates = pipeline_duplicate_rows.sum()

mapping_incorrect_orginal_name_extraction = \
df_merged[df_merged['Product_Service_SKU_Name_Original_x'] !=
          df_merged['Product_Service_SKU_Name_Original_y']].groupby('File_Name_x')['File_Name_x'].count()
df_result['Product_Service_SKU_Name_Original'] = df_result['File_Name'].map(
    mapping_incorrect_orginal_name_extraction).fillna(0)


cols_to_check = ["File_Name", "Total Rows per File as per GT", "Missing Extractions (Complete Row)",
                 "Extra Extractions (Not Present in Ground Truth)", "Duplicates Extraction"]
cols = list(df_output.columns[1:])
cols_to_check.extend(cols)
df_res = df_gt.merge(df_output,
                     left_on="Primary_key_gt",
                     right_on="Primary_key_output",
                     how="outer")


for i in range(len(cols)):
    # Check for mismatched values, excluding cases where both are NaN
    try:
        mismatched = df_res[
            (df_res[f'{cols_to_check[i]}_x'] != df_res[f'{cols_to_check[i]}_y']) &
            ~(pd.isna(df_res[f'{cols_to_check[i]}_x']) & pd.isna(df_res[f'{cols_to_check[i]}_y']))
            ]
    except Exception as e:
        df_res[cols_to_check[i]] = "NA"
        print(f"{cols_to_check[i]} is unable to merge:", e)

    # Group by 'File_Name_x' and count mismatches
    mappings = mismatched.groupby('File_Name_x').size().to_dict()

    # Map mismatches to the result DataFrame
    df_result['File_Name'] = files
    df_result[cols[i]] = df_result['File_Name'].map(mappings).fillna(0).astype(int)

# Calculate overall accuracy and affected files for each measure
results = []
measures = list(df_result.columns)[2:]

df_result_summary = pd.DataFrame(
    columns=["Iteration Number", "Issue Type", "Issue Level", "Overall Accuracy Percentage",
             "Number of Files affected", "Percentage_of_Missing", "Percentage of Correct"])

mismatches = find_mismatches(df_output, df_gt)
mismatches["Duplicates Extraction"] = true_duplicates if (
                                    true_duplicates >= accuracy_threshold) else 0

print("Generating Summary report...")
# Calculate overall accuracy and affected files for each measure
for measure in measures:
    # iteration number has to handle in pipeline while naming the file incremental number in suffix
    file_level_issue = ["Missing Extractions (Complete Row)",
                        "Extra Extractions (Not Present in Ground Truth)",
                        "Duplicates Extraction"]
    total_errors = df_result[measure].sum()
    total_rows = df_result["Total Rows per File as per GT"].sum()
    accuracy_percentage = round(100 - (total_errors / total_rows * 100), 2)
    affected_files = ((df_result[measure] > 0) &
                      ((100 - df_result[measure] / df_result["Total Rows per File as per GT"]
                        * 100)))
    num_affected_files = affected_files.sum()
    percentage_of_missing = (df_output[measure].isnull().sum()/len(df_output[measure]))*100\
                            if measure in df_output.columns else 0
    # percentage_of_missing = (df_result[measure].isnull().sum() / len(df_result[measure]) * 100)
    percentage_of_incorrect = mismatches[measure] if measure in list(mismatches.keys()) else "-"

    # Append results to the DataFrame
    df_records_field_type = {
        "Iteration Number": "0.0",
        "Issue Type": measure,
        "Issue Level": "Field" if measure not in file_level_issue else "File",
        "Overall Accuracy Percentage": float(accuracy_percentage),
        "Number of Files affected (have file level accuracy < x%)": float(num_affected_files),
        "Perrcentage of missing": round(float(percentage_of_missing), 2),
        "percentage_of_Incorrect": percentage_of_incorrect
    }

    df_result_summary.loc[measures.index(measure)+1] = df_records_field_type.values()


with pd.ExcelWriter(output_file) as writer:
    df_result_summary.to_excel(writer, sheet_name='Category_Issue_Summary')
    df_result.to_excel(writer, sheet_name='File Level Accuracy', index=False)
    print(f"Generated reports are copied here: {os.path.abspath(output_file)}")

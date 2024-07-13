import pandas as pd
file1 = 'excelfile1.xlsx'
file2 = 'excelfile2.xlsx'
file3 = 'excelfile3.xlsx'


df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)
df3 = pd.read_excel(file3)

# Merge the dataframes
merged_df = pd.concat([df1, df2, df3])

# Reset index for courses
current_course_index = 1
previous_course_index = merged_df.loc[0, 'Course Index']
new_course_indices = []

# Save the final merged dataframe to a new Excel file
output_file = 'merged_df.xlsx'
merged_df.to_excel(output_file, index=False)

print(f'Final merged file saved as {output_file}')
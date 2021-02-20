# Surecom_KPI
Surecom Parser for Indoor KPI process

This tool is a custom parser tool to create the results for:
* 3G statistics: RSCP, EcNo, Band

Usage: python.exe main.py input_directory_with_FMT_files

Ouput: Creates one csv file for every FMT file that is found in input directory.
The output directory can be configured on the Settings.py python file.

On output directory, there is a template excel file to visualize better the created csv files.

The default delimiter is set to ';', however it can be changed in Settings.py file.
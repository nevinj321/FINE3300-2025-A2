# FINE 3300 — Assignment 2 (Part B): Consumer Price Index (CPI) Analysis
# Data manipulation using Pandas from Statistics Canada files

import pandas as pd

# Read and combined 11 CPI files into one new DataFrame 
# List of 11 CSV files (Canada + 10 provinces), uses file names
files = [
    "Canada.CPI.1810000401.csv",
    "AB.CPI.1810000401.csv",
    "BC.CPI.1810000401.csv",
    "MB.CPI.1810000401.csv",
    "NB.CPI.1810000401.csv",
    "NL.CPI.1810000401.csv",
    "NS.CPI.1810000401.csv",
    "ON.CPI.1810000401.csv",
    "PEI.CPI.1810000401.csv",
    "QC.CPI.1810000401.csv",
    "SK.CPI.1810000401.csv"
]

# Create empty list to store DataFrames
all_data = []

for file in files:
    # Read CSV file
    df = pd.read_csv(file)
    
    # Extract jurisdiction abbreviation from filename (before first dot)
    jurisdiction = file.split(".")[0]
    
    # Add jurisdiction column
    df["Jurisdiction"] = jurisdiction
    
    # Reshape from wide to long format using pd.melt()
    # Converts month columns (24-Jan, 24-Feb, etc.) into rows
    df_long = pd.melt(df, 
                      id_vars=["Item", "Jurisdiction"], 
                      var_name="Month", 
                      value_name="CPI")
    
    all_data.append(df_long)

# Question 1: Combined all dataframes and included few entries to show the new data frame working
combined_df = pd.concat(all_data, ignore_index=True)
combined_df = combined_df[["Item", "Month", "Jurisdiction", "CPI"]]
print()
print("Question 1: Combined DataFrame created and few entries shown just as example")
print("=" * 60)
sample = combined_df[
    (combined_df["Jurisdiction"] == "Canada") & 
    (combined_df["Month"] == "24-Jan") &
    (combined_df["Item"].isin(["All-items", "Food", "Shelter"]))
]
print(sample.to_string(index=False))
print()

# Question 2: I printed the first 12 lines 
print("Question 2: First 12 lines of combined DataFrame")
print("=" * 60)
print(combined_df.head(12))
print()

# Question 3: calculated the Average month-to-month change for specific categories 
print("Question 3: Average month-to-month change (%)")
print("=" * 60)
print("->>>Average change for Food, Shelter, and All-items excluding Food and Energy (all combined)")
print()

# Calculate Month to Month change across ALL rows (no filtering, no category distinction)
combined_df = combined_df.sort_values(["Jurisdiction", "Month"])
combined_df["Month_to_month_Change"] = combined_df.groupby("Jurisdiction")["CPI"].pct_change() * 100

# Grouped it by Jurisdiction and found average month-to-month change
jurisdiction_avg_change = combined_df.groupby("Jurisdiction")["Month_to_month_Change"].mean().reset_index()
# Rename to desired average column name and round
jurisdiction_avg_change["Avg_Month_to_month_Change"] = jurisdiction_avg_change["Month_to_month_Change"].round(1)
jurisdiction_avg_change = jurisdiction_avg_change[["Jurisdiction", "Avg_Month_to_month_Change"]]
print(jurisdiction_avg_change)
print()


# Question 4: Province with highest average change for the three categories from Question 3
print("Question 4: Province with highest average change (in Food, Shelter, and All-items excluding food and energy)")
print("=" * 60)

# From our summary DataFrame created in Question 3, get the province with the maximum average
# (idxmax returns the row index of the highest value)
highest_row = jurisdiction_avg_change.loc[
    jurisdiction_avg_change["Avg_Month_to_month_Change"].idxmax()
]
# Print the result with proper labelling as required by the assignment
print(f"Jurisdiction: {highest_row['Jurisdiction']}")
print(f"Average Change: {highest_row['Avg_Month_to_month_Change']}%")
print()

#  Question 5: Equivalent salary to $100,000 in Ontario (December 2024) 
print("Question 5: Equivalent salary to $100,000 in Ontario across all provinces (Dec-2024)")
print("=" * 60)

# From the combined CPI data, filter for 'All-items' and December 2024 only
# (The assignment wants to compare December 2024 purchasing power)
# "Canada" is included in the table as a national reference for baseline purposes
dec_2024 = combined_df[(combined_df["Month"] == "24-Dec") & 
                        (combined_df["Item"] == "All-items")].copy()
# Get Ontario's All-items CPI (needed for scaling) 
ontario_cpi = dec_2024[dec_2024["Jurisdiction"] == "ON"]["CPI"].values[0]
# For each province, calculate salary with equivalent purchasing power as $100,000 in Ontario
# (classic cross-province CPI scaling formula)
dec_2024["Equivalent_Salary"] = (100000 * dec_2024["CPI"] / ontario_cpi).round(2)
# Print a table of all provinces, their December CPI, and the calculated equivalent salary
result_q5 = dec_2024[["Jurisdiction", "CPI", "Equivalent_Salary"]].sort_values("Jurisdiction")
print(result_q5.to_string(index=False))
print()

#  Question 6: Minimum wage analysis 
print("Question 6: Minimum Wage Analysis")
print("=" * 60)
min_wages = pd.read_csv("MinimumWages.csv")
# 6a: Find the nominal (not CPI-adjusted) highest minimum wage in Canada, and print province and wage
highest_nominal = min_wages.loc[min_wages["MinimumWage"].idxmax()]
print(f"6a. Highest nominal minimum wage:")
print(f"    Province: {highest_nominal['Province']}")
print(f"    Wage: ${highest_nominal['MinimumWage']:.2f}")
print()
# 6b: Find the lowest nominal minimum wage and print province and wage 
lowest_nominal = min_wages.loc[min_wages["MinimumWage"].idxmin()]
print(f"6b. Lowest nominal minimum wage:")
print(f"    Province: {lowest_nominal['Province']}")
print(f"    Wage: ${lowest_nominal['MinimumWage']:.2f}")
print()
# 6c: Merge minimum wage data with December 2024 CPI table calculated above
#    This is for "real" (CPI-adjusted) provincial minimum wage comparison
min_wages_with_cpi = min_wages.merge(dec_2024[["Jurisdiction", "CPI"]], 
                                      left_on="Province", 
                                      right_on="Jurisdiction")
# Calculate "real" minimum wage using the formula = (Nominal wage / CPI) * 100 
min_wages_with_cpi["Real_MinWage"] = (min_wages_with_cpi["MinimumWage"] / 
                                       min_wages_with_cpi["CPI"] * 100).round(2)
# Identify and print the province with the highest CPI-adjusted real minimum wage 
highest_real = min_wages_with_cpi.loc[min_wages_with_cpi["Real_MinWage"].idxmax()]
print(f"6c. Highest REAL minimum wage (adjusted for CPI, Dec-2024):")
print(f"    Province: {highest_real['Province']}")
print(f"    Real Wage: ${highest_real['Real_MinWage']:.2f}")
print()

#  Question 7: Annual change in CPI for Services 
print("Question 7: Annual change in CPI for Services (Jan-2024 to Dec-2024)")
print("=" * 60)
# Get DataFrame with only 'Services' rows for all months and provinces
services_df = combined_df[combined_df["Item"] == "Services"].copy()
# Get each province's CPI for January 2024
jan_services = services_df[services_df["Month"] == "24-Jan"][["Jurisdiction", "CPI"]]
jan_services.columns = ["Jurisdiction", "CPI_Jan"]
# Get each province's CPI for December 2024
dec_services = services_df[services_df["Month"] == "24-Dec"][["Jurisdiction", "CPI"]]
dec_services.columns = ["Jurisdiction", "CPI_Dec"]
# Merge Jan and Dec for every province so we can do the annual comparison
annual_change = jan_services.merge(dec_services, on="Jurisdiction")
# Calculate annual % change using: (Dec - Jan) / Jan * 100, rounded to 1 decimal place
annual_change["Annual_Change"] = ((annual_change["CPI_Dec"] - annual_change["CPI_Jan"]) / 
                                   annual_change["CPI_Jan"] * 100).round(1)
# Print all provinces and their annual % change
result_q7 = annual_change[["Jurisdiction", "Annual_Change"]].sort_values("Jurisdiction")
print(result_q7.to_string(index=False))
print()

#  Question 8: Region with highest inflation in Services 
print("Question 8: Region with highest inflation in Services")
print("=" * 60)
# The idxmax step finds which province row had the largest positive annual CPI change in the 'Services' category
highest_inflation = annual_change.loc[annual_change["Annual_Change"].idxmax()]
print(f"Jurisdiction: {highest_inflation['Jurisdiction']}")
print(f"Annual Change: {highest_inflation['Annual_Change']}%")
print()
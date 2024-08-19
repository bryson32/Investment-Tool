import pandas as pd

# Global variables
investment_per_month = 0  # Monthly investment amount in dollars
iul_cap = 10 / 100  # IUL cap
iul_floor = 0 / 100  # IUL floor
initial_investment = 100
years = 30  # Number of years
number_of_tranches = 54  # Number of tranches

# File path to the CSV file
file_path = './SP 500 vs. IUL Comparison.csv'
output_file_path = './investment_results_yearly.csv'

data = pd.read_csv(file_path, skiprows=5)
data.columns = ['Date', 'SP_Value', 'Trimmed_SP_Value', 'Rolling_Annual_Returns', 'IUL_Returns', 'IUL_Returns_Value']
data['Date'] = pd.to_datetime(data['Date'], format='%d-%b-%y')
data_cleaned = data.dropna(subset=['Rolling_Annual_Returns', 'IUL_Returns_Value'])

data_cleaned['SP_Value'] = pd.to_numeric(data_cleaned['SP_Value'].str.replace(' ', '').str.replace(',', ''), errors='coerce')
data_cleaned['Rolling_Annual_Returns'] = pd.to_numeric(data_cleaned['Rolling_Annual_Returns'].str.replace('%', ''), errors='coerce') / 100
data_cleaned['IUL_Returns'] = pd.to_numeric(data_cleaned['IUL_Returns'].str.replace('%', ''), errors='coerce') / 100

data_cleaned = data_cleaned.dropna()

# Select the first 360 rows (most recent 30 years) and reverse them to go from oldest to newest (the plus 6 is to start from january of the 30 years ago for my friends use case, remove if you want purely 30 years ago)
data_last_30_years = data_cleaned.iloc[:years * 12 + 6][::-1].reset_index(drop=True)

# Create a DataFrame to store the results
results_df = pd.DataFrame()

# Loop through each tranche
for tranche in range(number_of_tranches):
    sp_investment_value = initial_investment
    iul_investment_value = initial_investment

    # Create lists to store yearly values for this tranche
    sp_values = []
    iul_values = []

    # Calculate the maximum number of years we can iterate for the current tranche
    max_years_for_tranche = years - tranche // 12
    
    # Loop through each year for the current tranche
    for year in range(max_years_for_tranche):
        month_index = tranche + year * 12
        
        if month_index >= len(data_last_30_years):
            break

        # S&P 500
        if year > 0:
            sp_investment_value = sp_investment_value * (1 + data_last_30_years.loc[month_index, 'Rolling_Annual_Returns'])
        sp_investment_value += investment_per_month * 12

        # IUL
        if year > 0:
            iul_return = data_last_30_years.loc[month_index, 'Rolling_Annual_Returns']
            capped_return = max(min(iul_return, iul_cap), iul_floor)
            iul_investment_value = iul_investment_value * (1 + capped_return)
        iul_investment_value += investment_per_month * 12

        # Store the values for this year
        sp_values.append(sp_investment_value)
        iul_values.append(iul_investment_value)

    # Add the yearly values to the results DataFrame
    results_df[f'Tranche_{tranche+1}_SP'] = pd.Series(sp_values)
    results_df[f'Tranche_{tranche+1}_IUL'] = pd.Series(iul_values)

# Write the results to a CSV file
results_df.to_csv(output_file_path, index=False)

print(f"Investment results have been saved to {output_file_path}")

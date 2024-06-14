import numpy as np
import pandas as pd
from data_preparation.cleaning import drop_controversies_columns
from utils.connector import all_companies_with_ticker as companies
from data_preparation.cleaning import flatten_dict, clean_decarbonization_target, merge_involvement
from data_preparation.encoding import encoding_colors, involvement_encoding, encoding_aligned_no


def create_weighted_metric(df, weights, metric_name):
    for col in weights.keys():
        if col not in df.columns:
            raise ValueError(f"Colonna {col} non trovata nel DataFrame")
    df[metric_name] = sum(df[col] * weight for col, weight in weights.items())
    return df.drop(columns=list(weights.keys()))


def merge_by_esg(df):
    environmental_weights = {
        'Controversies_Environment': 1.0,
        'sdg_Affordable and Clean Energy': 1.0,
        'sdg_Clean Water and Sanitation': 1.0,
        'sdg_Climate Action': 1.0,
        'sdg_Life under Water': 1.0,
        'sdg_Life on Land': 1.0
    }

    social_weights = {
        'Controversies_Social': 1.0,
        'Controversies_Customers': 1.0,
        'Controversies_Human Rights & Community': 1.0,
        'Controversies_Labor Rights & Supply Chain': 1.0,
        'sdg_No Poverty': 1.0,
        'sdg_No Hunger': 1.0,
        'sdg_Good Health and Well-Being': 1.0,
        'sdg_Quality Education': 1.0,
        'sdg_Gender Equality': 1.0,
        'sdg_Decent Work and Economic Growth': 1.0,
        'sdg_Reduced Inequalities': 1.0,
        'sdg_Sustainable Cities and Communities': 1.0,
        'sdg_Peace, Justice and Strong Institutions': 1.0,
        'sdg_Responsible Consumption and Production': 1.0
    }

    governance_weights = {
        'Controversies_Governance': 1.0,
        'sdg_Partnerships for the Goals': 1.0,
        'sdg_Industry, Innovation and Infrastructure': 1.0,
    }

    involvement_weights = {
        'Weapons involvement': 1.0,
        'Gambling involvement': 1.0,
        'Tobacco involvement': 1.0,
        'Alcoholic involvement': 1.0
    }

    # Create metrics and drop original columns
    df = create_weighted_metric(df, environmental_weights, 'environmental_metric')
    df = create_weighted_metric(df, social_weights, 'social_metric')
    df = create_weighted_metric(df, governance_weights, 'governance_metric')
    df = create_weighted_metric(df, involvement_weights, 'involvement_metric')

    return df


def clean():
    flattened_data = [flatten_dict(data) for data in companies]
    df = pd.DataFrame(flattened_data)
    df.to_csv('../data/raw.csv', index=False)

    df = df.drop(columns=['_id', 'domain', 'name', 'sector', 'industry', 'ticker', 'sdg',
                          'Decarbonization Target_Decarbonization Target',
                          'Decarbonization Target_Decarbonization Target on Temperature Rise'])

    # replace null values with Nan in esg column
    df['esg'] = df['esg'].replace('null', np.nan)
    df = df.dropna(subset=['esg'])

    df = drop_controversies_columns(df)

    # merging of columns and drop 'Environment'
    df = merge_involvement(df).drop(columns=['Environment'])

    inv_cols = ['Weapons', 'Gambling', 'Tobacco', 'Alcoholic']

    # replace null values with Nan in involvement columns
    for col in inv_cols:
        df[col] = df[col].replace('null', np.nan)

    # save dataset
    df.to_csv('../data/temp.csv', index=False)
    df = df.dropna(subset=inv_cols)

    df = involvement_encoding(df)

    # drop columns with less than 50% of values
    # threshold = len(df) * 0.3
    # df = df.dropna(thresh=threshold, axis=1)

    # df = involvement_encoding(df)

    print('---------------------')
    # count number of value not null for each column
    cols = df.columns
    for col in cols:
        print(f"{col} - {df[col].count()}")

    # df = clean_decarbonization_target(df)
    # df = drop_controversies(df).copy()

    df.to_csv('../data/cleaned.csv', index=False)
    print('\nData cleaning completed')


def clean_with_metrics(flattened_data):
    df = (pd.DataFrame(flattened_data).drop(columns=['_id', 'domain',
                                                     'name',
                                                     'sector',
                                                     'industry'])
          .replace('null', np.nan))

    df = df.dropna(subset=['esg'])

    # Drop columns with all NaN values
    df = df.dropna(subset=['ticker'])
    # df = df.drop('ticker', axis=1)

    # format decarbonization columns
    df = clean_decarbonization_target(df)

    # format employee column
    df['employees'] = df['employees'].astype('Int64')

    # merge involvement columns
    df = merge_involvement(df)
    df = involvement_encoding(df)  # yes/no = 1/0

    # encoding controversies columns
    df = encoding_colors(df)

    # drop cols with only one value
    cols_with_only_one_value = ['Decarbonization Target_Decarbonization Target',
                                'Decarbonization Target_Decarbonization Target on Temperature Rise']
    df = df.drop(columns=cols_with_only_one_value)

    df = encoding_aligned_no(df)

    # drop column with less 500 values
    threshold = 500
    df = df.dropna(thresh=threshold, axis=1)

    df = df.dropna()
    df = merge_by_esg(df)

    # df.to_csv('../data/label_with_metrics.csv', index=False)
    return df


if __name__ == '__main__':
    flattened_data = [flatten_dict(data) for data in companies]
    clean_with_metrics(flattened_data=flattened_data)

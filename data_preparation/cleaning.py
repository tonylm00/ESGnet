import numpy as np
import pandas as pd

pd.set_option('future.no_silent_downcasting', True)


def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f'{parent_key}{sep}{k}' if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def clean_decarbonization_target(df):
    df['Decarbonization Target_Target Year'] = df['Decarbonization Target_Target Year'].astype('Int64')
    df['Decarbonization Target_Comprehensiveness'] = (df['Decarbonization Target_Comprehensiveness']
                                                      .replace('t\n', '', regex=True))
    df['Decarbonization Target_Comprehensiveness'] = (df['Decarbonization Target_Comprehensiveness']
                                                      .str.replace('%', '').astype(float))
    df['Decarbonization Target_Ambition p.a.'] = (df['Decarbonization Target_Ambition p.a.'].astype(str)
                                                  .str.replace('%', '').astype(float))
    return df


def merge_columns_function(row, columns):
    if any(row[col] == 'Yes' for col in columns):
        return 'Yes'
    if any(row[col] == 'No' for col in columns):
        return 'No'
    return np.nan


def merge_involvement(df):
    # Define the mapping for new columns
    merge_columns = {
        'Weapons involvement': [
            'involvement_msci_Controversial Weapons',
            'involvement_Controversial Weapons',
            'involvement_Small Arms',
            'involvement_Military Contracting'
        ],
        'Gambling involvement': [
            'involvement_Gambling',
            'involvement_msci_Gambling',
            'involvement_Adult Entertainment'
        ],
        'Tobacco involvement': [
            'involvement_msci_Tobacco Products',
            'involvement_Tobacco Products'
        ],
        'Alcoholic involvement': [
            'involvement_Alcoholic Beverages',
            'involvement_msci_Alcoholic Beverages'
        ],
        'Environment involvement': [
            'involvement_Pesticides',
            'involvement_Thermal Coal',
            'involvement_Palm Oil',
            'involvement_GMO',
            'involvement_Animal Testing',
            'involvement_Fur and Specialty Leather'
        ]
    }

    for new_col, cols_to_merge in merge_columns.items():
        df[new_col] = df.apply(lambda row: merge_columns_function(row, cols_to_merge), axis=1)

    # Drop unwanted columns
    ob_cols = [
        'involvement_Alcoholic Beverages',
        'involvement_Adult Entertainment',
        'involvement_Gambling',
        'involvement_Tobacco Products',
        'involvement_Animal Testing',
        'involvement_Fur and Specialty Leather',
        'involvement_Controversial Weapons',
        'involvement_Small Arms',
        'involvement_Catholic Values',
        'involvement_GMO',
        'involvement_Military Contracting',
        'involvement_Pesticides',
        'involvement_Thermal Coal',
        'involvement_Palm Oil',
        'involvement_msci_Controversial Weapons',
        'involvement_msci_Gambling',
        'involvement_msci_Tobacco Products',
        'involvement_msci_Alcoholic Beverages',
        'involvement'
    ]

    df.drop(columns=ob_cols, inplace=True)

    return df


def controversies_imputation(dataframe):
    # List of columns to check for NaN and replace with 'White'
    controversy_columns = [
        'Controversies_Supply Chain Labor Standards',
        'Controversies_Health & Safety',
        'Controversies_Discrimination & Workforce Diversity',
        'Controversies_Labor Management Relations',
        'Controversies_Anticompetitive Practices',
        'Controversies_Privacy & Data Security',
        'Controversies_Bribery & Fraud',
        'Controversies_Governance Structures',
        'Controversies_Customer Relations',
        'Controversies_Product Safety & Quality',
        'Controversies_Human Rights Concerns',
        'Controversies_Energy & Climate Change',
        'Controversies_Toxic Emissions & Waste',
        'Controversies_Impact on Local Communities',
        'Controversies_Biodiversity & Land Use',
        'Controversies_Other',
        'Controversies_Marketing & Advertising',
        'Controversies_Civil Liberties',
        'Controversies_Operational Waste (Non-Hazardous)',
        'Controversies_Collective Bargaining & Union',
        'Controversies_Supply Chain Management',
        'Controversies_Water Stress',
        'Controversies_Child Labor',
        'Controversies_Controversial Investments'
    ]

    # Replace NaN values with 'White' in the specified columns
    for col in controversy_columns:
        dataframe[col] = dataframe[col].fillna('White')

    return dataframe


def drop_controversies_columns(df):
    cols = [
        'Controversies_Supply Chain Labor Standards',
        'Controversies_Collective Bargaining & Union',
        'Controversies_Health & Safety',
        'Controversies_Discrimination & Workforce Diversity',
        'Controversies_Labor Management Relations',
        'Controversies_Anticompetitive Practices',
        'Controversies_Privacy & Data Security',
        'Controversies_Bribery & Fraud',
        'Controversies_Governance Structures',
        'Controversies_Customer Relations',
        'Controversies_Product Safety & Quality',
        'Controversies_Human Rights Concerns',
        'Controversies_Energy & Climate Change',
        'Controversies_Toxic Emissions & Waste',
        'Controversies_Impact on Local Communities',
        'Controversies_Biodiversity & Land Use',
        'Controversies_Other',
        'Controversies_Marketing & Advertising',
        'Controversies_Civil Liberties',
        'Controversies_Operational Waste (Non-Hazardous)',
        'Controversies_Supply Chain Management',
        'Controversies_Water Stress',
        'Controversies_Child Labor',
        'Controversies_Controversial Investments'
    ]

    return df.drop(columns=cols)

import numpy as np
import pandas as pd

pd.set_option('future.no_silent_downcasting', True)


def flatten_dict(d, parent_key='', sep='_'):
    """
    Flattens a nested dictionary.

    Parameters:
    d (dict): The dictionary to flatten.
    parent_key (str, optional): The base key string to use for the new keys. Defaults to ''.
    sep (str, optional): The separator to use between parent and child keys. Defaults to '_'.

    Returns:
    dict: A flattened dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = f'{parent_key}{sep}{k}' if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def clean_decarbonization_target(df):
    """
    Cleans and processes decarbonization target columns in the DataFrame.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing decarbonization target columns.

    Returns:
    pd.DataFrame: The DataFrame with cleaned decarbonization target columns.
    """
    try:
        df['Decarbonization Target_Target Year'] = df['Decarbonization Target_Target Year'].astype('Int64')

        df['Decarbonization Target_Comprehensiveness'] = (df['Decarbonization Target_Comprehensiveness']
                                                          .replace('t\n', '', regex=True))
        df['Decarbonization Target_Comprehensiveness'] = (df['Decarbonization Target_Comprehensiveness']
                                                          .str.replace('%', '').astype(float))

        df['Decarbonization Target_Ambition p.a.'] = (df['Decarbonization Target_Ambition p.a.'].astype(str)
                                                      .str.replace('%', '').astype(float))
    except KeyError:
        pass

    return df


def merge_columns_function(row, columns):
    """
    Merges multiple columns into a single column based on specific criteria.

    Parameters:
    row (pd.Series): A row of the DataFrame.
    columns (list): A list of column names to merge.

    Returns:
    str or np.nan: 'Yes' if any column has 'Yes', 'No' if any column has 'No', otherwise NaN.
    """
    try:
        if any(row[col] == 'Yes' for col in columns):
            return 'Yes'
        if any(row[col] == 'No' for col in columns):
            return 'No'
    except KeyError:
        pass
    return np.nan


def merge_involvement(df):
    """
    Merges involvement columns into new columns and drops the original columns.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing involvement columns.

    Returns:
    pd.DataFrame: The DataFrame with merged involvement columns and original columns dropped.
    """
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

    cols_to_drop = [
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
    df.drop(columns=cols_to_drop, inplace=True, errors='ignore')

    return df


def controversies_imputation(dataframe):
    """
    Imputes missing values in controversy columns with 'White'.

    Parameters:
    dataframe (pd.DataFrame): The input DataFrame containing controversy columns.

    Returns:
    pd.DataFrame: The DataFrame with imputed controversy columns.
    """
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

    for col in controversy_columns:
        dataframe[col] = dataframe[col].fillna('White')

    return dataframe


def drop_controversies_columns(df):
    """
    Drops controversy columns from the DataFrame.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing controversy columns.

    Returns:
    pd.DataFrame: The DataFrame with controversy columns dropped.
    """
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

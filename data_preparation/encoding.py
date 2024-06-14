def involvement_encoding(df):
    """
    Encodes involvement columns in the DataFrame by replacing 'Yes' with 1.0 and 'No' with 0.01.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing involvement columns.

    Returns:
    pd.DataFrame: The DataFrame with encoded involvement columns.
    """
    cols = [
        'Weapons involvement',
        'Gambling involvement',
        'Tobacco involvement',
        'Alcoholic involvement',
        'Environment involvement'
    ]

    for col in cols:
        df[col] = df[col].replace('Yes', 1.0).replace('No', 0.01)

    return df


def encoding_colors(df):
    """
    Encodes color-based controversy columns in the DataFrame with numerical values.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing controversy columns.

    Returns:
    pd.DataFrame: The DataFrame with encoded controversy columns.
    """
    cols = [
        'Controversies_Environment',
        'Controversies_Social',
        'Controversies_Customers',
        'Controversies_Human Rights & Community',
        'Controversies_Labor Rights & Supply Chain',
        'Controversies_Governance'
    ]
    for col in cols:
        try:
            df[col] = (df[col].replace('Green', 0.01)
                       .replace('Yellow', 0.34)
                       .replace('Orange', 0.67)
                       .replace('Red', 1.0))
        except KeyError:
            pass
    return df


def encoding_aligned_no(df):
    """
    Encodes SDG alignment columns in the DataFrame by replacing 'No', 'Aligned', and 'Strongly Aligned'
    with numerical values 1.0, 0.5, and 0.01, respectively.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing SDG alignment columns.

    Returns:
    pd.DataFrame: The DataFrame with encoded SDG alignment columns.
    """
    cols = [
        'sdg_No Poverty',
        'sdg_No Hunger',
        'sdg_Good Health and Well-Being',
        'sdg_Quality Education',
        'sdg_Gender Equality',
        'sdg_Clean Water and Sanitation',
        'sdg_Affordable and Clean Energy',
        'sdg_Decent Work and Economic Growth',
        'sdg_Industry, Innovation and Infrastructure',
        'sdg_Reduced Inequalities',
        'sdg_Sustainable Cities and Communities',
        'sdg_Responsible Consumption and Production',
        'sdg_Climate Action',
        'sdg_Life under Water',
        'sdg_Life on Land',
        'sdg_Peace, Justice and Strong Institutions',
        'sdg_Partnerships for the Goals'
    ]

    for col in cols:
        df[col] = (df[col].replace('No', 1.0)
                   .replace('Aligned', 0.5)
                   .replace('Strongly Aligned', 0.01))

    return df


def create_weighted_controversy_metric(df):
    """
    Creates a weighted controversy metric for the DataFrame and drops the original controversy columns.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing controversy columns.

    Returns:
    pd.DataFrame: The DataFrame with the weighted controversy metric and without the original controversy columns.

    Raises:
    ValueError: If any controversy column is not found in the DataFrame.
    """
    weights = {
        'Controversies_Environment': 1.0,
        'Controversies_Social': 1.0,
        'Controversies_Customers': 1.0,
        'Controversies_Human Rights & Community': 1.0,
        'Controversies_Labor Rights & Supply Chain': 1.0,
        'Controversies_Governance': 1.0,
    }

    for col in weights.keys():
        if col not in df.columns:
            raise ValueError(f"{col} not found in DataFrame")

    df['controversies_metric'] = sum(df[col] * weight for col, weight in weights.items())

    return df.drop(columns=list(weights.keys()))


def create_weighted_sdg_metric(df):
    """
    Creates a weighted SDG metric for the DataFrame and drops the original SDG columns.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing SDG columns.

    Returns:
    pd.DataFrame: The DataFrame with the weighted SDG metric and without the original SDG columns.

    Raises:
    ValueError: If any SDG column is not found in the DataFrame.
    """
    sdg_weights = {
        'sdg_No Poverty': 1.0,
        'sdg_No Hunger': 1.0,
        'sdg_Good Health and Well-Being': 1.0,
        'sdg_Quality Education': 1.0,
        'sdg_Gender Equality': 1.0,
        'sdg_Clean Water and Sanitation': 1.0,
        'sdg_Affordable and Clean Energy': 1.0,
        'sdg_Decent Work and Economic Growth': 1.0,
        'sdg_Industry, Innovation and Infrastructure': 1.0,
        'sdg_Reduced Inequalities': 1.0,
        'sdg_Sustainable Cities and Communities': 1.0,
        'sdg_Responsible Consumption and Production': 1.0,
        'sdg_Climate Action': 1.0,
        'sdg_Life under Water': 1.0,
        'sdg_Life on Land': 1.0,
        'sdg_Peace, Justice and Strong Institutions': 1.0,
        'sdg_Partnerships for the Goals': 1.0,
    }

    for col in sdg_weights.keys():
        if col not in df.columns:
            raise ValueError(f"{col} not found in DataFrame")

    df['sdg_metric'] = sum(df[col] * weight for col, weight in sdg_weights.items())

    return df.drop(columns=list(sdg_weights.keys()))

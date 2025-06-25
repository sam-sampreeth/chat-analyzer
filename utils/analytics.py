def filter_by_date(df, date_range):
    start, end = date_range
    return df[(df["datetime"].dt.date >= start) & (df["datetime"].dt.date <= end)]

def get_users(df):
    return sorted(df["sender"].unique())

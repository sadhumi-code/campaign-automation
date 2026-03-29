import pandas as pd


def load_data(events_path: str, ads_path: str, campaigns_path: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load source CSV files."""
    events = pd.read_csv(events_path)
    ads = pd.read_csv(ads_path)
    campaigns = pd.read_csv(campaigns_path)
    return events, ads, campaigns


def merge_datasets(events: pd.DataFrame, ads: pd.DataFrame, campaigns: pd.DataFrame) -> pd.DataFrame:
    """Join event-level data with ad and campaign dimensions."""
    merged = events.merge(ads, on="ad_id", how="left")
    merged = merged.merge(campaigns, on="campaign_id", how="left")
    return merged


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Safely divide two Series, returning 0 where denominator is 0."""
    result = numerator.div(denominator.where(denominator != 0))
    return result.fillna(0)


def calculate_event_metrics(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """Aggregate standard campaign event metrics by chosen dimensions."""
    summary = (
        df.groupby(group_cols)
        .agg(
            impressions=("event_type", lambda x: (x == "Impression").sum()),
            clicks=("event_type", lambda x: (x == "Click").sum()),
            purchases=("event_type", lambda x: (x == "Purchase").sum()),
        )
        .reset_index()
    )

    summary["CTR"] = safe_divide(summary["clicks"], summary["impressions"])
    summary["Conversion_Rate"] = safe_divide(summary["purchases"], summary["clicks"])
    return summary


def create_ad_day_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create ad-level daily performance using day_of_week granularity."""
    group_cols = ["campaign_id", "ad_id", "ad_platform", "day_of_week"]
    return calculate_event_metrics(df, group_cols)


def create_platform_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create platform-level performance by campaign and day of week."""
    group_cols = ["campaign_id", "ad_platform", "day_of_week"]
    return calculate_event_metrics(df, group_cols)


def save_outputs(ad_day_summary: pd.DataFrame, platform_summary: pd.DataFrame) -> None:
    """Write aggregated outputs to CSV files."""
    ad_day_summary.to_csv("output_summary.csv", index=False)
    platform_summary.to_csv("output_platform_summary.csv", index=False)


def main() -> None:
    events, ads, campaigns = load_data("ad_events.csv", "ads.csv", "campaigns.csv")
    df = merge_datasets(events, ads, campaigns)

    ad_day_summary = create_ad_day_summary(df)
    platform_summary = create_platform_summary(df)

    save_outputs(ad_day_summary, platform_summary)
    print("✅ Campaign metrics generated (ad/day + platform summaries)!")


if __name__ == "__main__":
    main()

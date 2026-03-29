
def main():
    import pandas as pd

    # Load files
    events = pd.read_csv("ad_events.csv")
    ads = pd.read_csv("ads.csv")
    campaigns = pd.read_csv("campaigns.csv")

    # Merge datasets
    df = events.merge(ads, on="ad_id", how="left")
    df = df.merge(campaigns, on="campaign_id", how="left")

    # Aggregate metrics
    summary = df.groupby(["campaign_id", "ad_id"]).agg(
        impressions=("event_type", lambda x: (x == "Impression").sum()),
        clicks=("event_type", lambda x: (x == "Click").sum()),
        purchases=("event_type", lambda x: (x == "Purchase").sum())
    ).reset_index()

    # Derived metrics
    summary["CTR"] = summary["clicks"] / summary["impressions"]
    summary["Conversion_Rate"] = summary["purchases"] / summary["clicks"]

    # Handle division issues
    summary = summary.fillna(0)

    # Save output
    summary.to_csv("output_summary.csv", index=False)

    print("✅ Campaign metrics generated!")


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

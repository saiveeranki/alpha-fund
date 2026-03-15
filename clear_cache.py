from data.database import SessionLocal, GenericCache

def clear_all_heatmap_cache():
    db = SessionLocal()
    try:
        # Clear sector returns for all markets
        count1 = db.query(GenericCache).filter(GenericCache.key.like("sector_returns_%")).delete(synchronize_session=False)
        # Clear sector metrics for all markets
        count2 = db.query(GenericCache).filter(GenericCache.key.like("sector_metrics_%")).delete(synchronize_session=False)
        db.commit()
        print(f"Cleared {count1} return cache entries and {count2} metric cache entries.")
    except Exception as e:
        db.rollback()
        print(f"Error clearing cache: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_heatmap_cache()


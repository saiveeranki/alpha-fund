from data.database import SessionLocal, GenericCache

def clear_india_cache():
    db = SessionLocal()
    try:
        # Clear sector returns for India
        count1 = db.query(GenericCache).filter(GenericCache.key.like("sector_returns_India%")).delete(synchronize_session=False)
        # Clear sector metrics for India
        count2 = db.query(GenericCache).filter(GenericCache.key == "sector_metrics_India").delete(synchronize_session=False)
        db.commit()
        print(f"Cleared {count1} return cache entries and {count2} metric cache entries for India.")
    except Exception as e:
        db.rollback()
        print(f"Error clearing cache: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_india_cache()

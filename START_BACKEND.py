#!/usr/bin/env python
"""
START BACKEND - Production Ready
Keep this running in a terminal
"""
import sys
import time

if __name__ == "__main__":
    print("=" * 60)
    print("ENTRY SAFE BACKEND - v3 Clean Start")
    print("=" * 60)
    
    start_time = time.time()
    print(f"\n🚀 Starting at {time.strftime('%H:%M:%S')}")
    
    try:
        import uvicorn
        print(f"[+{time.time() - start_time:.2f}s] Uvicorn imported")
        
        print(f"[+{time.time() - start_time:.2f}s] Starting server...")
        print("\n" + "=" * 60)
        
        uvicorn.run(
            app="app.main:app",
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=False,
            access_log=True
        )
        
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n\n✅ Backend shutdown cleanly after {elapsed:.1f}s")
        sys.exit(0)
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ ERROR after {elapsed:.1f}s:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

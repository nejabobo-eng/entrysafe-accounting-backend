#!/usr/bin/env python
"""
Quick startup verification - checks if app can start WITHOUT hanging
"""
import asyncio
import sys

async def test_startup():
    """Test if the startup event completes within a reasonable time"""
    print("Testing app startup...")
    
    try:
        # Import app
        from app.main import app
        print("✅ App imported")
        
        # Simulate startup event
        print("Testing startup event...")
        startup_task = asyncio.create_task(app.router.startup_events[0]())
        
        # Wait with timeout
        await asyncio.wait_for(startup_task, timeout=5.0)
        print("✅ Startup completed in < 5 seconds")
        return True
        
    except asyncio.TimeoutError:
        print("❌ STARTUP HUNG (timeout > 5 seconds)")
        return False
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_startup())
    sys.exit(0 if result else 1)

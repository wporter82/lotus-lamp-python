import asyncio
from lotus_lamp import LotusLamp

async def main():
    lamp = LotusLamp()
    await lamp.connect()
    
    # Always sync time first (lamp has no RTC)
    await lamp.sync_time()
    
    # One-shot timer: turn on at 7:30 AM tomorrow
    await lamp.set_timer_on(7, 30)
    
    # Repeating timer: turn off at 11 PM on weekdays
    await lamp.set_timer_off(23, 0, days=['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
    
    # Disable timers
    await lamp.disable_timer_on()
    await lamp.disable_timer_off()
    
    await lamp.disconnect()

asyncio.run(main())
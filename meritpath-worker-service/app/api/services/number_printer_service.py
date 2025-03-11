import logging
import asyncio

logger = logging.getLogger(__name__)

class NumberPrinterService:
    async def print_numbers(self):
        """
        Print numbers from 1 to 100 and return the result.
        Uses asyncio.sleep instead of time.sleep for non-blocking operation.
        """
        logger.info("Starting to print numbers from 1 to 100")
        
        numbers = []
        for i in range(1, 101):
            print(i)
            numbers.append(i)
            # Small delay to avoid flooding the console
            await asyncio.sleep(0.05)
        
        logger.info("Finished printing numbers from 1 to 100")
        return {"numbers": numbers, "count": len(numbers)} 
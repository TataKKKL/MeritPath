import logging
import asyncio
import random

logger = logging.getLogger(__name__)

class NumberPrinterService:
    async def print_numbers(self):
        """
        Print numbers from 1 to a random number between 50 and 100 and return the result.
        Uses asyncio.sleep instead of time.sleep for non-blocking operation.
        """
        # Generate a random end number between 50 and 100
        end_number = random.randint(50, 100)
        
        logger.info(f"Starting to print numbers from 1 to {end_number}")
        
        numbers = []
        for i in range(1, end_number + 1):
            print(i)
            numbers.append(i)
            # Small delay to avoid flooding the console
            await asyncio.sleep(0.05)
        
        logger.info(f"Finished printing numbers from 1 to {end_number}")
        return {"numbers": numbers, "count": len(numbers), "end_number": end_number} 
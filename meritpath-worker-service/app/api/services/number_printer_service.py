import logging
import asyncio
import random

logger = logging.getLogger(__name__)

class NumberPrinterService:
    async def print_numbers(self, end_number=None):
        """
        Print numbers from 1 to a specified number or random between 50 and 100 and return the result.
        Uses asyncio.sleep instead of time.sleep for non-blocking operation.
        """
        try:
            # Use provided end number or generate random one
            if end_number is None:
                end_number = random.randint(50, 100)
            else:
                end_number = int(end_number)  # Ensure it's an integer
            
            logger.info(f"Starting to print numbers from 1 to {end_number}")
            
            numbers = []
            for i in range(1, end_number + 1):
                print(i)
                numbers.append(i)
                # Small delay to avoid flooding the console
                await asyncio.sleep(0.05)
            
            logger.info(f"Finished printing numbers from 1 to {end_number}")
            return {
                "status": "success",
                "numbers": numbers, 
                "count": len(numbers), 
                "end_number": end_number
            }
        except Exception as e:
            logger.error(f"Error printing numbers: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            } 
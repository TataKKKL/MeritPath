import logging
import time

logger = logging.getLogger(__name__)

class NumberPrinterService:
    def print_numbers(self):
        """
        Print numbers from 1 to 100 and return the result.
        """
        logger.info("Starting to print numbers from 1 to 100")
        
        numbers = []
        for i in range(1, 101):
            print(i)
            numbers.append(i)
            # Small delay to avoid flooding the console
            time.sleep(0.05)
        
        logger.info("Finished printing numbers from 1 to 100")
        return {"numbers": numbers, "count": len(numbers)} 
# Modified number_printer_controller.py
from fastapi import Response
from app.api.services.number_printer_service import NumberPrinterService

class NumberPrinterController:
    def __init__(self):
        self.number_printer_service = NumberPrinterService()
        
    async def print_numbers(self):  # Make this method async too
        """
        Execute the number printer service and return the result.
        """
        result = await self.number_printer_service.print_numbers()  # Add await here
        return result
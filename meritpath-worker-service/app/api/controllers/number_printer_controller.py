# Modified number_printer_controller.py
from fastapi import Response
from app.api.services.number_printer_service import NumberPrinterService

class NumberPrinterController:
    def __init__(self):
        self.number_printer_service = NumberPrinterService()
        
    async def print_numbers(self, end_number=None):  # Add the optional parameter
        """
        Execute the number printer service and return the result.
        """
        result = await self.number_printer_service.print_numbers(end_number)  # Pass the parameter
        return result
from fastapi import Response
from app.api.services.number_printer_service import NumberPrinterService

class NumberPrinterController:
    def __init__(self):
        self.number_printer_service = NumberPrinterService()
        
    def print_numbers(self):
        """
        Execute the number printer service and return the result.
        """
        result = self.number_printer_service.print_numbers()
        return result 
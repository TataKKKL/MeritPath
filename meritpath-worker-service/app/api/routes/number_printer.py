# Modified number_printer.py (route)
from fastapi import APIRouter, Query
from app.api.controllers.number_printer_controller import NumberPrinterController

router = APIRouter(
    prefix="",
    tags=["number_printer"]
)
number_printer_controller = NumberPrinterController()

@router.get("", include_in_schema=True)
async def print_numbers(end_number: int = Query(None, description="Optional end number")):
    """
    Print numbers from 1 to the specified number (or random between 50-100) and return the result.
    """
    return await number_printer_controller.print_numbers(end_number)
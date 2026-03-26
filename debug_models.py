import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    print("Importing Ticket model...")
    from app.models.ticket import Ticket
    print("Ticket imported.")
    # from app.models.ticket import TicketMessage
    # print("TicketMessage imported.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

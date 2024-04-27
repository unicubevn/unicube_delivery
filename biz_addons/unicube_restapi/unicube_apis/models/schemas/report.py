class Report:
    total_ship: int
    total_price: int
    count: int
    state: str
    picking_type_id: int

    def __init__(self, total_ship: int, total_price: int, count: int, state: str, picking_type_id: int) -> None:
        self.total_ship = total_ship
        self.total_price = total_price
        self.count = count
        self.state = state
        self.picking_type_id = picking_type_id
class ReportResponse:
    total_ship: int
    total_price: int
    total_order: int
    status: str

    def __init__(self, total_ship: int, total_price: int, total_order: int, status : str) -> None:
        self.total_ship = total_ship
        self.total_price = total_price
        self.total_order = total_order
        self.status = status

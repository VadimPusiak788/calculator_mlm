import json
import argparse
from typing import List, Dict
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import calendar


class MLMCommissionCalculator:
    COMMISSION_RATE = Decimal('0.05')

    def __init__(self, partners_data: List[Dict]):
        self.partners_data = self._build_partner_hierarchy(partners_data)

    def _build_partner_hierarchy(self, partners_data: List[Dict]) -> Dict:
        partners_by_id: Dict[int, Dict] = {}

        for partner in partners_data:
            partner_id: int = partner['id']
            parent_id: int = partner['parent_id']

            if not isinstance(partner_id, int):
                raise ValueError(f'Invalid partner ID: {partner_id}')

            if parent_id is not None and not isinstance(parent_id, int):
                raise ValueError(f'Invalid parent ID for partner {partner_id}')

            if partner_id in partners_by_id:
                raise ValueError(f"Duplicate partner ID: {partner_id}")

            partners_by_id[partner_id] = {
                'id': partner_id,
                'name': partner.get('name', f'Partner {partner_id}'),
                'monthly_revenue': Decimal(str(partner['monthly_revenue'])),
                'parent_id': parent_id,
                'children': []
            }

        self._detect_cycles(partners_by_id)

        for partner_id, partner in partners_by_id.items():
            parent_id = partner['parent_id']
            if parent_id is not None:
                if parent_id not in partners_by_id:
                    raise ValueError(f'Parent {parent_id} not found for partner {partner_id}')
                partners_by_id[parent_id]['children'].append(partner_id)

        return partners_by_id

    def _detect_cycles(self, partner_dict: Dict):

        def trace_ancestry(partner_id: int) -> List[int]:
            path = []
            current_id = partner_id

            while current_id is not None:
                if current_id in path:
                    # Cycle detected
                    cycle_start_index = path.index(current_id)
                    cycle = path[cycle_start_index:]
                    raise ValueError(
                        f"Cycle detected in partner hierarchy: {' -> '.join(map(str, cycle + [current_id]))}"
                    )

                path.append(current_id)
                current_id = partner_dict.get(current_id, {}).get('parent_id')

            return path

        for partner_id in partner_dict:
            trace_ancestry(partner_id)

    def _calculate_daily_revenue(self, monthly_revenue: Decimal) -> Decimal:
        """
        Calculate daily revenue based on current month's days.

        Args:
            monthly_revenue: Monthly revenue amount

        Returns:
            Daily revenue amount
        """
        current_date: datetime = datetime.now()
        days_in_month: int = calendar.monthrange(current_date.year, current_date.month)[1]
        return monthly_revenue / Decimal(days_in_month)


    def _calculate_partner_commission(self, partner_id: int) -> Decimal:

        partner: Dict = self.partners_data[partner_id]
        total_descendant_revenue: Decimal = Decimal('0')
        for child_id in partner['children']:
            child_daily_revenue = self._calculate_daily_revenue(
                self.partners_data[child_id]['monthly_revenue']
            )
            total_descendant_revenue += child_daily_revenue
            child_commission = self._calculate_partner_commission(child_id)
            if child_commission > 0:
                total_descendant_revenue += child_commission / self.COMMISSION_RATE

        commission = total_descendant_revenue * self.COMMISSION_RATE

        return commission.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


    def calculate_daily_commissions(self) -> Dict[str, float]:
        return {
            str(partner_id): float(self._calculate_partner_commission(partner_id))
            for partner_id in self.partners_data
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.input) as f:
        partners_data = json.load(f)

    calculator = MLMCommissionCalculator(partners_data)
    commissions = calculator.calculate_daily_commissions()

    with open(args.output, "w") as f:
        json.dump(commissions, f, indent=2)


if __name__ == "__main__":
    main()

# def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--input", required=True)
    # parser.add_argument("--output", required=True)
    # args = parser.parse_args()

    # with open("dataset.json") as f:
    #     partners = json.load(f)
    #
    # partners_by_id, children, roots = build_tree(partners)
    # if detect_cycles(partners_by_id, children, roots):
    #     print("Hierarchy error: cycle or orphan detected.")
    #     exit(1)
    #
    # commissions = compute_commissions(partners_by_id, children, roots)
    # with open("test.json", "w") as f:
    #     json.dump(commissions, f, indent=2)

# if __name__ == "__main__":
#     main()

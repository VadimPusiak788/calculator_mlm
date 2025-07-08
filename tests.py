import pytest
import json
import tempfile
from main import MLMCommissionCalculator


class TestMLMCommissionCalculator:
    def test_single_partner_no_descendants(self):
        """Test a single partner with no descendants has zero commission."""
        partners = [
            {
                "id": 1,
                "parent_id": None,
                "name": "Root Partner",
                "monthly_revenue": 10000
            }
        ]
        calculator = MLMCommissionCalculator(partners)
        commissions = calculator.calculate_daily_commissions()

        assert commissions['1'] == 0.0

    def test_two_level_hierarchy(self):
        """Test a two-level hierarchy with direct commission calculation."""
        partners = [
            {
                "id": 1,
                "parent_id": None,
                "name": "Root Partner",
                "monthly_revenue": 0
            },
            {
                "id": 2,
                "parent_id": 1,
                "name": "Child Partner",
                "monthly_revenue": 3100
            }
        ]
        calculator = MLMCommissionCalculator(partners)
        commissions = calculator.calculate_daily_commissions()

        assert commissions['1'] == 5.0
        assert commissions['2'] == 0.0

    def test_multi_level_hierarchy(self):
        """Test a complex multi-level hierarchy."""
        partners = [
            {"id": 1, "parent_id": None, "name": "Root", "monthly_revenue": 0},
            {"id": 2, "parent_id": 1, "name": "Level2A", "monthly_revenue": 3100},
            {"id": 3, "parent_id": 1, "name": "Level2B", "monthly_revenue": 6200},
            {"id": 4, "parent_id": 2, "name": "Level3A", "monthly_revenue": 9300},
            {"id": 5, "parent_id": 3, "name": "Level3B", "monthly_revenue": 12400},
            {"id": 6, "parent_id": 3, "name": "Level3C", "monthly_revenue": 15500}
        ]
        calculator = MLMCommissionCalculator(partners)
        commissions = calculator.calculate_daily_commissions()

        assert commissions['4'] == 0.0
        assert commissions['5'] == 0.0
        assert commissions['6'] == 0.0
        assert round(commissions['2'], 2) == 15.0
        assert round(commissions['3'], 2) == 45.0
        assert round(commissions['1'], 2) == 75.0

    def test_cycle_detection_direct_cycle(self):
        """Test cycle detection for direct circular reference."""
        partners = [
            {"id": 1, "parent_id": 2, "name": "Partner1", "monthly_revenue": 1000},
            {"id": 2, "parent_id": 1, "name": "Partner2", "monthly_revenue": 2000}
        ]

        with pytest.raises(ValueError, match="Cycle detected in partner hierarchy"):
            MLMCommissionCalculator(partners)

    def test_cycle_detection_multi_level_cycle(self):
        """Test cycle detection for multi-level circular reference."""
        partners = [
            {"id": 1, "parent_id": 3, "name": "Partner1", "monthly_revenue": 1000},
            {"id": 2, "parent_id": 1, "name": "Partner2", "monthly_revenue": 2000},
            {"id": 3, "parent_id": 2, "name": "Partner3", "monthly_revenue": 3000}
        ]

        with pytest.raises(ValueError, match="Cycle detected in partner hierarchy"):
            MLMCommissionCalculator(partners)

    def test_invalid_partner_id(self):
        """Test handling of invalid partner IDs."""
        partners = [
            {"id": "ID", "parent_id": None, "name": "Invalid Partner", "monthly_revenue": 1000}
        ]

        with pytest.raises(ValueError, match="Invalid partner ID"):
            MLMCommissionCalculator(partners)

    def test_duplicate_partner_id(self):
        """Test handling of duplicate partner IDs."""
        partners = [
            {"id": 1, "parent_id": None, "name": "Partner1", "monthly_revenue": 1000},
            {"id": 1, "parent_id": None, "name": "Partner2", "monthly_revenue": 2000}
        ]

        with pytest.raises(ValueError, match="Duplicate partner ID"):
            MLMCommissionCalculator(partners)

    def test_nonexistent_parent(self):
        """Test handling of partners with non-existent parent."""
        partners = [
            {"id": 2, "parent_id": 999, "name": "Partner", "monthly_revenue": 1000}
        ]

        with pytest.raises(ValueError, match="Parent 999 not found"):
            MLMCommissionCalculator(partners)

    def test_zero_revenue_partner(self):
        """Test partner with zero monthly revenue."""
        partners = [
            {"id": 1, "parent_id": None, "name": "Root", "monthly_revenue": 0},
            {"id": 2, "parent_id": 1, "name": "Child", "monthly_revenue": 0}
        ]

        calculator = MLMCommissionCalculator(partners)
        commissions = calculator.calculate_daily_commissions()

        assert commissions['1'] == 0.0
        assert commissions['2'] == 0.0

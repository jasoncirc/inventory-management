"""
Tests for reports API endpoints.
"""
import pytest


class TestReportsEndpoints:
    """Test suite for quarterly and monthly-trend report endpoints."""

    def test_get_quarterly_reports(self, client):
        """Test getting quarterly reports without filters."""
        response = client.get("/api/reports/quarterly")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        for quarter in data:
            assert "quarter" in quarter
            assert "total_orders" in quarter
            assert "total_revenue" in quarter
            assert "avg_order_value" in quarter
            assert "fulfillment_rate" in quarter
            assert 0 <= quarter["fulfillment_rate"] <= 100

    def test_quarterly_reports_sorted(self, client):
        """Test that quarterly reports are sorted by quarter."""
        data = client.get("/api/reports/quarterly").json()
        quarters = [q["quarter"] for q in data]
        assert quarters == sorted(quarters)

    def test_quarterly_totals_match_orders(self, client):
        """Test that quarterly order counts and revenue add up to all orders."""
        orders = client.get("/api/orders").json()
        data = client.get("/api/reports/quarterly").json()

        assert sum(q["total_orders"] for q in data) == len(orders)
        total_revenue = sum(o["total_value"] for o in orders)
        assert abs(sum(q["total_revenue"] for q in data) - total_revenue) < 0.01

    def test_get_quarterly_reports_by_warehouse(self, client):
        """Test that the warehouse filter narrows quarterly totals to matching orders."""
        orders = client.get("/api/orders?warehouse=Tokyo").json()
        data = client.get("/api/reports/quarterly?warehouse=Tokyo").json()

        assert sum(q["total_orders"] for q in data) == len(orders)

    def test_get_quarterly_reports_by_quarter(self, client):
        """Test that a quarter filter returns only that quarter."""
        response = client.get("/api/reports/quarterly?month=Q2-2025")
        assert response.status_code == 200

        data = response.json()
        assert [q["quarter"] for q in data] == ["Q2-2025"]

    def test_get_quarterly_reports_by_status(self, client):
        """Test that a Delivered-only filter yields 100% fulfillment."""
        data = client.get("/api/reports/quarterly?status=Delivered").json()
        assert len(data) > 0

        for quarter in data:
            assert quarter["fulfillment_rate"] == 100.0

    def test_get_quarterly_reports_no_matches(self, client):
        """Test that a filter with no matching orders returns an empty list."""
        response = client.get("/api/reports/quarterly?warehouse=Nonexistent")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_monthly_trends(self, client):
        """Test getting monthly trends without filters."""
        response = client.get("/api/reports/monthly-trends")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        months = [m["month"] for m in data]
        assert months == sorted(months)

        for month in data:
            assert "order_count" in month
            assert "revenue" in month
            assert "delivered_count" in month
            assert len(month["month"]) == 7  # YYYY-MM

    def test_get_monthly_trends_by_month(self, client):
        """Test that a single-month filter returns only that month."""
        data = client.get("/api/reports/monthly-trends?month=2025-03").json()
        assert [m["month"] for m in data] == ["2025-03"]

    def test_get_monthly_trends_multiple_filters(self, client):
        """Test that combined filters match the filtered orders endpoint."""
        query = "warehouse=San Francisco&category=Sensors&month=Q1-2025"
        orders = client.get(f"/api/orders?{query}").json()
        data = client.get(f"/api/reports/monthly-trends?{query}").json()

        assert sum(m["order_count"] for m in data) == len(orders)
        total_revenue = sum(o["total_value"] for o in orders)
        assert abs(sum(m["revenue"] for m in data) - total_revenue) < 0.01
        for month in data:
            assert month["month"] in ["2025-01", "2025-02", "2025-03"]

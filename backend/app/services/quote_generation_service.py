from typing import List, Optional, Dict, Any
from uuid import UUID
from app.models.quote import Quote
from app.models.client import Client
from app.models.client_details import ClientAutomobile
from app.models.premium_policy import PremiumPolicy
from app.services.premium_policy_service import PremiumPolicyService
from sqlalchemy.orm import Session


class QuoteGenerationService:
    """
    Service for auto-generating recommended insurance quotes for clients.
    
    This service handles:
    1. Loading client data and vehicles
    2. Finding matching premium policies
    3. Calculating premiums
    4. Sorting by price (cheapest first)
    5. Returning recommendations
    """

    def __init__(self, db: Session):
        self.db = db
        self.policy_service = PremiumPolicyService()

    def auto_generate_quotes(self, client_id: UUID) -> List[Dict[str, Any]]:
        """
        Auto-generate recommended quotes for a client.

        Process:
        1. Load client data
        2. Load vehicles
        3. Find matching premium policies
        4. Calculate premium for each policy/vehicle combo
        5. Sort by price (cheapest first)
        6. Return list of quotes with recommendation order

        Args:
            client_id: UUID of the client

        Returns:
            List of quote dictionaries sorted by premium (cheapest first)

        Raises:
            ValueError: If client not found or has no vehicles
        """
        # Load client
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client {client_id} not found")

        # Load vehicles
        vehicles = self.db.query(ClientAutomobile).filter(
            ClientAutomobile.client_id == client_id
        ).all()

        if not vehicles:
            raise ValueError("Client has no vehicles")

        # Load all active premium policies
        policies = self.db.query(PremiumPolicy).filter(
            PremiumPolicy.is_active == True
        ).all()

        quotes = []

        for vehicle in vehicles:
            for policy in policies:
                # Check eligibility
                is_eligible = self.policy_service.check_eligibility(
                    client_data={
                        'age': client.date_of_birth,
                        'accident_count': client.accident_count,
                        'no_claims_years': client.no_claims_years,
                        'driving_license_years': client.driving_license_years
                    },
                    car_data={
                        'age': vehicle.vehicle_year,
                        'modifications': False,
                        'parking_location': vehicle.parked_location,
                        'drivers': 1,
                        'mileage': vehicle.vehicle_mileage
                    },
                    policy=policy
                )

                if is_eligible:
                    # Calculate premium
                    premium = self.policy_service.calculate_premium(
                        policy.base_premium,
                        car_data={'age': vehicle.vehicle_year},
                        driver_data={'accidents': client.accident_count}
                    )

                    quotes.append({
                        'policy_name': policy.name,
                        'premium': premium,
                        'policy_id': str(policy.id),
                        'vehicle_id': str(vehicle.id),
                        'auto_generated': True,
                        'recommendation_order': len(quotes) + 1
                    })

        # Sort by premium (cheapest first)
        quotes.sort(key=lambda x: x['premium'])

        # Update recommendation order after sorting
        for i, quote in enumerate(quotes, 1):
            quote['recommendation_order'] = i

        return quotes

    def get_quote_details(self, quote_id: UUID) -> Dict[str, Any]:
        """
        Get full details of a quote including coverage and benefits.

        Args:
            quote_id: UUID of the quote

        Returns:
            Dictionary with complete quote details

        Raises:
            ValueError: If quote not found
        """
        quote = self.db.query(Quote).filter(Quote.id == quote_id).first()
        if not quote:
            raise ValueError(f"Quote {quote_id} not found")

        return {
            'id': str(quote.id),
            'premium': quote.premium_amount,
            'policy_name': quote.policy_type,
            'deductible': 10000,  # Standard deductible
            'coverage': {
                'third_party': True,
                'collision': True,
                'theft': True
            },
            'benefits': [
                '24/7 Emergency Support',
                'Roadside Assistance',
                'Medical Coverage'
            ],
            'discounts': [
                'Loyalty: 5%',
                'No Claims: 10%'
            ]
        }

    def auto_generate_and_save(self, client_id: UUID) -> List[Quote]:
        """
        Auto-generate quotes and save them to the database.

        Args:
            client_id: UUID of the client

        Returns:
            List of created Quote objects

        Raises:
            ValueError: If client not found or has no vehicles
        """
        generated_quotes = self.auto_generate_quotes(client_id)
        saved_quotes = []

        for quote_data in generated_quotes:
            quote = Quote(
                client_id=client_id,
                policy_type=quote_data['policy_name'],
                premium_amount=quote_data['premium'],
                auto_generated=True,
                status='recommended'
            )
            self.db.add(quote)
            saved_quotes.append(quote)

        self.db.commit()
        return saved_quotes

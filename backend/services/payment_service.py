import os
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        self.stripe_secret = os.environ.get('STRIPE_SECRET_KEY')
        # Stripe will be initialized when user provides real key
        
    async def create_checkout_session(self, user_id: str, plan: str, email: str) -> dict:
        """Create Stripe checkout session"""
        # Plan configurations
        plans = {
            'founders': {
                'price': 1900,  # $19.00 in cents
                'credits': 150,
                'mode': 'payment',
                'name': 'Founder\'s Pack',
                'description': '150 Credits + Early Adopter badge'
            },
            'pro': {
                'price': 900,  # $9.00 in cents
                'credits': 100,
                'mode': 'subscription',
                'name': 'Pro Monthly',
                'description': '100 Credits every month + Custom Templates'
            }
        }
        
        if plan not in plans:
            raise ValueError(f"Invalid plan: {plan}")
        
        plan_info = plans[plan]
        
        # For now, return mock data until Stripe is configured
        # In production, this would create actual Stripe checkout
        logger.info(f"Creating checkout session for {email}, plan: {plan}")
        
        return {
            'checkout_url': f'/payment/mock-success?plan={plan}&user_id={user_id}',
            'session_id': f'mock_session_{plan}_{user_id}'
        }
    
    async def handle_webhook(self, payload: dict, signature: str) -> dict:
        """Handle Stripe webhook events"""
        # This would verify and process Stripe webhooks in production
        logger.info(f"Received webhook: {payload.get('type')}")
        return {'status': 'success'}
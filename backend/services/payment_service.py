import os
import logging
import requests

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        self.dodo_api_key = os.environ.get('DODO_PAYMENTS_API_KEY')
        self.dodo_public_key = os.environ.get('DODO_PAYMENTS_PUBLIC_KEY')
        self.base_url = 'https://api.dodopayments.com/v1'
        
    async def create_checkout_session(self, user_id: str, plan: str, email: str) -> dict:
        """Create Dodo Payments checkout session"""
        # Plan configurations
        plans = {
            'pro': {
                'product_id': 'pdt_0NVGHVzjPDjC2IDdjCGG7',
                'price': 900,  # $9.00 in cents
                'credits': 100,
                'name': 'Pro Monthly',
                'description': '100 Credits every month',
                'billing': 'monthly'
            },
            'lifetime': {
                'product_id': 'pdt_0NVGHqByNTPrBoKH1pmDK',
                'price': 3900,  # $39.00 in cents
                'credits': 500,
                'name': 'Lifetime Access',
                'description': '500 Credits + Lifetime access',
                'billing': 'one-time'
            }
        }
        
        if plan not in plans:
            raise ValueError(f"Invalid plan: {plan}")
        
        plan_info = plans[plan]
        
        try:
            # Create Dodo Payments checkout session
            headers = {
                'Authorization': f'Bearer {self.dodo_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'product_id': plan_info['product_id'],
                'customer_email': email,
                'success_url': f'{os.environ.get("FRONTEND_URL", "http://localhost:3000")}/payment/success?plan={plan}&user_id={user_id}',
                'cancel_url': f'{os.environ.get("FRONTEND_URL", "http://localhost:3000")}/pricing',
                'metadata': {
                    'user_id': user_id,
                    'plan': plan,
                    'credits': plan_info['credits']
                }
            }
            
            response = requests.post(
                f'{self.base_url}/checkout/sessions',
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                logger.info(f"Created Dodo checkout session for {email}, plan: {plan}")
                return {
                    'checkout_url': data.get('checkout_url') or data.get('url'),
                    'session_id': data.get('id') or data.get('session_id')
                }
            else:
                logger.error(f"Dodo API error: {response.status_code} - {response.text}")
                raise Exception(f"Failed to create checkout session: {response.text}")
                
        except Exception as e:
            logger.error(f"Error creating Dodo checkout: {str(e)}")
            raise
    
    async def handle_webhook(self, payload: dict, signature: str) -> dict:
        """Handle Dodo Payments webhook events"""
        logger.info(f"Received Dodo webhook: {payload.get('event_type')}")
        return {'status': 'success'}
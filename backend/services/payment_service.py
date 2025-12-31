import os
import logging
import requests

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        self.dodo_api_key = os.environ.get('DODO_PAYMENTS_API_KEY')
        self.dodo_public_key = os.environ.get('DODO_PAYMENTS_PUBLIC_KEY')
        self.base_url = 'https://api.dodopayments.com'
        
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
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
        
        try:
            # Create Dodo Payments checkout session using the correct endpoint
            headers = {
                'Authorization': f'Bearer {self.dodo_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'type': 'session',
                'product_cart': [
                    {
                        'product_id': plan_info['product_id'],
                        'quantity': 1
                    }
                ],
                'customer': {
                    'email': email
                },
                'return_url': f'{frontend_url}/payment/success?plan={plan}&user_id={user_id}',
                'metadata': {
                    'user_id': user_id,
                    'plan': plan,
                    'credits': str(plan_info['credits'])
                }
            }
            
            response = requests.post(
                f'{self.base_url}/checkouts',
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                logger.info(f"Created Dodo checkout session for {email}, plan: {plan}")
                return {
                    'checkout_url': data.get('checkout_url'),
                    'session_id': data.get('id') or data.get('checkout_id')
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
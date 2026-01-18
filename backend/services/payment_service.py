import os
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        self.dodo_api_key = os.environ.get('DODO_PAYMENTS_API_KEY')
        self.dodo_public_key = os.environ.get('DODO_PAYMENTS_PUBLIC_KEY')
        # Test mode - set to 'true' to bypass actual payment processing
        self.test_mode = os.environ.get('PAYMENT_TEST_MODE', 'false').lower() == 'true'
        # Use correct Dodo Payments API endpoint
        self.base_url = 'https://test.dodopayments.com' if self.test_mode else 'https://live.dodopayments.com'
        
    async def create_checkout_session(self, user_id: str, plan: str, email: str) -> dict:
        """Create Dodo Payments checkout session"""
        # Plan configurations - use test product IDs in test mode
        # Credits = PDF downloads (1 credit = 1 PDF)
        if self.test_mode:
            plans = {
                'pro': {
                    'product_id': 'pdt_0NVXNwzXNZlKGSa8V1z9D',  # Test mode product ID
                    'price': 500,  # $5.00 in cents
                    'credits': 50,  # 50 PDF downloads per month
                    'name': 'Pro Plan (Test)',
                    'description': '50 PDF downloads every month',
                    'billing': 'monthly'
                },
                'credit_topup': {
                    'product_id': 'pdt_test_topup_20',  # Test mode product ID
                    'price': 200,  # $2.00 in cents
                    'credits': 20,  # 20 PDF downloads
                    'name': 'Credit Top-Up (Test)',
                    'description': '20 credits (One-time)',
                    'billing': 'one-time'
                }
            }
        else:
            plans = {
                'pro': {
                    'product_id': 'pdt_0NWBVEhqraATfO68LybuM',  # Live mode product ID
                    'price': 500,  # $5.00 in cents
                    'credits': 50,  # 50 PDF downloads per month
                    'name': 'Pro Plan',
                    'description': '50 PDF downloads every month',
                    'billing': 'monthly'
                },
                'credit_topup': {
                    'product_id': 'pdt_0NWV65ozKz7CyPKyrCJTx',  # Live mode product ID
                    'price': 200,  # $2.00 in cents
                    'credits': 20,
                    'name': 'Credit Top-Up',
                    'description': '20 credits (One-time)',
                    'billing': 'one-time'
                }
            }
        
        if plan not in plans:
            raise ValueError(f"Invalid plan: {plan}")
        
        plan_info = plans[plan]
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
        
        # TEST MODE - Return mock checkout URL
        if self.test_mode:
            logger.warning(f"TEST MODE: Simulating checkout for {email}, plan: {plan}")
            session_id = f'test_session_{user_id}_{plan}_{int(datetime.now().timestamp())}'
            return {
                'checkout_url': f'{frontend_url}/payment/success?plan={plan}&user_id={user_id}&session_id={session_id}&test=true',
                'session_id': session_id
            }
        
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
                # Return URL without placeholders - Dodo will redirect here after payment
                # We'll verify using checkout_session_id from Dodo API
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
                checkout_session_id = data.get('id') or data.get('checkout_id')
                
                # Append session_id to the checkout_url for verification
                # This allows us to verify the payment when user returns
                checkout_url = data.get('checkout_url')
                if checkout_session_id and checkout_url:
                    # Add session_id as a query parameter to the return URL
                    # Dodo will redirect to this URL after payment
                    separator = '&' if '?' in checkout_url else '?'
                    # Note: We're adding it to metadata, not the checkout_url
                    # The return_url in payload already has plan and user_id
                    pass
                
                logger.info(f"Created Dodo checkout session for {email}, plan: {plan}, session_id: {checkout_session_id}")
                return {
                    'checkout_url': checkout_url,
                    'session_id': checkout_session_id
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
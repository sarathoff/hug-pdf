"""
Credit Service - Manages user credits and feature limits across tiers

This service handles:
- Credit checking before feature usage
- Credit deduction after usage
- Monthly credit resets
- Credit pack purchases
- Usage tracking and analytics
"""

from supabase import Client
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging
from backend.core.config import settings

logger = logging.getLogger(__name__)

class CreditService:
    """Manage credits and feature limits for tiered pricing"""
    
    # Plan configurations
    PLAN_LIMITS = {
        'free': {
            'research_credits': 0,
            'diagram_credits': 0,
            'ebook_credits': 0,
            'pdf_limit': 5,  # 5 free PDFs
            'model': 'gemini-2.5-pro',
            'perplexity_enabled': False
        },
        'starter': {
            'research_credits': 2,
            'diagram_credits': 5,
            'ebook_credits': 0,
            'pdf_limit': 100,
            'model': 'gemini-2.5-pro',
            'perplexity_enabled': False  # Use Google Search instead
        },
        'pro': {
            'research_credits': 15,
            'diagram_credits': 25,
            'ebook_credits': 2,
            'pdf_limit': -1,  # Unlimited
            'model': 'gemini-2.5-pro',
            'perplexity_enabled': True
        },
        'power': {
            'research_credits': 50,
            'diagram_credits': -1,  # Unlimited
            'ebook_credits': 10,
            'pdf_limit': -1,  # Unlimited
            'model': 'gemini-2.5-pro',
            'perplexity_enabled': True
        }
    }
    
    @staticmethod
    def determine_plan_from_credits(credits: int) -> str:
        """
        Determine user plan based on credit count
        
        Args:
            credits: Total credits user has
            
        Returns:
            'pro' if credits > 5, else 'free'
        """
        return 'pro' if credits > 5 else 'free'
    
    def __init__(self, supabase_admin: Client):
        """Initialize with admin Supabase client to bypass RLS"""
        self.db = supabase_admin
    
    def get_user_credits(self, user_id: str) -> Optional[Dict]:
        """Get current credit status for user"""
        try:
            response = self.db.table("users").select("*").eq("user_id", user_id).execute()
            
            if not response.data:
                return None
            
            user = response.data[0]
            
            # Check if credits need monthly reset
            reset_date = user.get('credits_reset_date')
            if reset_date and datetime.now() > datetime.fromisoformat(reset_date):
                logger.info(f"Resetting monthly credits for user {user_id}")
                self.reset_monthly_credits(user_id, user['plan'])
                # Fetch updated data
                response = self.db.table("users").select("*").eq("user_id", user_id).execute()
                user = response.data[0]
            
            return {
                'plan': user['plan'],
                'research_credits': user.get('research_credits', 0),
                'diagram_credits': user.get('diagram_credits', 0),
                'ebook_credits': user.get('ebook_credits', 0),
                'pdf_downloads': user.get('pdf_downloads', 0),
                'pdf_limit': self.PLAN_LIMITS[user['plan']]['pdf_limit'],
                'credits_reset_date': user.get('credits_reset_date')
            }
        except Exception as e:
            logger.error(f"Error getting user credits: {str(e)}")
            return None
    
    def check_credit_available(self, user_id: str, credit_type: str) -> tuple[bool, str]:
        """
        Check if user has credits available for a feature
        
        Args:
            user_id: User ID
            credit_type: 'research', 'diagram', 'ebook', or 'pdf'
        
        Returns:
            (has_credit: bool, message: str)
        """
        credits = self.get_user_credits(user_id)
        
        if not credits:
            return False, "User not found"
        
        plan = credits['plan']
        
        # Check unlimited features
        if credit_type == 'diagram' and plan == 'power':
            return True, "Unlimited diagrams"
        
        if credit_type == 'pdf' and plan in ['pro', 'power']:
            return True, "Unlimited PDFs"
        
        # Check credit limits
        credit_field = f"{credit_type}_credits" if credit_type != 'pdf' else 'pdf_downloads'
        current_value = credits.get(credit_field, 0)
        
        if credit_type == 'pdf':
            limit = credits['pdf_limit']
            if limit == -1:  # Unlimited
                return True, "Unlimited PDFs"
            if current_value >= limit:
                return False, f"PDF download limit reached ({limit}/month). Upgrade to Pro for unlimited PDFs."
        else:
            if current_value <= 0:
                upgrade_messages = {
                    'research': "No research credits remaining. Upgrade to Pro (15/mo) or Power (50/mo) for more.",
                    'diagram': "No diagram credits remaining. Upgrade to Pro (25/mo) or Power (unlimited) for more.",
                    'ebook': "E-book mode requires Pro (2/mo) or Power (10/mo) plan."
                }
                return False, upgrade_messages.get(credit_type, "Insufficient credits")
        
        return True, "Credit available"
    
    def deduct_credit(self, user_id: str, credit_type: str, reason: str = "") -> bool:
        """
        Deduct one credit from user's account
        
        Returns:
            True if successful, False otherwise
        """
        try:
            credits = self.get_user_credits(user_id)
            
            if not credits:
                return False
            
            plan = credits['plan']
            
            # Don't deduct for unlimited features
            if credit_type == 'diagram' and plan == 'power':
                return True
            if credit_type == 'pdf' and plan in ['pro', 'power']:
                return True
            
            # Deduct credit
            if credit_type == 'pdf':
                new_value = credits['pdf_downloads'] + 1
                update_field = 'pdf_downloads'
            else:
                credit_field = f"{credit_type}_credits"
                current_credits = credits.get(credit_field, 0)
                
                if current_credits <= 0:
                    return False
                
                new_value = current_credits - 1
                update_field = credit_field
            
            # Update database
            self.db.table("users").update({
                update_field: new_value,
                'updated_at': datetime.now().isoformat()
            }).eq("user_id", user_id).execute()
            
            # Log transaction
            self.db.table("credit_transactions").insert({
                "user_id": user_id,
                "credit_type": credit_type,
                "amount": -1,
                "transaction_type": "deduct",
                "reason": reason or f"Used {credit_type} feature"
            }).execute()
            
            logger.info(f"Deducted {credit_type} credit from user {user_id}. New value: {new_value}")
            return True
            
        except Exception as e:
            logger.error(f"Error deducting credit: {str(e)}")
            return False
    
    def reset_monthly_credits(self, user_id: str, plan: str):
        """Reset user's credits based on their plan (called monthly)"""
        try:
            plan_config = self.PLAN_LIMITS.get(plan, self.PLAN_LIMITS['starter'])
            
            self.db.table("users").update({
                'research_credits': plan_config['research_credits'],
                'diagram_credits': plan_config['diagram_credits'],
                'ebook_credits': plan_config['ebook_credits'],
                'pdf_downloads': 0,
                'credits_reset_date': (datetime.now() + timedelta(days=30)).isoformat(),
                'updated_at': datetime.now().isoformat()
            }).eq("user_id", user_id).execute()
            
            # Log reset
            self.db.table("credit_transactions").insert({
                "user_id": user_id,
                "credit_type": "all",
                "amount": 0,
                "transaction_type": "reset",
                "reason": f"Monthly reset for {plan} plan"
            }).execute()
            
            logger.info(f"Reset monthly credits for user {user_id} on {plan} plan")
            
        except Exception as e:
            logger.error(f"Error resetting credits: {str(e)}")
    
    def add_credit_pack(self, user_id: str, pack_type: str = 'research', credits: int = 1) -> bool:
        """
        Add credits from purchased credit pack
        
        Args:
            user_id: User ID
            pack_type: Type of credits ('research', 'diagram', 'ebook')
            credits: Number of credits to add
        """
        try:
            current_credits = self.get_user_credits(user_id)
            
            if not current_credits:
                return False
            
            credit_field = f"{pack_type}_credits"
            new_value = current_credits.get(credit_field, 0) + credits
            
            # Determine new plan based on total credits
            # For simplicity, we'll use the main credit field or sum all credits
            # Assuming 'credits' field exists in users table for total credits
            total_credits = new_value  # This assumes pack_type credits = total credits
            new_plan = self.determine_plan_from_credits(total_credits)
            
            self.db.table("users").update({
                credit_field: new_value,
                'plan': new_plan,
                'updated_at': datetime.now().isoformat()
            }).eq("user_id", user_id).execute()
            
            # Log transaction
            self.db.table("credit_transactions").insert({
                "user_id": user_id,
                "credit_type": pack_type,
                "amount": credits,
                "transaction_type": "add",
                "reason": f"Purchased {credits} {pack_type} credit(s)"
            }).execute()
            
            logger.info(f"Added {credits} {pack_type} credits to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding credit pack: {str(e)}")
            return False
    
    def get_plan_config(self, plan: str) -> Dict:
        """Get configuration for a specific plan"""
        return self.PLAN_LIMITS.get(plan, self.PLAN_LIMITS['starter'])
    
    def upgrade_user_plan(self, user_id: str, new_plan: str) -> bool:
        """
        Upgrade user to a new plan and reset credits
        
        Args:
            user_id: User ID
            new_plan: 'starter', 'pro', or 'power'
        """
        try:
            if new_plan not in self.PLAN_LIMITS:
                logger.error(f"Invalid plan: {new_plan}")
                return False
            
            plan_config = self.PLAN_LIMITS[new_plan]
            
            self.db.table("users").update({
                'plan': new_plan,
                'research_credits': plan_config['research_credits'],
                'diagram_credits': plan_config['diagram_credits'],
                'ebook_credits': plan_config['ebook_credits'],
                'pdf_downloads': 0,
                'credits_reset_date': (datetime.now() + timedelta(days=30)).isoformat(),
                'updated_at': datetime.now().isoformat()
            }).eq("user_id", user_id).execute()
            
            logger.info(f"Upgraded user {user_id} to {new_plan} plan")
            return True
            
        except Exception as e:
            logger.error(f"Error upgrading user plan: {str(e)}")
            return False

import uuid
import time
import logging
from DatabaseService import DatabaseService

logger = logging.getLogger(__name__)

class TokenService:
    """
    Service for managing debate access tokens.
    Handles generation, insertion, and lifecycle of tokens.
    """
    
    def __init__(self):
        self.db = DatabaseService()
        # Default TTL: 24 hours in seconds
        self.DEFAULT_TTL_SECONDS = 24 * 60 * 60

    def generate_available_token(self, payment_id: str, email: str, ttl_hours: int = 24) -> dict:
        """
        Generates a new token, inserts it into DynamoDB with AVAILABLE status,
        and returns the created token data.
        
        Args:
            payment_id: The Stripe/PayPal session ID.
            ttl_hours: How many hours until the token expires (default 24).
            
        Returns:
            dict: The created token item if successful, None otherwise.
        """
        token_id = str(uuid.uuid4())
        now = int(time.time())
        ttl = now + (ttl_hours * 60 * 60)
        
        token_data = {
            'TOKEN_ID': token_id, # Matching the PK name in DatabaseService
            'STATUS': 'AVAILABLE',
            'PAYMENT_ID': payment_id,
            'EMAIL': email,
            'CREATED_AT': now,
            'TTL': ttl,
            'REQUEST_COUNT': 10
        }
        
        logger.info(f"Attempting to create token: {token_id} for payment: {payment_id}")
        
        success = self.db.create_token(token_id, token_data)
        
        if success:
            logger.info(f"Successfully created token: {token_id}")
            return token_data
        else:
            logger.error(f"Failed to create token in database for payment: {payment_id}")
            return None

    

if __name__ == "__main__":
    # Quick test script
    logging.basicConfig(level=logging.INFO)
    service = TokenService()
    
    test_payment = f"test_pay_{int(time.time())}"
    test_payment = "try"
    new_token = service.generate_available_token(test_payment, "try@email.com")
    
    
    if new_token:
        print(f"Token Created: {new_token['TOKEN_ID']}")
        print(f"Status: {new_token['STATUS']}")
        print(f"Request Count: {new_token['REQUEST_COUNT']}")
        print(f"Expires at: {time.ctime(new_token['TTL'])}")
    else:
        print("Failed to create token.")

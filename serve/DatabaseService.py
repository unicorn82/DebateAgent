import boto3
import os
import logging
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import time
from typing import Optional

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Service for interacting with DynamoDB for access control and data persistence.
    """
    
    def __init__(self):
        # Configuration from environment variables
        self.endpoint_url = os.getenv("DYNAMODB_ENDPOINT_URL")
        self.region_name = os.getenv("AWS_REGION", "us-east-1")
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.table_name = "DEBATE_ACCESS_CONTROL"
        
        # Initialize DynamoDB resource
        try:
            params = {
                'region_name': self.region_name
            }
            if self.endpoint_url:
                params['endpoint_url'] = self.endpoint_url
            if self.access_key:
                params['aws_access_key_id'] = self.access_key
            if self.secret_key:
                params['aws_secret_access_key'] = self.secret_key
                
            self.dynamodb = boto3.resource('dynamodb', **params)
            self.table = self.dynamodb.Table(self.table_name)
            if self.endpoint_url:
                logger.info(f"Connected to DynamoDB at {self.endpoint_url}")
            else:
                logger.info(f"Connected to AWS DynamoDB in {self.region_name}")
        except Exception as e:
            logger.error(f"Failed to connect to DynamoDB: {str(e)}")
            self.dynamodb = None
            self.table = None

    def validate_token(self, token_id: str) -> bool:
        """
        Check if a TOKEN_ID exists in the DEBATE_ACCESS_CONTROL table.
        """
        if not self.table:
            logger.error("DynamoDB table not initialized")
            return False
            
        try:
            from boto3.dynamodb.conditions import Key
            response = self.table.query(
                KeyConditionExpression=Key('TOKEN_ID').eq(token_id)
            )
            return len(response.get('Items', [])) > 0
        except ClientError as e:
            logger.error(f"Error validating token: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error validating token: {str(e)}")
            return False

    def get_token_data(self, token_id: str) -> dict:
        """
        Retrieve all data associated with a TOKEN_ID.
        Uses query because STATUS is a Sort Key.
        """
        if not self.table:
            return None
            
        try:
            from boto3.dynamodb.conditions import Key
            response = self.table.query(
                KeyConditionExpression=Key('TOKEN_ID').eq(token_id)
            )
            items = response.get('Items', [])
            if not items:
                logger.warning(f"Token {token_id} not found in database")
                return None
                
            # If there are multiple items (e.g. AVAILABLE and USED), 
            # we probably want the one that isn't USED yet, or just the first one.
            # For now, let's take the first one found.
            item = items[0]
            
            # Check if the token is expired
            ttl = item.get('TTL')
            if ttl is not None:
                try:
                    if int(ttl) < int(time.time()):
                        logger.warning(f"Token {token_id} expired. TTL: {ttl}, Now: {int(time.time())}")
                        return None
                except (ValueError, TypeError) as e:
                    logger.error(f"Error parsing TTL for token {token_id}: {e}")
            
            # Check if the token is used
            if item.get('STATUS') == 'USED':
                logger.warning(f"Token {token_id} has STATUS=USED")
                return None
                
            return item
        except Exception as e:
            logger.error(f"Error retrieving token data for {token_id}: {str(e)}")
            return None

    def create_token(self, token_id: str, data: dict = None) -> bool:
        """
        Create a new token entry in the database.
        """
        if not self.table:
            return False
            
        item = {'TOKEN_ID': token_id}
        if data:
            item.update(data)
            
        try:
            self.table.put_item(Item=item)
            return True
        except Exception as e:
            logger.error(f"Error creating token: {str(e)}")
            return False
    
    def mark_token_as_used(self, token_id: str) -> bool:
        """
        Updates a token status to USED.
        """
        token_data = self.get_token_data(token_id)
        if not token_data:
            return False
            
        old_status = token_data.get('STATUS')
        if old_status == 'USED':
            return True
            
        token_data['STATUS'] = 'USED'
        
        # Delete old item because STATUS is a Sort Key
        try:
            self.table.delete_item(Key={'TOKEN_ID': token_id, 'STATUS': old_status})
        except Exception as e:
            logger.error(f"Error deleting old token item in mark_token_as_used: {e}")
            
        return self.create_token(token_id, token_data)

    def decrement_request_count(self, token_id: str) -> Optional[int]:
        """
        Decrements the request count for a token and returns the new count.
        Returns None if token not found or already at 0.
        """
        token_data = self.get_token_data(token_id)
        if not token_data:
            return None
        
        old_status = token_data.get('STATUS')
        count = token_data.get('REQUEST_COUNT', 0)
        if count <= 0:
            self.mark_token_as_used(token_id)
            return 0
            
        new_count = count - 1
        token_data['REQUEST_COUNT'] = new_count
        
        if new_count <= 0:
            token_data['STATUS'] = 'USED'
            
        new_status = token_data.get('STATUS')
        
        # If status changed, we need to delete the old item because STATUS is a Sort Key
        if old_status != new_status:
            try:
                self.table.delete_item(Key={'TOKEN_ID': token_id, 'STATUS': old_status})
            except Exception as e:
                logger.error(f"Error deleting old token item: {e}")

        if self.create_token(token_id, token_data):
            return new_count
        return None
        

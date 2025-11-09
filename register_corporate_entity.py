#!/usr/bin/env python3
"""
Corporate Entity Registration Script

This script registers a new corporate entity in the database and publishes 
an event to NATS JetStream with the registration details.

Environment Variables Required:
- COMPANY_DATA: The full company data in JSON format
- COMPANY_NAME: Name of the corporate entity
- SUBSCRIPTION_TIER: Subscription tier (basic, groovy, far-out)
- DB_HOST: Database host
- DB_PORT: Database port (default: 3306)
- DB_USER: Database username
- DB_PASSWORD: Database password
- DB_NAME: Database name
- NATS_SERVER: NATS server URL
- NATS_STREAM: JetStream stream name
- NATS_SUBJECT: Subject for the event
- NATS_USER: NATS username
- NATS_PASSWORD: NATS password
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid

import mysql.connector
from mysql.connector import Error
import nats


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass


class NATSError(Exception):
    """Custom exception for NATS operations"""
    pass


class CorporateEntityRegistrar:
    """Handles corporate entity registration and event publishing"""
    
    def __init__(self):
        self.company_info = self._load_company_info()
        self.db_config = self._load_db_config()
        self.nats_config = self._load_nats_config()
        
    def _load_company_info(self) -> Dict[str, Any]:
        """Load company information from environment variables"""
        required_vars = ['COMPANY_DATA', 'COMPANY_NAME', 'SUBSCRIPTION_TIER']
        company_info = {}
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                raise ValueError(f"Required environment variable {var} not set")
            company_info[var.lower().replace('_', '')] = value
            
        # Parse COMPANY_DATA JSON string into a dict
        try:
            company_info['companydata'] = json.loads(company_info['companydata'])
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in COMPANY_DATA: {e}")
            
        # Validate subscription tier
        valid_tiers = ['basic', 'groovy', 'far-out']
        if company_info['subscriptiontier'] not in valid_tiers:
            raise ValueError(f"Invalid subscription tier. Must be one of: {', '.join(valid_tiers)}")
            
        logger.info(f"Loaded company info for: {company_info['companyname']}")
        return company_info
        
    def _load_db_config(self) -> Dict[str, Any]:
        """Load database configuration from environment variables"""
        db_config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
            'charset': 'utf8mb4',
            'autocommit': True
        }
        
        # Check required fields
        required_fields = ['host', 'user', 'password', 'database']
        for field in required_fields:
            if not db_config[field]:
                raise ValueError(f"Required database configuration {field} not set")
                
        logger.info(f"Database config loaded for host: {db_config['host']}")
        return db_config
        
    def _load_nats_config(self) -> Dict[str, str]:
        """Load NATS configuration from environment variables"""
        nats_config = {
            'server': os.getenv('NATS_SERVER'),
            'stream': os.getenv('NATS_STREAM'),
            'subject': os.getenv('NATS_SUBJECT'),
            'user': os.getenv('NATS_USER'),
            'password': os.getenv('NATS_PASSWORD')
        }
        
        for key, value in nats_config.items():
            if not value:
                raise ValueError(f"Required NATS configuration {key} not set")
                
        logger.info(f"NATS config loaded for server: {nats_config['server']}")
        return nats_config

    def register_corporate_entity(self) -> str:
        """
        Register a new corporate entity in the database
        
        Returns:
            str: The UUID of the newly created corporate customer
        """
        connection = None
        try:
            # Connect to database
            connection = mysql.connector.connect(**self.db_config)
            
            if connection.is_connected():
                logger.info("Successfully connected to MySQL database")
                
                cursor = connection.cursor()
                
                # Generate UUID for the new customer
                customer_id = str(uuid.uuid4())
                
                # Insert corporate customer
                insert_query = """
                    INSERT INTO corporate_customers (id, name, subscription_tier) 
                    VALUES (%s, %s, %s)
                """
                
                cursor.execute(insert_query, (
                    customer_id,
                    self.company_info['companyname'],
                    self.company_info['subscriptiontier']
                ))
                
                # Verify the insertion
                if cursor.rowcount == 1:
                    logger.info(f"Successfully registered corporate entity: {self.company_info['companyname']} "
                              f"with ID: {customer_id}")
                    return customer_id
                else:
                    raise DatabaseError("Failed to insert corporate customer")
                    
        except Error as e:
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
            
        finally:
            if connection and connection.is_connected():
                connection.close()
                logger.info("Database connection closed")

    async def publish_registration_event(self, customer_id: str) -> None:
        """
        Publish registration event to NATS JetStream
        
        Args:
            customer_id: The UUID of the registered corporate customer
        """
        try:
            # Connect to NATS
            nc = await nats.connect(servers=[self.nats_config['server']], user=self.nats_config['user'], password=self.nats_config['password'])
            logger.info(f"Connected to NATS server: {self.nats_config['server']}")
            
            # Create JetStream context
            js = nc.jetstream()
            
            # Prepare CloudEvents payload
            event_data = {
                'specversion': '1.0',
                'type': 'disco.knapscen.customer.saved',
                'source': 'knapscen.disco',
                'subject': customer_id,
                'id': str(uuid.uuid4())[:8],
                'time': datetime.now(timezone.utc).isoformat(),
                'datacontenttype': 'application/json',
                'data': {
                    'name': self.company_info['companyname'],
                    'subscription_tier': self.company_info['subscriptiontier'],
                    'users': self.company_info['companydata'].get('users', [])
                }
            }
            
            # Publish to JetStream
            ack = await js.publish(
                self.nats_config['subject'],
                json.dumps(event_data).encode('utf-8')
            )
            
            logger.info(f"Published registration event to stream '{self.nats_config['stream']}' "
                       f"with subject '{self.nats_config['subject']}', sequence: {ack.seq}")
            
            await nc.close()
            logger.info("NATS connection closed")
            
        except Exception as e:
            logger.error(f"NATS publishing error: {e}")
            raise NATSError(f"Failed to publish event to NATS: {e}")

    async def run(self) -> None:
        """Main execution method"""
        try:
            logger.info("Starting corporate entity registration process...")
            
            # Register in database
            customer_id = self.register_corporate_entity()
            
            # Publish event to NATS JetStream
            await self.publish_registration_event(customer_id)
            
            logger.info("Corporate entity registration completed successfully")
            
        except (ValueError, DatabaseError, NATSError) as e:
            logger.error(f"Registration failed: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            sys.exit(1)


async def main():
    """Entry point"""
    try:
        registrar = CorporateEntityRegistrar()
        await registrar.run()
    except Exception as e:
        logger.error(f"Failed to initialize registrar: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

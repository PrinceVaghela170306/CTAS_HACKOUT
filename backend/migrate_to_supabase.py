#!/usr/bin/env python3
"""
Migration script to transition from legacy authentication to Supabase Auth integration.

This script helps migrate existing users and update the system to use Supabase Auth
while maintaining backward compatibility during the transition period.

Usage:
    python migrate_to_supabase.py [--dry-run] [--batch-size=100]

Options:
    --dry-run       Show what would be migrated without making changes
    --batch-size    Number of users to process in each batch (default: 100)
"""

import asyncio
import argparse
import sys
from typing import List, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.core.supabase import get_supabase_client
from app.core.config import settings


class SupabaseMigrator:
    def __init__(self, dry_run: bool = False, batch_size: int = 100):
        self.dry_run = dry_run
        self.batch_size = batch_size
        self.supabase = get_supabase_client()
        self.stats = {
            'total_users': 0,
            'migrated_users': 0,
            'skipped_users': 0,
            'failed_users': 0,
            'errors': []
        }

    def log(self, message: str, level: str = 'INFO'):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")

    def validate_supabase_connection(self) -> bool:
        """Validate Supabase connection and configuration"""
        try:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                self.log("Supabase configuration missing. Please check SUPABASE_URL and SUPABASE_KEY.", "ERROR")
                return False

            # Test connection by trying to get auth users
            response = self.supabase.auth.admin.list_users()
            if hasattr(response, 'error') and response.error:
                self.log(f"Supabase connection failed: {response.error}", "ERROR")
                return False

            self.log("Supabase connection validated successfully")
            return True
        except Exception as e:
            self.log(f"Failed to validate Supabase connection: {str(e)}", "ERROR")
            return False

    def get_legacy_users(self, db: Session, offset: int = 0) -> List[User]:
        """Get batch of legacy users that need migration"""
        return (
            db.query(User)
            .filter(User.supabase_id.is_(None))  # Users without Supabase ID
            .offset(offset)
            .limit(self.batch_size)
            .all()
        )

    def create_supabase_user(self, user: User) -> Dict[str, Any]:
        """Create user in Supabase Auth"""
        try:
            # Generate a temporary password for migration
            temp_password = f"temp_{user.id}_{datetime.now().strftime('%Y%m%d')}"
            
            user_data = {
                'email': user.email,
                'password': temp_password,
                'email_confirm': True,  # Skip email confirmation for migrated users
                'user_metadata': {
                    'full_name': user.full_name or '',
                    'phone_number': user.phone_number or '',
                    'migrated_from_legacy': True,
                    'legacy_user_id': str(user.id),
                    'migration_date': datetime.now().isoformat()
                }
            }

            if self.dry_run:
                self.log(f"[DRY RUN] Would create Supabase user for: {user.email}")
                return {'success': True, 'user_id': f'mock_uuid_{user.id}'}

            response = self.supabase.auth.admin.create_user(user_data)
            
            if hasattr(response, 'error') and response.error:
                return {'success': False, 'error': response.error}
            
            return {
                'success': True, 
                'user_id': response.user.id,
                'temp_password': temp_password
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_legacy_user(self, db: Session, user: User, supabase_user_id: str) -> bool:
        """Update legacy user with Supabase ID"""
        try:
            if self.dry_run:
                self.log(f"[DRY RUN] Would update user {user.email} with Supabase ID: {supabase_user_id}")
                return True

            user.supabase_id = supabase_user_id
            user.updated_at = datetime.utcnow()
            db.commit()
            return True
        except Exception as e:
            self.log(f"Failed to update user {user.email}: {str(e)}", "ERROR")
            db.rollback()
            return False

    def migrate_user_batch(self, db: Session, users: List[User]) -> None:
        """Migrate a batch of users"""
        for user in users:
            self.stats['total_users'] += 1
            
            try:
                # Skip users that already have Supabase ID
                if user.supabase_id:
                    self.log(f"Skipping user {user.email} - already has Supabase ID")
                    self.stats['skipped_users'] += 1
                    continue

                # Create Supabase user
                result = self.create_supabase_user(user)
                
                if not result['success']:
                    error_msg = f"Failed to create Supabase user for {user.email}: {result.get('error', 'Unknown error')}"
                    self.log(error_msg, "ERROR")
                    self.stats['failed_users'] += 1
                    self.stats['errors'].append(error_msg)
                    continue

                # Update legacy user with Supabase ID
                if self.update_legacy_user(db, user, result['user_id']):
                    self.log(f"Successfully migrated user: {user.email}")
                    self.stats['migrated_users'] += 1
                    
                    # Log temporary password for user notification
                    if 'temp_password' in result:
                        self.log(f"Temporary password for {user.email}: {result['temp_password']}")
                else:
                    self.stats['failed_users'] += 1

            except Exception as e:
                error_msg = f"Unexpected error migrating user {user.email}: {str(e)}"
                self.log(error_msg, "ERROR")
                self.stats['failed_users'] += 1
                self.stats['errors'].append(error_msg)

    def run_migration(self) -> bool:
        """Run the complete migration process"""
        self.log("Starting Supabase migration process")
        
        if self.dry_run:
            self.log("Running in DRY RUN mode - no changes will be made")

        # Validate Supabase connection
        if not self.validate_supabase_connection():
            return False

        # Get database session
        db = next(get_db())
        
        try:
            offset = 0
            while True:
                # Get batch of users to migrate
                users = self.get_legacy_users(db, offset)
                
                if not users:
                    break

                self.log(f"Processing batch of {len(users)} users (offset: {offset})")
                self.migrate_user_batch(db, users)
                
                offset += self.batch_size

            # Print migration summary
            self.print_summary()
            return True

        except Exception as e:
            self.log(f"Migration failed with error: {str(e)}", "ERROR")
            return False
        finally:
            db.close()

    def print_summary(self):
        """Print migration summary"""
        self.log("=" * 50)
        self.log("MIGRATION SUMMARY")
        self.log("=" * 50)
        self.log(f"Total users processed: {self.stats['total_users']}")
        self.log(f"Successfully migrated: {self.stats['migrated_users']}")
        self.log(f"Skipped (already migrated): {self.stats['skipped_users']}")
        self.log(f"Failed migrations: {self.stats['failed_users']}")
        
        if self.stats['errors']:
            self.log("\nERRORS:")
            for error in self.stats['errors']:
                self.log(f"  - {error}")
        
        if self.dry_run:
            self.log("\nNOTE: This was a dry run. No actual changes were made.")
        else:
            self.log("\nMigration completed. Users will need to reset their passwords.")


def create_password_reset_script():
    """Create a script to help users reset their passwords after migration"""
    script_content = '''
#!/usr/bin/env python3
"""
Password Reset Helper for Migrated Users

This script helps send password reset emails to users who were migrated
from the legacy authentication system to Supabase Auth.
"""

import csv
from app.core.supabase import get_supabase_client

def send_password_reset_emails(csv_file_path: str):
    """Send password reset emails to migrated users"""
    supabase = get_supabase_client()
    
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            email = row['email']
            try:
                response = supabase.auth.reset_password_for_email(email)
                print(f"Password reset sent to: {email}")
            except Exception as e:
                print(f"Failed to send reset email to {email}: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python password_reset_helper.py <csv_file_with_emails>")
        sys.exit(1)
    
    send_password_reset_emails(sys.argv[1])
'''
    
    with open('password_reset_helper.py', 'w') as f:
        f.write(script_content)
    
    print("Created password_reset_helper.py for post-migration password resets")


def main():
    parser = argparse.ArgumentParser(description='Migrate users to Supabase Auth')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated without making changes')
    parser.add_argument('--batch-size', type=int, default=100, help='Number of users to process in each batch')
    parser.add_argument('--create-reset-script', action='store_true', help='Create password reset helper script')
    
    args = parser.parse_args()
    
    if args.create_reset_script:
        create_password_reset_script()
        return
    
    migrator = SupabaseMigrator(dry_run=args.dry_run, batch_size=args.batch_size)
    
    success = migrator.run_migration()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
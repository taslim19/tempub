#!/usr/bin/env python3
"""
Quick script to generate WEB_API_KEY for Ultroid Web API
Run this to generate a secure random API key
"""
import secrets
import sys

def generate_api_key():
    """Generate a secure random API key"""
    api_key = secrets.token_urlsafe(32)
    return api_key

if __name__ == "__main__":
    key = generate_api_key()
    print("\n" + "="*60)
    print("🔐 Generated WEB_API_KEY")
    print("="*60)
    print(f"\nWEB_API_KEY={key}\n")
    print("="*60)
    print("\n📝 Add this to your .env file:")
    print(f"   WEB_API_KEY={key}\n")
    print("💡 Or set it directly:")
    print(f"   export WEB_API_KEY={key}\n")
    print("⚠️  Keep this key secret! Don't share it publicly.\n")


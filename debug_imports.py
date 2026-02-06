"""
Test script to check if all imports work correctly
"""

import sys
import os
from pathlib import Path

print("🔍 Testing imports...")

try:
    print("1. Testing basic imports...")
    import os
    import re
    import time
    import requests
    import logging
    from flask import Flask, render_template, request, flash, send_file, redirect, url_for
    import pandas as pd
    from io import BytesIO
    from pymongo import MongoClient
    from bson.objectid import ObjectId
    from dotenv import load_dotenv
    from datetime import datetime, timedelta
    print("✅ Basic imports successful")
except Exception as e:
    print(f"❌ Basic imports failed: {e}")
    sys.exit(1)

try:
    print("2. Testing extraction module...")
    from extraction import extract_business_card_details
    print("✅ Extraction module imported")
except Exception as e:
    print(f"❌ Extraction module failed: {e}")
    sys.exit(1)

try:
    print("3. Testing Flask app creation...")
    app = Flask(__name__)
    app.secret_key = "testkey"
    print("✅ Flask app created")
except Exception as e:
    print(f"❌ Flask app creation failed: {e}")
    sys.exit(1)

try:
    print("4. Testing MongoDB connection...")
    MONGO_URI = "mongodb+srv://sreeharitechxle:b3HCLN9Sbk3U72VN@cluster0.zea0bj6.mongodb.net/"
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("✅ MongoDB connection successful")
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e}")
    print("   This might be okay if Atlas is blocking this IP")

print("\n🎉 Import tests completed!")
print("If all basic imports passed, the issue is likely environment variables in Vercel.")

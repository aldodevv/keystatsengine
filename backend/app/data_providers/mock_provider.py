"""
Mock Data Provider (DEPRECATED):
Replaced by InstitutionalDataProvider with standardized XBRL taxonomy
and official OJK banking compliance.
"""

from app.data_providers.institutional_provider import InstitutionalDataProvider

# Backward compatibility alias
MockDataProvider = InstitutionalDataProvider

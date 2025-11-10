"""
MFA (Multi-Factor Authentication)
TOTP-based 2FA for enhanced security
"""
import pyotp
import qrcode
import io
import base64
from typing import Optional

from ultracore.security.auth.jwt_auth import User


class MFAManager:
    """
    Multi-Factor Authentication Manager
    
    Zero-trust: Require second factor for sensitive operations
    """
    
    @staticmethod
    def generate_secret() -> str:
        """Generate TOTP secret for user"""
        return pyotp.random_base32()
    
    @staticmethod
    def get_totp_uri(user: User, secret: str) -> str:
        """
        Get TOTP URI for QR code generation
        
        User scans with Google Authenticator, Authy, etc.
        """
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name='UltraCore Banking'
        )
    
    @staticmethod
    def generate_qr_code(totp_uri: str) -> str:
        """
        Generate QR code as base64 image
        
        Returns base64-encoded PNG
        """
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def verify_totp_code(secret: str, code: str) -> bool:
        """
        Verify TOTP code
        
        Returns True if valid
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # Allow 30s window
    
    @staticmethod
    async def enable_mfa_for_user(user: User) -> Dict:
        """
        Enable MFA for user
        
        Returns secret and QR code
        """
        secret = MFAManager.generate_secret()
        totp_uri = MFAManager.get_totp_uri(user, secret)
        qr_code = MFAManager.generate_qr_code(totp_uri)
        
        # In production: Store encrypted secret with user
        # user.mfa_secret = encrypt(secret)
        user.mfa_enabled = True
        
        return {
            'secret': secret,
            'qr_code': qr_code,
            'message': 'Scan QR code with authenticator app'
        }

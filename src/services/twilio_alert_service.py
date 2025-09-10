"""
Twilio Alert Service
Handles SMS and voice call notifications for emergency alerts.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from loguru import logger

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, environment variables should be set externally


class TwilioAlertService:
    """Service for sending SMS and voice alerts via Twilio."""
    
    def __init__(self):
        """Initialize Twilio client with credentials from environment."""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.twiml_app_sid = os.getenv('TWILIO_TWIML_APP_SID')  # For voice calls
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            logger.warning("Twilio credentials not properly configured. Alert system will be disabled.")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("Twilio alert service initialized successfully")
    
    def is_available(self) -> bool:
        """Check if Twilio service is properly configured."""
        return self.client is not None
    
    def send_sms_alert(self, phone_number: str, message: str, report_data: Dict) -> Tuple[bool, str]:
        """
        Send SMS alert to a phone number.
        
        Args:
            phone_number: Recipient phone number (E.164 format)
            message: Alert message content
            report_data: Report data for context
            
        Returns:
            Tuple of (success: bool, message_id_or_error: str)
        """
        if not self.is_available():
            return False, "Twilio service not available"
        
        try:
            # Format phone number to E.164 if needed
            formatted_number = self._format_phone_number(phone_number)
            if not formatted_number:
                return False, "Invalid phone number format"
            
            # Create comprehensive SMS message
            alert_message = self._create_sms_message(message, report_data)
            
            # Send SMS
            message_obj = self.client.messages.create(
                body=alert_message,
                from_=self.phone_number,
                to=formatted_number
            )
            
            logger.info(f"SMS alert sent to {formatted_number}: {message_obj.sid}")
            return True, message_obj.sid
            
        except TwilioException as e:
            logger.error(f"Twilio SMS error for {phone_number}: {str(e)}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Unexpected SMS error for {phone_number}: {str(e)}")
            return False, str(e)
    
    def make_voice_call_alert(self, phone_number: str, message: str, report_data: Dict) -> Tuple[bool, str]:
        """
        Make a voice call alert to a phone number.
        
        Args:
            phone_number: Recipient phone number (E.164 format)
            message: Alert message content for TTS
            report_data: Report data for context
            
        Returns:
            Tuple of (success: bool, call_id_or_error: str)
        """
        if not self.is_available():
            return False, "Twilio service not available"
        
        try:
            # Format phone number to E.164 if needed
            formatted_number = self._format_phone_number(phone_number)
            if not formatted_number:
                return False, "Invalid phone number format"
            
            # Create voice message
            voice_message = self._create_voice_message(message, report_data)
            
            # Create TwiML for voice call
            twiml_url = self._create_twiml_url(voice_message)
            
            # Make voice call
            call = self.client.calls.create(
                twiml=f'<Response><Say voice="alice">{voice_message}</Say></Response>',
                to=formatted_number,
                from_=self.phone_number
            )
            
            logger.info(f"Voice alert call made to {formatted_number}: {call.sid}")
            return True, call.sid
            
        except TwilioException as e:
            logger.error(f"Twilio voice call error for {phone_number}: {str(e)}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Unexpected voice call error for {phone_number}: {str(e)}")
            return False, str(e)
    
    def send_bulk_sms_alerts(self, recipients: List[Dict], message: str, report_data: Dict) -> Dict:
        """
        Send SMS alerts to multiple recipients.
        
        Args:
            recipients: List of dicts with 'phone_number' and optionally 'name'
            message: Alert message content
            report_data: Report data for context
            
        Returns:
            Dict with success/failure counts and details
        """
        results = {
            'total': len(recipients),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for recipient in recipients:
            phone_number = recipient.get('phone_number')
            name = recipient.get('name', 'Subscriber')
            
            if not phone_number:
                results['failed'] += 1
                results['details'].append({
                    'recipient': name,
                    'phone': phone_number,
                    'status': 'failed',
                    'error': 'No phone number provided'
                })
                continue
            
            # Personalize message if name is available
            personalized_message = f"Hello {name}, " + message if name != 'Subscriber' else message
            
            success, result = self.send_sms_alert(phone_number, personalized_message, report_data)
            
            if success:
                results['successful'] += 1
                results['details'].append({
                    'recipient': name,
                    'phone': phone_number,
                    'status': 'sent',
                    'message_id': result
                })
            else:
                results['failed'] += 1
                results['details'].append({
                    'recipient': name,
                    'phone': phone_number,
                    'status': 'failed',
                    'error': result
                })
        
        logger.info(f"Bulk SMS sent: {results['successful']}/{results['total']} successful")
        return results
    
    def make_bulk_voice_alerts(self, recipients: List[Dict], message: str, report_data: Dict) -> Dict:
        """
        Make voice call alerts to multiple recipients.
        
        Args:
            recipients: List of dicts with 'phone_number' and optionally 'name'
            message: Alert message content for TTS
            report_data: Report data for context
            
        Returns:
            Dict with success/failure counts and details
        """
        results = {
            'total': len(recipients),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for recipient in recipients:
            phone_number = recipient.get('phone_number')
            name = recipient.get('name', 'Subscriber')
            
            if not phone_number:
                results['failed'] += 1
                results['details'].append({
                    'recipient': name,
                    'phone': phone_number,
                    'status': 'failed',
                    'error': 'No phone number provided'
                })
                continue
            
            # Personalize message if name is available
            personalized_message = f"Hello {name}, " + message if name != 'Subscriber' else message
            
            success, result = self.make_voice_call_alert(phone_number, personalized_message, report_data)
            
            if success:
                results['successful'] += 1
                results['details'].append({
                    'recipient': name,
                    'phone': phone_number,
                    'status': 'called',
                    'call_id': result
                })
            else:
                results['failed'] += 1
                results['details'].append({
                    'recipient': name,
                    'phone': phone_number,
                    'status': 'failed',
                    'error': result
                })
        
        logger.info(f"Bulk voice alerts made: {results['successful']}/{results['total']} successful")
        return results
    
    def _format_phone_number(self, phone_number: str) -> Optional[str]:
        """
        Format phone number to E.164 format.
        
        Args:
            phone_number: Raw phone number string
            
        Returns:
            Formatted phone number or None if invalid
        """
        if not phone_number:
            return None
        
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone_number))
        
        # Handle Indian phone numbers (add +91 prefix if needed)
        if len(digits) == 10 and digits.startswith(('9', '8', '7', '6')):
            return f"+91{digits}"
        elif len(digits) == 12 and digits.startswith('91'):
            return f"+{digits}"
        elif digits.startswith('+'):
            return phone_number
        elif len(digits) == 11 and digits.startswith('1'):  # US numbers
            return f"+{digits}"
        elif len(digits) >= 10:
            return f"+{digits}"
        
        return None
    
    def _create_sms_message(self, base_message: str, report_data: Dict) -> str:
        """
        Create formatted SMS alert message.
        
        Args:
            base_message: Base alert message
            report_data: Report data for context
            
        Returns:
            Formatted SMS message
        """
        location = ""
        if report_data.get('city') and report_data.get('state'):
            location = f" in {report_data['city']}, {report_data['state']}"
        elif report_data.get('address'):
            location = f" at {report_data['address']}"
        
        hazard_type = report_data.get('hazard_type', 'hazard')
        severity = report_data.get('severity', 'medium').upper()
        
        sms_content = f"""
🚨 COASTAL HAZARD ALERT 🚨

{base_message}

DETAILS:
• Type: {hazard_type.title()}
• Severity: {severity}
• Location: {location}
• Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

This is an automated alert from the Coastal Hazard Management System. Stay safe and follow local emergency guidelines.

Reply STOP to unsubscribe.
        """.strip()
        
        # Truncate if too long (SMS limit is 1600 characters)
        if len(sms_content) > 1500:
            sms_content = sms_content[:1450] + "... [truncated]"
        
        return sms_content
    
    def _create_voice_message(self, base_message: str, report_data: Dict) -> str:
        """
        Create formatted voice message for TTS.
        
        Args:
            base_message: Base alert message
            report_data: Report data for context
            
        Returns:
            Formatted voice message
        """
        location = ""
        if report_data.get('city') and report_data.get('state'):
            location = f" in {report_data['city']}, {report_data['state']}"
        elif report_data.get('address'):
            location = f" at {report_data['address']}"
        
        hazard_type = report_data.get('hazard_type', 'hazard')
        severity = report_data.get('severity', 'medium').lower()
        
        voice_content = f"""
This is an emergency alert from the Coastal Hazard Management System.

{base_message}

This is a {severity} severity {hazard_type} alert{location}.

Please follow local emergency guidelines and stay safe.

This message will repeat once.

{base_message}

Thank you for your attention. Stay safe.
        """.strip()
        
        return voice_content
    
    def _create_twiml_url(self, message: str) -> str:
        """
        Create TwiML URL for voice calls (if using hosted TwiML).
        This is a placeholder - you would implement actual TwiML hosting.
        """
        # For now, we'll use inline TwiML in the call creation
        return None
    
    def get_alert_templates(self) -> Dict[str, Dict]:
        """
        Get predefined alert message templates.
        
        Returns:
            Dict of alert templates by severity/type
        """
        return {
            'flood_high': {
                'sms': "URGENT: Severe flooding detected. Immediate evacuation may be required. Avoid flooded roads and seek higher ground.",
                'voice': "Urgent flood alert. Severe flooding has been detected in your area. Immediate evacuation may be required. Please avoid flooded roads and seek higher ground immediately."
            },
            'flood_medium': {
                'sms': "WARNING: Flooding reported in your area. Exercise caution, monitor conditions, and be prepared to evacuate if necessary.",
                'voice': "Flood warning. Flooding has been reported in your area. Please exercise caution, monitor local conditions, and be prepared to evacuate if conditions worsen."
            },
            'tsunami_high': {
                'sms': "TSUNAMI ALERT: Move to higher ground immediately. This is not a drill. Follow evacuation routes and official emergency instructions.",
                'voice': "This is a tsunami alert. Move to higher ground immediately. This is not a drill. Please follow designated evacuation routes and listen to official emergency instructions."
            },
            'storm_surge_high': {
                'sms': "STORM SURGE WARNING: Dangerous coastal flooding expected. Evacuate low-lying areas immediately. Do not attempt to travel through flood waters.",
                'voice': "Storm surge warning. Dangerous coastal flooding is expected in your area. Please evacuate low-lying areas immediately. Do not attempt to travel through flood waters."
            },
            'general_high': {
                'sms': "EMERGENCY ALERT: Serious coastal hazard detected in your area. Follow local emergency instructions and stay informed through official channels.",
                'voice': "Emergency alert. A serious coastal hazard has been detected in your area. Please follow local emergency instructions and stay informed through official channels."
            },
            'general_medium': {
                'sms': "HAZARD ALERT: Coastal hazard conditions detected. Monitor local conditions and be prepared to take action if advised by authorities.",
                'voice': "Hazard alert. Coastal hazard conditions have been detected in your area. Please monitor local conditions and be prepared to take action if advised by authorities."
            }
        }
    
    def get_template_message(self, hazard_type: str, severity: str, message_type: str = 'sms') -> str:
        """
        Get a predefined template message.
        
        Args:
            hazard_type: Type of hazard (flood, tsunami, etc.)
            severity: Severity level (high, medium, low)
            message_type: Type of message (sms or voice)
            
        Returns:
            Template message string
        """
        templates = self.get_alert_templates()
        
        # Try specific hazard type + severity combination
        template_key = f"{hazard_type.lower()}_{severity.lower()}"
        if template_key in templates:
            return templates[template_key].get(message_type, templates[template_key].get('sms', ''))
        
        # Fall back to general template
        general_key = f"general_{severity.lower()}"
        if general_key in templates:
            return templates[general_key].get(message_type, templates[general_key].get('sms', ''))
        
        # Default message
        return f"Alert: {hazard_type.title()} hazard detected with {severity.lower()} severity. Please stay informed and follow official guidance."


# Global instance
twilio_service = TwilioAlertService()

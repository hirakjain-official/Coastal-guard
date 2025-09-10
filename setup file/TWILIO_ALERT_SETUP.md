# 🚨 Twilio Alert Broadcasting System Setup Guide

Your Coastal Hazard Management System now includes a comprehensive alert broadcasting system that allows admins to send SMS and voice call notifications to registered users via Twilio.

## 📋 Features Added

✅ **SMS Alerts** - Send emergency SMS messages to users  
✅ **Voice Call Alerts** - Make automated voice calls with text-to-speech  
✅ **Admin Confirmation Interface** - Review and confirm alerts before sending  
✅ **User Phone Number Registration** - Collect phone numbers during signup  
✅ **Alert Preferences** - Users can choose SMS and/or voice notifications  
✅ **Bulk Broadcasting** - Send alerts to multiple recipients at once  
✅ **Alert History** - Track all sent alerts with success/failure metrics  
✅ **Template Messages** - Pre-configured messages for different hazard types  
✅ **Indian Phone Number Support** - Automatic formatting for Indian (+91) numbers

## 🛠️ Setup Instructions

### Step 1: Install Twilio Dependency

The Twilio SDK has been added to `requirements.txt`. Install it:

```bash
pip install twilio==8.10.0
```

### Step 2: Get Twilio Credentials

1. **Create a Twilio Account**: Visit [twilio.com](https://www.twilio.com) and sign up
2. **Get Your Credentials**: Go to [Twilio Console](https://console.twilio.com/)
   - Copy your **Account SID**
   - Copy your **Auth Token**
3. **Get a Phone Number**: 
   - Go to Phone Numbers > Manage > Buy a number
   - Choose a number (voice + SMS capabilities)
   - Note the number (it will be in +1XXXXXXXXXX format)

### Step 3: Configure Environment Variables

Update your `.env` file with Twilio credentials:

```env
# Twilio Alert Service Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890  # Your Twilio phone number
```

### Step 4: Test the System

Run the test script to verify everything is working:

```bash
python test_alert_system.py
```

This will test:
- Phone number formatting
- Message templates
- Twilio configuration
- Optional: Send test SMS/voice calls

### Step 5: Run the Application

Start your Flask application:

```bash
python app.py
```

## 📱 How to Use

### For Users (Registration)

1. **Sign up** with phone number (now included in registration form)
2. **Choose alert preferences**: SMS and/or voice calls
3. Phone numbers are automatically formatted for Indian numbers

### For Admins (Sending Alerts)

1. **View Reports** in the admin dashboard
2. **Click "Send Alert"** button on any report detail page
3. **Review Report Details** and AI analysis
4. **Customize Alert Message** (or use suggested template)
5. **Choose Alert Type**: SMS, Voice, or Both
6. **Select Recipients** (all users with phone numbers by default)
7. **Send Alert** and monitor results

### Alert Types Available

- **SMS Only**: Send text message alerts
- **Voice Only**: Make automated phone calls with text-to-speech
- **Both**: Send SMS and make voice calls to maximum reach

## 🎯 Alert Templates

The system includes predefined templates for different scenarios:

### High Severity Alerts
- **Flood**: "URGENT: Severe flooding detected. Immediate evacuation may be required..."
- **Tsunami**: "TSUNAMI ALERT: Move to higher ground immediately..."
- **Storm Surge**: "STORM SURGE WARNING: Dangerous coastal flooding expected..."

### Medium/General Alerts
- **Flood**: "WARNING: Flooding reported in your area. Exercise caution..."
- **General**: "HAZARD ALERT: Coastal hazard conditions detected..."

## 📊 Monitoring & Analytics

### Admin Features
- **Alerts History**: View all sent alerts with success/failure counts
- **Recipient Management**: See which users can receive alerts
- **Delivery Reports**: Track SMS and voice call success rates
- **Report Status Updates**: Automatically updates report status to "alerted"

### Database Tables Added
- `alert_broadcasts`: Records all alert broadcasts
- Updated `users` table with `phone_number` and `alert_preferences`
- Updated `report_status_history` to track alert events

## ⚙️ Configuration Options

### Alert Preferences (Users)
- `sms`: Receive SMS alerts
- `voice`: Receive voice call alerts
- Both options can be enabled simultaneously

### Phone Number Formats Supported
- Indian: `9876543210` → `+919876543210`
- Indian with code: `+919876543210` (unchanged)
- US/International: `+1234567890` (unchanged)

### Message Customization
- **Base Message**: Custom alert content
- **Location Details**: Automatically added from report
- **Hazard Information**: Type and severity included
- **Timestamp**: Auto-generated
- **System Branding**: Coastal Hazard Management System

## 🚀 Usage Examples

### Example 1: Flood Alert in Mumbai

**Admin Action**: Click "Send Alert" on a Mumbai flood report

**Generated SMS**:
```
🚨 COASTAL HAZARD ALERT 🚨

URGENT: Severe flooding detected. Immediate evacuation may be required. Avoid flooded roads and seek higher ground.

DETAILS:
• Type: Flood
• Severity: HIGH
• Location:  in Mumbai, Maharashtra
• Time: 2025-09-10 15:30

This is an automated alert from the Coastal Hazard Management System. Stay safe and follow local emergency guidelines.

Reply STOP to unsubscribe.
```

**Generated Voice Call**:
```
This is an emergency alert from the Coastal Hazard Management System.

URGENT: Severe flooding detected. Immediate evacuation may be required. Avoid flooded roads and seek higher ground.

This is a high severity flood alert in Mumbai, Maharashtra.

Please follow local emergency guidelines and stay safe.

This message will repeat once.

[Message repeats]

Thank you for your attention. Stay safe.
```

### Example 2: Admin Workflow

1. **Report Received**: Citizen reports storm surge
2. **AI Analysis**: System processes with 85% confidence
3. **Admin Review**: Admin opens report detail page
4. **Alert Decision**: Admin clicks "🚨 Send Alert"
5. **Message Customization**: Admin reviews suggested message
6. **Recipient Selection**: 15 users with phone numbers selected
7. **Alert Broadcast**: SMS sent to 15 users, 14 successful, 1 failed
8. **History Recorded**: Alert logged in database with full details

## 🔧 Troubleshooting

### Common Issues

**"Twilio service not available"**
- Check your `.env` file has correct credentials
- Verify `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_PHONE_NUMBER`
- Ensure credentials are valid in Twilio Console

**"Invalid phone number format"** 
- Phone numbers must be 10+ digits
- Indian numbers automatically get +91 prefix
- International numbers should include country code

**"No valid recipients found"**
- Users must register with phone numbers
- Check that users have `phone_number` field populated
- Verify users' alert preferences include desired type (SMS/voice)

**SMS/Voice calls not received**
- Check Twilio account balance
- Verify phone number is SMS/voice enabled
- Check spam filters for SMS messages
- Ensure phone number is correct format

### Testing Checklist

- [ ] Twilio credentials configured in `.env`
- [ ] Run `test_alert_system.py` successfully
- [ ] Register test user with phone number
- [ ] Create test report with high confidence
- [ ] Send test alert to yourself
- [ ] Check alert history in admin panel
- [ ] Verify SMS and voice delivery

## 💰 Costs

### Twilio Pricing (Approximate)
- **SMS**: ~$0.0075 per SMS to Indian numbers
- **Voice**: ~$0.02 per minute to Indian numbers
- **Phone Number**: ~$1/month rental

### Cost Examples
- **100 users, 1 alert**: ~$0.75 (SMS) or ~$2 (voice)
- **Monthly for small city**: ~$10-50 depending on usage
- **Free Tier**: Twilio offers free credits for new accounts

## 🚦 Next Steps

1. **Configure Twilio** credentials in your `.env` file
2. **Test the system** with your own phone number
3. **Register users** with phone numbers
4. **Create admin workflows** for alert confirmation
5. **Monitor delivery rates** and optimize as needed

## 📞 Support

If you need help with setup or encounter issues:

1. **Check the logs** for detailed error messages
2. **Run the test script** to isolate configuration issues  
3. **Verify Twilio Console** for account status and usage
4. **Review phone number formats** in the database

The alert system is designed to be reliable and user-friendly, with comprehensive error handling and logging to help diagnose any issues.

---

**🇮🇳 Built for emergency response and community safety in India's coastal regions**

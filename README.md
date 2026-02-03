# ZKTeco Biometric Integration for FrappeHR

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<img width="834" height="407" alt="ZKTeco Integration Banner" src="https://github.com/user-attachments/assets/c86f875b-1173-4a56-83ae-e7bf6d4c4ea8" />

## Overview

An integration solution that connects ZKTeco biometric devices with FrappeHR for automated attendance tracking and real-time synchronization. This app eliminates manual data entry, ensures accurate attendance records, and streamlines workforce management.

## Features

- 🔄 **Real-time Synchronization**: Automatic data sync from ZKTeco devices to FrappeHR
- 🔐 **Secure Authentication**: JWT token-based secure API communication
- ⏰ **Flexible Scheduling**: Configurable sync frequencies (Hourly, Daily, Weekly, Monthly, Cron)
- 👥 **Employee Mapping**: Seamless biometric ID to employee record mapping
- 📊 **Attendance Automation**: Automatic Employee Check-in record creation
- 🔧 **Multi-Device Support**: Manage multiple ZKTeco devices from a single interface
- 📝 **Audit Trail**: Comprehensive logging for all synchronization activities
- 🔒 **User Status Management**: Automatic user enable/disable on device during check-in/check-out

## Prerequisites

- Frappe Framework
- ERPNext
- FrappeHR
- ZKTeco Biometric Device with network connectivity
- Admin access to ZKTeco device

## Installation

### For Self-Hosted/Manual Installation

1. **Get the app:**

```bash
bench get-app --branch version-16 https://github.com/navariltd/zkteco-biometric-integration
```

2. **Install on your site:**

```bash
bench --site {sitename} install-app zkteco_biometric_integration
```

3. **Restart bench:**

```bash
bench restart
```

## Configuration

### 1. ZKTeco Device Setup

Ensure your ZKTeco device is:

- Connected to the network
- Accessible via IP address
- Has admin credentials configured

### 2. FrappeHR Configuration

**Step 1: Create ZKTeco Biometric Settings**

Navigate to: `ZKTeco Biometric Integration` > `ZKTeco Biometric Settings`

<img width="848" height="593" alt="image" src="https://github.com/user-attachments/assets/4532fd73-c9f6-4627-b56a-5e977227b53d" />

Configure the following fields:

- **Username**: Admin username for ZKTeco device (must be unique per device)
- **Password**: Admin password for ZKTeco device
- **URL**: Device IP address (e.g., `http://192.168.1.100`)
- **Fetch Frequency**: Select sync frequency:
  - All (Continuous)
  - Hourly
  - Daily
  - Weekly
  - Monthly
  - Custom Cron expression
- **Enable**: Activate the integration

**Step 2: JWT Token Generation**

Upon saving, the system automatically:

- Generates a secure JWT token
- Handles token renewal
- Manages authentication with the device

### 3. Employee Configuration

**Biometric ID Mapping:**

For each employee:

1. Navigate to Employee master
2. Enter the **Biometric ID** matching the ID registered on the ZKTeco device
3. Ensure the ID is unique and matches exactly

**Shift Assignment:**

Assign appropriate shifts to employees for accurate attendance tracking.

## How It Works

### Authentication Flow

1. System generates JWT token using device credentials
2. Token authenticates all API requests
3. Automatic token renewal on expiry

### Synchronization Process

1. **Scheduled Job**: Runs based on configured frequency
2. **Data Fetch**: Retrieves punch transactions from device API
3. **Validation**: Maps employee codes to FrappeHR records
4. **Record Creation**: Creates Employee Check-in records
5. **Duplicate Prevention**: Automatically filters duplicate entries

### Data Mapping

- **Punch States**: Converted to IN/OUT log types
- **Employee Codes**: Mapped to FrappeHR Employee records
- **Timestamps**: Synchronized with accurate punch times

### User Status Management

The integration automatically manages user status on the ZKTeco device based on check-in/check-out activities:

**Check-Out (OUT log type):**

- When an employee checks out, the system automatically **disables** their user account on the ZKTeco device
- This prevents unauthorized access after the employee has left the premises
- The user's biometric data remains on the device but access is restricted

**Check-In (IN log type):**

- When an employee checks in, the system automatically **re-enables** their user account on the ZKTeco device
- This restores full biometric access for the employee
- Ensures seamless entry for the next work session

**Benefits:**

- Enhanced security by controlling device access based on attendance status
- Automatic access control without manual intervention
- Reduced risk of unauthorized entries outside work hours

## Usage

Once configured, the integration automatically:

- Fetches punch data from ZKTeco devices
- Creates Employee Check-in records
- Updates last synchronization timestamps
- Manages user enable/disable status on the device
- Logs all synchronization activities

Monitor synchronization through:

- Error Logs
- Scheduled Job Logs
- Employee Check-in records

## Troubleshooting

**Common Issues:**

1. **Connection Failed**
   - Verify device URL and network connectivity
   - Check firewall settings
   - Ensure device is powered on

2. **Authentication Error**
   - Verify username and password
   - Check token generation in settings

3. **No Data Syncing**
   - Verify fetch frequency configuration
   - Check if integration is enabled
   - Review scheduled job status

4. **Employee Not Found**
   - Verify biometric ID mapping
   - Ensure employee record exists in FrappeHR

5. **User Enable/Disable Not Working**
   - Ensure an employee is linked to their respective userId
   - Verify API permissions for user management
   - Check device firmware supports user status management
   - Review error logs for API response errors

## Support & Consultation

For implementation support, customization, or consultation:

📧 **Contact**: [Navari Limited](https://navari.co.ke/)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

**Developed by**: [Navari Limited](https://navari.co.ke/)  
**Repository**: [github.com/navariltd/zkteco-biometric-integration](https://github.com/navariltd/zkteco-biometric-integration)

#  ZKTeco Biometric Integraion System with FrappeHR 
## Introduction
<img width="834" height="407" alt="image" src="https://github.com/user-attachments/assets/c86f875b-1173-4a56-83ae-e7bf6d4c4ea8" />

Integrating the ZKTeco biometric system with FrappeHR enables real-time attendance tracking and automated data synchronization. This integration allows you to efficiently capture and manage punch logs directly from your ZKTeco biometric devices, ensuring accurate and up-to-date attendance records.

By setting up this integration, you can streamline your attendance processes, minimize manual data entry, and enhance overall accuracy in tracking employee time. The integration ensures that punch data from ZKTeco biometric devices is seamlessly transferred to FrappeHR, where it is recorded in real-time, helping you maintain a reliable attendance management system.

## 1. Setup and Configuration

### 1.1 ZKTeco Biometric Settings

1. **Username and Password:**
   * After configuring your ZKTeco device, you will need the admin username and password.
   * These credentials are crucial for configuring the ZKTeco device and integrating it with FrappeHR.
   * Fill those details in the respective fields in the ZKTeco biometric settings doctype.

2. **Device URL:**
   * You will need the IP address or URL of your ZKTeco device.
   * This URL is essential for establishing communication between FrappeHR and the ZKTeco device.
   * Enter the device URL in the URL field in the ZKTeco biometric settings doctype.
  
   ### NL ZKTeco Biometric Settings
     <img width="1193" height="476" alt="image" src="https://github.com/user-attachments/assets/b3f7e567-cc13-4655-bd2c-611c8c4041e1" />
     <img width="909" height="169" alt="image" src="https://github.com/user-attachments/assets/46320735-d498-4581-872d-866f126a7ad7" />



1. **Settings Configuration:**
   * Navigate to the ZKTeco Biometric Integration Settings.
   * Create a new ZKTeco Biometric Settings record.
   * Fill in the required configuration:
     * **Username**: ZKTeco device  username   NB: username should be unique for each
     * **Password**: ZKTeco device  password
     * **URL**: ZKTeco device IP address or URL
     * **Fetch Frequency**: Choose synchronization frequency (Hourly, Daily, etc.)
     * **Enable**: Check to activate the integration

2. **Token Generation:**
   * Upon saving the settings, the system automatically generates a JWT token.
   * This token is used for secure API communication with the ZKTeco device.
   * Token expiry is handled automatically by the system.

### 1.4 Employee Configuration

1. **Employee Biometric ID Mapping:**
   * Each employee must be assigned a unique biometric ID in the FrappeHR system, similar to the one registered in the ZKTeco device.
   * It is recommended that this ID closely resembles the employee's system ID for consistency.
   * Since you have registered the employee on the ZKTeco device, get the same ID and ensure it matches the employee ID in FrappeHR.

2. **Shift Assignment:**
   * Assign appropriate shifts to each employee to facilitate automatic attendance marking.
   * This step is crucial for ensuring that the attendance system functions correctly, as it relies on shift data to log employee punch times accurately.

## 2. Key Points to Remember

* **Attendance Marking:**
  * The biometric punch data will update the Employee Check-in records.
  * The date of the last synchronization from the attached shift will be updated with the latest punch log.

* **Regular Syncing:**
  * The system automatically synchronizes data based on the configured frequency.
  * Regularly verify and monitor synchronization logs to ensure accurate attendance records.

* **Employee Records:**
  * Accurate mapping of biometric IDs and shift assignments is vital for correct attendance tracking and reporting.

* **Scheduled Synchronization:**
  * The integration uses  scheduled job system to automatically fetch punch data.
  * You can configure different synchronization frequencies based on your requirements.
  * Available options include: All, Hourly, Daily, Weekly, Monthly, and custom Cron expressions.

## 3. How the Integration Works

### 3.1 Authentication Process

1. **Token Generation:**
   * The system generates a JWT token using the provided username and password.
   * This token is used for all subsequent API calls to the ZKTeco device.

2. **Token Management:**
   * Tokens are automatically renewed when they expire.
   * The system handles token validation and renewal transparently.

### 3.2 Data Synchronization Process

1. **Scheduled Execution:**
   * The system runs synchronization based on the configured frequency.
   * Each enabled ZKTeco configuration is processed independently.

2. **Transaction Retrieval:**
   * The system fetches punch transactions from the ZKTeco device using the API.
   * Transactions include employee codes, punch times, and punch states.

3. **Data Processing:**
   * Punch states are converted to check-in/check-out logs.
   * Employee codes are mapped to FrappeHR employee records.
   * Duplicate records are automatically prevented.

4. **Record Creation:**
   * Employee Checkin records are created in FrappeHR for each valid transaction.
   * Records include employee ID, log type (IN/OUT), and punch time.

## Installation Process

### Manual/Self-Hosted Installation

1. Install bench
2. Install ERPNext
3. Install FrappeHR
4. Once bench, ERPNext and FrappeHR are installed, add zkteco_biometric_integration to your bench by running:

```bash
bench get-app --branch {branch-name} [https://github.com/navariltd/zkteco_biometric_integration.git](https://github.com/navariltd/zkteco-biometric-integration)
```

Replace `{branch-name}` with the desired branch name from the repository. Ensure compatibility with your installed versions of Frappe, ERPNext and Frappe HR.

5. Install the zkteco_biometric_integration app on your site by running:

```bash
bench --site {sitename} install-app zkteco_biometric_integration
```

Replace `{sitename}` with the name of your site.



If assistance is needed to get started, reach out for consultation and support from: [Navari](https://navari.co.ke/)

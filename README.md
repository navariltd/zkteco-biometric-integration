# ZKTeco Biometric Integration for FrappeHR

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<img width="834" height="407" alt="ZKTeco Integration Banner" src="https://github.com/user-attachments/assets/c86f875b-1173-4a56-83ae-e7bf6d4c4ea8" />


An integration application that connects ZKTeco biometric devices with FrappeHR for automated attendance tracking. It eliminates manual data entry by pulling punch transactions directly from the device, mapping them to employee records, and creating Employee Check-in documents on a configurable schedule.

For full documentation, visit the **[ZKTeco Biometric Integration Wiki](https://docs.navari.co.ke/zkteco/zkteco)**.

## Prerequisites

- Frappe Framework v16
- ERPNext v16
- FrappeHR v16
- A network-accessible ZKTeco biometric device with admin credentials

## Installation

```bash
bench get-app --branch version-16 https://github.com/navariltd/zkteco-biometric-integration
bench --site {sitename} install-app zkteco_biometric_integration
bench restart
```

## Quick Setup

1. Go to **ZKTeco Biometric Integration > ZKTeco Biometric Settings** and create a settings record for each device — provide the device URL, admin credentials, and sync frequency.
2. On each **Employee** master, set the **Biometric ID** field to match the ID registered on the ZKTeco device.
3. Assign shifts to employees so FrappeHR can process the synced check-in records into attendance.

The integration will begin pulling data automatically on the next scheduled run. Monitor activity via **Error Logs** and **Scheduled Job Logs**.


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

## Support

For implementation support or customisation, contact [Navari Limited](https://navari.co.ke/).

## Contributing

Contributions are welcome. Please target the `develop` branch when submitting pull requests.

**Developed by [Navari Limited](https://navari.co.ke/)**

**Repository**: [github.com/navariltd/zkteco-biometric-integration](https://github.com/navariltd/zkteco-biometric-integration)

'''
## Back-end Structure

The backend is organized into the following main components:

- **`app.py`**: The entry point for the Flask application.
- **`config.py`**: Configuration settings for the application.
- **`components/`**: Contains modularized backend logic, such as worker management, entry logging, and camera verification.
- **`database/`**: Contains database models and schemas for data validation and serialization.
- **`tests/`**: Unit tests for the backend components.

## Functions
The back-end is responsible for **2** core modules:

### Employee Camera Verification
Verification of employee (worker) entry into the building. Works by implementing a 2 factor authentication by checking the face biometry and the QR code provided to the worker. 
Any violation gets logged, notably:
- Mismatch of face and QR code data
- Multiple QR codes detected
- Multiple persons (faces) detected
- Expired QR code

### Admin Panel
Handles all administration tasks related to the camera verification behind an intuitive web dashboard.
- Creation of entry permits
- Invalidation of entry permits
- Changing details of existing entry permits
- Viewing entry logs, advanced filtering by employee, event type, event code
- Generating PDF/JSON entry log reports


'''
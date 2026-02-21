# Django Webhook App

A backend-only webhook application demonstrating a typical request flow: the client sends a request to the server, the webhook verifies the client's signature and idempotency key, triggers background tasks, and returns a confirmation that the request has been received and is being processed.

## Testing Functionality

1. Clone the repo
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   # Linux/macOS
   source .venv/bin/activate
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
3. Install django if not installed: `pip install django`
3. Create a .env file and set adapter secrets as bellow:
  - ADAPTER_1_SECRET=b7f3c9e21a4d8f6c0e92ab31f47d6c58
  - ADAPTER_2_SECRET=91c4d7fa82e63b1c5f9a4d7e2b8c0a16
4. Run tests: `python manage.py test`

## Project Structure

- **Event Model:** Used for verifying idempotency keys. Could also store timestamps, status, or set expiration timers to allow repeated requests after a set duration.  
- **URL Routing:** Single dynamic path using `<str:service>` to determine the service adapter.  
- **Views:** `receiver` – main view handling the webhook flow.  
- **Adapters:**
  - `BaseAdapter` – contains shared logic (`verify_signature`).  
  - `Adapter1` – enqueues welcome emails.  
  - `Adapter2` – demonstrates adaptability; contains an empty `trigger_actions` method.  

## Features

### Service Adapters
- Requests hitting the receiver view use the `<str:service>` path converter to determine which service made the request.  
- The corresponding adapter is stored in an `adapter` variable.  

### Signature Verification
- The receiver view calls `adapter.verify_signature(request, adapter.secret_key)` and returns a `401 Unauthorized` response if verification fails.  
- Verification flow:
  1. Checks for the presence of the client’s signature in the headers.  
  2. Converts the adapter’s secret to bytes (UTF-8).  
  3. Computes the expected signature using HMAC with SHA-256.  
  4. Compares the client-provided signature with the expected signature using `hmac.compare_digest`.  

### Idempotency Key Verification
- Returns a `400 Bad Request` if the client does not provide an `idempotency_key`.  
- If a key is provided:
  - Returns `200 OK` if an event with that key already exists.  
  - Creates a new `Event` in the database if the key does not exist.  

### Email Validation
- `Adapter1` sends an email when its actions are triggered. The receiver attempts to extract an email from the request body:
  - If present, it validates the email and returns `400 Bad Request` for invalid emails.  
  - If valid, it triggers `Adapter1` actions via `adapter.trigger_actions(email)`.  
  - If no email is present, `Adapter2` actions are triggered.  
- **Note:** As adapters grow in complexity, separating URLs per service would reduce the need for special-case logic in the main receiver view.  

### Background Task Execution with Retries
- `Adapter1` enqueues the `email_users` task via Django’s background task functionality.  
- The task tracks retries and re-executes up to three times if an `SMTPError` occurs.  
- In the development environment, ImmediateBackend executes tasks synchronously for testing.  



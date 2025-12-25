# Functional requirements: User Profile section

## 1. General purpose

The Profile section provides the user with the ability to manage their personal data and account security settings.

##2. Section Structure

### 2.1 Page Title

**Elements**
- The "Profile" header in the headerStore
- Subtitle: "Personal data management and security settings"

### 2.2 Main sections

The page is divided into two cards:
1. **Personal Information** - user data
2. **Security** - Account protection settings

---

# PART 1: PERSONAL INFORMATION

##3. Personal Information Card

### 3.1 Avatar and basic information

**Avatar display:**
- Large round avatar with initials
- Class: user-avatar large
- Initials are calculated from the first and last names
- Default background and text color

**Information next to the avatar:**
- Full name (First name + Last Name)
- Style: h3, bold
- User's email address
- Style: plain text, secondary color

**Location:**
- Horizontal on the desktop
- Vertical on mobile devices
- Avatar on the left, information on the right (desktop)

### 3.2 Profile Form

**Form component:**
- n-form from Naive UI
- Model: profile
- Validation rules: rules
- Ref: formRef (for software validation)

**Form fields:**

#### 1. First Name (firstName)

**Parameters:**
- Label: "Name"
- Path: "firstName"
- Component: n-input
- Placeholder: "Enter a name"
- Disabled: !isEditing

**Validation:**
- Required field
- Message: "Enter a name"
- Trigger: blur

#### 2. Last name (lastName)

**Parameters:**
- Label: "Last name"
- Path: "lastName"
- Component: n-input
- Placeholder: "Enter last name"
- Disabled: !isEditing

**Validation:**
- Required field
- Message: "Enter your last name"
- Trigger: blur

#### 3. Email

**Parameters:**
- Label: "Email"
- Path: "email"
- Component: n-input
- Type: text
- Placeholder: "Enter email"
- Disabled: !isEditing

**Validation:**
- Required field
- Message: "Enter your email address"
- Email format
- Message: "Enter the correct email address"
- Trigger: blur

#### 4. Phone (phone)

**Parameters:**
- Label: "Phone"
- Path: "phone"
- Component: n-input
- Placeholder: "+7xxxxxxxxxx"
- Disabled: !isEditing

**Validation:**
- Optional field
- The format is checked when filling out
- Pattern: starts with a + or a number
- Only numbers and +

### 3.3 Modes of operation of the form

#### Viewing mode (isEditing = false)

**The state of the fields:**
- All fields are disabled
- Display the current values
- Not edited

**Buttons:**
- The only "Edit" button
is Type: primary
- Clicking switches to editing mode (startEditing())

#### Editing mode (isEditing = true)

**The state of the fields:**
- All fields are enabled
- You can enter and change values
- Focus illumination

**Buttons:**

1. ** "Save" button**
- Type: primary
   - Loading: Issuing (during saving)
- Click causes updateProfile()
- Saves changes

2. **The "Cancel" button**
   - The usual button
   - The click causes cancelEditing()
- Cancels the changes and exits the editing mode

### 3.4 Editing Logic

#### Start editing (startEditing)

**Actions:**
1. Saving current data to originalProfile (backup)
2. Switching isEditing = true
3. Activating form fields

#### Saving changes (updateProfile)

**The process:**
1. Form validation (formRef.validate())
2. If the validation is successful:
   - Setting isSaving = true
- API call: users.updateProfile(profile)
- Response processing
3. On success:
- Update local data
   - Switching isEditing = false
- Notification of success
   - isSaving = false
4. In case of error:
- Error modal window
- Error details from the server
   - The editing mode remains active
   - isSaving = false

#### Canceling editing (cancelEditing)

**Actions:**
1. Data recovery from originalProfile
2. Switching isEditing = false
3. Deactivating form fields
4. Reset validation errors (if any)

### 3.5 Calculating initials

**The userInitials function:**
- Takes the first letter of the firstName
- Takes the first letter of lastName
- Combines in uppercase
- For example: "Ivan Petrov" → "Sole proprietor"
- If there is no data: the first letter of the email is used.

---

# PART 2: SECURITY

##4. Security Card

### 4.1 Two-factor Authentication (2FA)

**Section structure:**

#### Information block:

**Title:**
- h3: "Two-factor authentication (2FA)"

**Description:**
- Text: "Add an additional layer of protection to your account"
- Class: security-description
- Color: Secondary

**Status indicator:**
- n-space with center alignment
- Round status indicator:
- Class: status-indicator
  - Modifier: active if enabled
  - Green color if active
  - Gray color if inactive
- Status text:
- "Enabled" if twoFactorEnabled = true
- "Disabled" if twoFactorEnabled = false

#### Action block:

**2FA control button:**
- Dynamic type:
  - error (red) if 2FA is enabled
  - primary (blue) if 2FA is disabled
- Dynamic text:
- "Disable" if enabled
- "Enable" if disabled
- Loading: is2FALoading (during operation)
- A click triggers toggle2FA()

#### 2FA Switching (toggle2FA)

**The process:**
1. Setting is2FALoading = true
2. Definition of action:
   - If enabled: call disable2FA()
- If disabled: call enable2FA()
3. API call the appropriate method
4. Response processing
5. On success:
- twoFactorEnabled switch
- Success notification
   - is2FALoading = false
6. In case of an error:
- Modal window with an error
- The state does not change
   - is2FALoading = false

**Features of inclusion:**
- May require additional confirmation
- A QR code can be opened to configure the authenticator app
- May require entering a confirmation code

**Shutdown Features:**
- Requires entering the current 2FA code
- Confirmation of the action
- A warning about a decrease in security

### 4.2 Password Change

**Section structure:**

#### Information block:

**Title:**
- h3: "Password change"

**Description:**
- Text: "Update your password regularly to ensure security"
- Class: security-description

#### Action block:

** "Change password" button:**
- Type: secondary (secondary button)
- Text: "Change password"
- A click calls openChangePasswordModal()

#### Modal password change window

**Component:** ChangePasswordModal

**Opening:**
- this.$modals.open(ChangePasswordModal, ...)
- Callback onOk for processing a successful shift

**Fields of the modal window:**

1. **Current password**
- Type: password
   - Required field
- Validation: not empty

2. **New password**
- Type: password
   - The required field
is Validation:
     - Minimum of 8 characters
     - Contains uppercase and lowercase letters
     - Contains numbers
     - Contains special characters

3. **Confirm a new password**
- Type: password
   - Required field
- Validation: must match the new password

**Buttons:**
- "Change password" - primary, with loading
- "Cancel" - closes the modal window

**The shift process:**
1. Validation of all fields
2. Checking the password match
3. API call: users.ChangePassword()
4. Upon success:
- Closing the modal window
- Notification of success
   - Possible logout (re-login requirement)
5. In case of an error:
- Error is displayed in the modal window
- The modal window remains open
   - Ability to correct data

---

##5. Uploading profile data

### 5.1 Initialization

**When mounting the component:**
1. Setting the page title (headerStore.setPageTitle('Profile'))
2. Loading profile data (loadProfile())
3. Checking the 2FA status (check2FAStatus())

### 5.2 Loading the profile (loadProfile)

**The process:**
1. API call: users.getProfile()
2. Getting user data
3. Filling in the profile object
4. Saving to originalProfile
5. In case of an error: a modal window with an error

### 5.3 2FA Status Check (check2FAStatus)

**The process:**
1. API call: users.get2FAStatus()
2. Getting the status (enabled/disabled)
3. Installing twoFactorEnabled
4. In case of error: the default setting is false

---

##6. Data validation

### 6.1 Field Validation Rules

**firstName:**
```javascript
{
  required: true,
  message: 'Enter a name',
  trigger: 'blur'
}
```

**lastName:**
```javascript
{
  required: true,
  message: 'Enter your last name',
  trigger: 'blur'
}
```

**email:**
```javascript
[
  {
    required: true,
    message: 'Enter email address',
    trigger: 'blur'
  },
  {
    type: 'email',
    message: 'Enter the correct email address',
    trigger: 'blur'
  }
]
```

**phone:**
``javascript
{
pattern: /^[\+]?[0-9]{10,15}$/,
message: 'Enter the correct phone number',
  trigger: 'blur'
}
```

### 6.2 Password Validation

**Minimum requirements:**
- Length: minimum 8 characters
- Capital letters: minimum 1
- Lowercase letters: minimum 1
- Numbers: at least 1
- Special characters: recommended

---

##7. Error Handling

### 7.1 Profile Loading Errors

**In case of an error:**
- Modal window with error text
- Details from the server response
- The "OK" button to close
- The ability to reload the page

### 7.2 Saving Errors

**If there is an error updating the profile:**
- Modal window with error description
- The editing mode remains active
- The data in the fields is saved
- It can be fixed and repeated

### 7.3 2FA Errors

**In case of an on/off error:**
- Modal window with error description
- The 2FA status does not change
- The possibility of a second attempt

### 7.4 Password Change Errors

**In case of an error:**
- Incorrect current password
- The new password does not meet the requirements
- The paroles match
- Displaying a specific error in the modal window

---

##8. Adaptability

### 8.1 Desktop (> 768px)

**Personal Information card:**
- Avatar and information horizontally
- One-column or two-column form
- Inline buttons (next to each other)

**Security Card:**
- 2FA and password sections vertically
- Information and buttons horizontally in each section

###8.2 Tablet (480px - 768px)

**General:**
- Adaptive margins
- Single column forms
- The buttons are slightly larger


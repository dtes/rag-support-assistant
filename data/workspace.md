# Functional requirements: Organization section

## 1. General purpose

The Organization section provides the ability to manage information about the workspace (organization) and the participants who have access to this workspace.

##2. Section Structure

### 2.1 Page Title

**Elements**
- Subtitle: "Workspace information and participant management"
- It is placed under the heading "Organization" from the headerStore

### 2.2 Main sections

The page is divided into two main cards:
1. **Workspace Information** - organization data
2. **Workspace members** - list of users with access

---

# PART 1: WORKSPACE INFORMATION

## 3. Workspace information Card

### 3.1 Displaying information

**Workspace logo**
- Round avatar with the initials of the title
- Class: workspace-logo
- Initials are calculated from the workspace name
- Size: large

**Workspace meta information**
- Name of the organization (large font, bold)
- Description of the organization
- If there is no description: "Description is not specified"

**A grid of additional information**
- Company's USERNAME (if specified, otherwise "Not specified")
- Workspace creation date (formatted date)
- Location: two-column grid

### 3.2 Viewing Mode

**Data display**
- All fields are shown as text
- The workspace name as the h3 header
- Description as a paragraph
- BIN and date in the info-grid

**The "Edit" button**
- Displayed only if the user has rights (canEditWorkspace)
- Type: secondary
- Size: small
- Icon: Pencil
- Text: "Edit"

### 3.3 Editing Mode

**Mode activation**
- Click on the "Edit" button
- Switching isEditingWorkspace = true
- Fields turn into inputs

**Editable fields:**

1. **workspace name**
   - n-input component
- Placeholder: "Workspace name"
- Model: editableWorkspace.name

2. **Workspace Description**
   - n-input with the textarea type
- Placeholder: "Workspace description"
- Number of lines: 3
- Model: editableWorkspace.description

3. **workspace BIN**
   - n-input component
- Placeholder: "Workspace BIN"
- Model: editableWorkspace.bin

**Date of creation**
- Remains unchanged (view only)

**Action buttons in edit mode:**

1. **The "Save" button**
   - Type: primary
   - Size: small
- Loading state when saving (isSavingWorkspace)
   - A click calls saveWorkspace()

2. **Cancel button**
- Size: small
- Click cancelEditingWorkspace()
- Cancels the changes and returns to the viewing mode

### 3.4 Saving Changes

**The process:**
1. Data validation (name required)
2. Sending to the server (API: workspaces.updateWorkspace)
3. Updating local data
4. Exit the editing mode
5. Success/Error Notification

** On success:**
- Data is being updated
- isEditingWorkspace = false
- A success message is displayed

**In case of an error:**
- Error modal window
- The editing mode remains active
- The user can fix and repeat

---

# PART 2: PARTICIPANTS IN THE WORKSPACE

## 4. Participant Card

### 4.1 Section heading

**Elements:**
- Heading: "Workspace participants" (section-title)
- The "Invite" button
is displayed only if canInviteMembers
  - Type: primary
  - Size: small
  - Icon: PersonAddOutline
  - Text: "Invite"

### 4.2 List of participants

**Component:**
- n-list with bordered and hoverable options
- Each participant in the n-list-item

**The structure of the participant element:**

1. **Avatar (prefix)**
- Round avatar with initials
- Class: member-avatar
   - Initials are calculated from the first and last names

2. **Basic information**
- First and last name of the participant
   - Email in parentheses (if specified)
- Tag "This is you" if participant = current user
- Tag in blue (type: info), size: small

3. **Role management (if canManageMembers and not the current user):**

   a. **Access level**
   - n-select component
- Options:
     - The owner
     - The administrator
     - User
     - View only
- Size: small
- updateMemberAccessLevel() is called when changing

   b. **Position**
- n-select component
- Options from the positions directory
   - Size: small
- When changing, updateMemberPosition() is called

4. **Actions (suffix if canManageMembers and not the current user):**

   **Participant removal button**
   - Not displayed for the owner (isOwner)
- Type: error
   - Size: small
- Secondary style
- Text: "Delete"
   - A click calls removeMemberModal()

### 4.3 Participant Invitation

**The InviteMemberModal modal window:**

**Opening:**
- Click on the "Invite"
button - The available positions are transferred

**Invitation fields:**
- Email of the invited user
- Access level
- Position (optional)

**After the invitation:**
- The modal window is closing
- The list of participants is updated (loadMembers())
- A success notification is displayed

**In case of an error:**
- Modal window with error description
- Possibility to try again

### 4.4 Changing the access level

**updateMemberAccessLevel function(MemberID, newAccessLevel)**

**The process:**
1. Validation of the change
2. API call: workspaces.updateMemberAccessLevel()
3. Updating the list of participants
4. Success/Error Notification

**Access levels:**
- OWNER - the owner (full access to everything)
- ADMIN - administrator (managing almost everything except deleting workspace)
- USER - user (working with operations and reports)
- VIEWER - view only (without editing)

### 4.5 Change of position

**updateMemberPosition function(MemberID, PositionID)**

**The process:**
1. API call: workspaces.updateMemberPosition()
2. Updating the list of participants
3. Success/Error Notification

**Positions:**
- Downloaded from the positions directory
- Examples: Director, Accountant, Manager, etc.

### 4.6 Deleting a participant

**The RemoveMemberModal modal window:**

**Opening:**
- Click on the "Delete" button from the participant
- Information about the participant is transmitted

**Confirmation:**
- Modal warning window
- Information about the consequences of deletion
- The "Delete" and "Cancel" buttons

**After removal:**
- API call: workspaces.removeMember()
- Modal window closes
- The list is updated (loadMembers())
- Notification of success

**Restrictions:**
- The workspace owner cannot be deleted
- You can't delete yourself
- You cannot delete a single administrator

---

## 5. Access rights

### 5.1 Rights Verification

**canEditWorkspace:**
- The ability to edit information about the workspace
- Only for the owner and administrators

**canInviteMembers:**
- The ability to invite new members
- For the owner and administrators

**canManageMembers:**
- Ability to manage participants (roles, deletion)
- Only for the owner and administrators

### 5.2 Identifying the current user

**currentUserId:**
- ID of the current authorized user
- Used to:
- Display the tag "This is you"
  - Hide controls for yourself
  - Preventing self-removal

---

##6. Formatting data

### 6.1 Initials of workspace

**workspaceInitials function:**
- Takes the first letters of the words of the name
- Maximum of 2 characters
- Uppercase
- For example: "My Company" → "MK"

### 6.2 Initials of the participant

**getMemberInitials(member) function:**
- First letter of first name + first letter of last name
- Uppercase
- For example: "Ivan Petrov" → "Sole proprietor"

### 6.3 Formatting the date

**formatDate(dateString) function:**
- Format: DD.MM.YYYY
- Locale: ru-RU
- For example: "2024-01-15" → "15.01.2024"

---

##7. Uploading data

### 7.1 Initialization

**When mounting the component:**
1. Loading workspace data (loadWorkspace())
2. Loading the list of participants (loadMembers())
3. Loading the directory of positions (loadPositions())

### 7.2 Load indication

**For workspace:**
- Loading indicator at initial loading
- Save indicator (isSavingWorkspace) when updating

**For participants:**
- List loading indicator
- Separate indicators for actions (role update, deletion)

---

##8. Error Handling

### 8.1 Download Errors

**If there is a workspace upload error:**
- Error modal window
- Error details
- The possibility of a second attempt

**If there is an error in uploading participants:**
- Error modal window
- An empty list
- The "Repeat" button

### 8.2 Saving Errors

**If there is a workspace update error:**
- Modal window with error description
- The editing mode remains active
- No data is lost

**In case of a participant management error:**
- Modal window with error description
- Rollback to the previous state
- The possibility of a second attempt

---

##9. Adaptability

### 9.1 Desktop

**Workspace card:**
- Horizontal arrangement of the logo and information
- Two-column grid for additional fields
- Inline action buttons

**List of participants:**
- Complete information in one line
- Selectors and buttons in one line
- Convenient element sizes

### 9.2 Mobile

**Workspace card:**
- Vertical arrangement of the elements
- Logo above the information
- Single-column grid
- Full-width buttons

**List of participants:**
- Vertical arrangement of information
- Selectors on separate lines
- Full-width buttons
- Minimum button height: 44px

---

## 10. Efficiency

**Optimizations:**
- Loading data in parallel during initialization
- Caching of the job directory
- Conditional rendering of controls
- Optimization of list updates

---

## 11. Safety

### 11.1 Validation on the client

**When editing the workspace:**
- Checking required fields
- Validation of the BIN format
- Limitation of the length of text fields

**When managing participants:**
- Checking rights before actions
- Validation of selected values
- Prevention of critical actions

### 11.2 Protection from accidental actions

**Confirmations:**
- Deleting a participant requires confirmation
- Changing critical settings with a warning
- The ability to cancel editing


# Roblox User Lookup

A Python application that fetches comprehensive user information from the Roblox API and displays it in a beautiful Tkinter GUI with the user's avatar.

The application was coded using the help of ChatGPT since i am a beginner and i did this application just for fun, please do not take the coding to heart.

## Features

- Search for any Roblox user by username
- Display comprehensive user information including:
  - Basic info (username, display name, user ID, description)
  - Account details (creation date, ban status, verified badge)
  - Social statistics (friends, followers, following)
  - Achievements (badges, groups)
  - Presence information (status, last location)
  - Direct links to profile and avatar pages
- Display user avatar image
- Modern, dark-themed UI
- Fast and responsive with threaded API calls

## Installation

1. Install Python 3.7 or higher

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python roblox_user_info.py
```

1. Enter a Roblox username in the search field
2. Click "Search" or press Enter
3. View the user's information and avatar

## Requirements

- Python 3.7+
- requests
- Pillow (PIL)
- tkinter (usually included with Python)

## API Endpoints Used

The application uses the official Roblox API endpoints:
- `https://users.roblox.com/v1/usernames/users` - Get user ID from username
- `https://users.roblox.com/v1/users/{userId}` - Get user information
- `https://thumbnails.roblox.com/v1/users/avatar-headshot` - Get user avatar
- `https://friends.roblox.com/v1/users/{userId}/friends/count` - Get friends count
- `https://friends.roblox.com/v1/users/{userId}/followers/count` - Get followers count
- `https://friends.roblox.com/v1/users/{userId}/followings/count` - Get following count
- `https://badges.roblox.com/v1/users/{userId}/badges/count` - Get badges count
- `https://groups.roblox.com/v1/users/{userId}/groups/roles` - Get groups
- `https://presence.roblox.com/v1/presence/users` - Get user presence

## Notes

- This application uses public Roblox API endpoints and does not require authentication
- Some information may not be available for all users (e.g., private profiles)
- The application makes multiple API calls to gather comprehensive information


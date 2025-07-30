# Google API Setup Guide

This guide explains how to set up Google API credentials for YouTube integration features in IotaPlayer.

## Overview

IotaPlayer's YouTube integration allows you to:
- **Upload playlists** to your YouTube account
- **Open YouTube videos** for current songs
- **Manage YouTube playlists** from within IotaPlayer

## Prerequisites

- **Google Account** with YouTube access
- **Google Cloud Project** (free tier available)
- **YouTube Data API v3** enabled
- **OAuth 2.0 credentials** configured

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. **Go to Google Cloud Console:**
   - Visit [console.cloud.google.com](https://console.cloud.google.com)
   - Sign in with your Google account

2. **Create a new project:**
   - Click "Select a project" → "New Project"
   - Enter a project name (e.g., "IotaPlayer YouTube Integration")
   - Click "Create"

3. **Select your project:**
   - Make sure your new project is selected in the top bar

### 2. Enable YouTube Data API v3

1. **Navigate to APIs & Services:**
   - Go to "APIs & Services" → "Library"

2. **Search for YouTube Data API:**
   - Search for "YouTube Data API v3"
   - Click on the result

3. **Enable the API:**
   - Click "Enable" button
   - Wait for the API to be enabled

### 3. Create OAuth 2.0 Credentials

1. **Go to Credentials:**
   - Navigate to "APIs & Services" → "Credentials"

2. **Create credentials:**
   - Click "Create Credentials" → "OAuth client ID"

3. **Configure OAuth consent screen:**
   - If prompted, configure the consent screen:
     - **User Type:** External
     - **App name:** IotaPlayer
     - **User support email:** Your email
     - **Developer contact information:** Your email
   - Click "Save and Continue" through all steps

4. **Create OAuth client ID:**
   - **Application type:** Desktop app
   - **Name:** IotaPlayer Desktop
   - Click "Create"

5. **Download credentials:**
   - Click "Download JSON"
   - Save the file as `client_secret.json`
   - Keep this file secure and private

### 4. Configure IotaPlayer

1. **Place the credentials file:**
   - Put `client_secret.json` in a secure location
   - Remember the full path to the file

2. **Open IotaPlayer Settings:**
   - Launch IotaPlayer
   - Click "Settings" button
   - Go to "Google" tab

3. **Set the client secret file path:**
   - Enter the full path to your `client_secret.json`
   - Example: `/home/user/secure/client_secret.json`
   - Click "Save"

4. **Restart IotaPlayer:**
   - Close and reopen the application
   - Settings will be applied

## First-Time Authentication

### When You Use YouTube Features

1. **Trigger authentication:**
   - Try to upload a playlist or use YouTube features
   - IotaPlayer will prompt for authentication

2. **Browser authentication:**
   - A browser window will open
   - Sign in with your Google account
   - Grant the requested permissions

3. **Complete setup:**
   - After successful authentication, a `token.pickle` file is created
   - This file stores your OAuth tokens for future use
   - You won't need to authenticate again unless tokens expire

## File Naming Convention

### For YouTube Integration

For best YouTube integration, name your audio files like this:
```
Artist - Title [YouTubeID].mp3
```

### Examples:
- `Artist - Song [dQw4w9WgXcQ].mp3`
- `Artist (feat. Other) - Song (Remix) [abcdef12345].mp3`
- `Artist - Song Title [1234567890].mp3`

### YouTube ID Format:
- **11 characters** long
- **Alphanumeric** characters
- **Hyphens and underscores** allowed
- **Case sensitive**

## Security Best Practices

### File Security
```bash
# Secure your credentials file
chmod 600 client_secret.json
chmod 600 token.pickle

# Store in secure location
mv client_secret.json ~/.config/IotaPlayer/
mv token.pickle ~/.config/IotaPlayer/
```

### Never Share Credentials
- **Don't commit** `client_secret.json` to public repositories
- **Don't share** your credentials with others
- **Keep backups** in a secure location
- **Rotate credentials** if compromised

### API Quota Management
- **Monitor usage** in Google Cloud Console
- **Stay within limits** to avoid rate limiting
- **Plan for quota increases** if needed

## Troubleshooting

### Common Issues

#### "Invalid client_secret.json"
**Solutions:**
1. **Check file path** in Settings
2. **Verify file exists** and is readable
3. **Ensure file format** is correct JSON
4. **Check file permissions**

#### "Authentication failed"
**Solutions:**
1. **Delete token.pickle** to re-authenticate
2. **Check internet connection**
3. **Verify Google account** has YouTube access
4. **Check API quotas** in Google Cloud Console

#### "API quota exceeded"
**Solutions:**
1. **Wait for quota reset** (daily/monthly limits)
2. **Request quota increase** in Google Cloud Console
3. **Optimize API usage** to reduce calls
4. **Use caching** to reduce API requests

#### "YouTube upload fails"
**Solutions:**
1. **Check file naming** convention
2. **Verify YouTube IDs** are valid
3. **Ensure audio files** are accessible
4. **Check playlist format** is correct


### Reset Authentication
If authentication is corrupted:
```bash
# Remove token file
rm token.pickle

# Restart IotaPlayer
# Re-authenticate when prompted
```

## Advanced Configuration

### Custom OAuth Scopes
```python
# Custom scopes for specific permissions
SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtube.readonly'
]
```

### API Quota Optimization
```python
# Implement rate limiting
import time

def rate_limited_api_call(func):
    def wrapper(*args, **kwargs):
        time.sleep(0.1)  # 100ms delay between calls
        return func(*args, **kwargs)
    return wrapper
```

### Error Handling
```python
# Robust error handling example
try:
    service = get_authenticated_service()
    # API call here
except Exception as e:
    logging.error(f"YouTube API error: {e}")
    # Handle error gracefully
```

## API Limits and Quotas

### YouTube Data API v3 Limits
- **Queries per day:** 10,000 units
- **Queries per 100 seconds per user:** 300 units
- **Queries per 100 seconds:** 3,000 units

### Cost Considerations
- **Free tier:** 10,000 units per day
- **Paid tier:** $5 per 1,000 additional units
- **Monitor usage** in Google Cloud Console

### Best Practices
1. **Cache results** when possible
2. **Batch requests** to reduce API calls
3. **Implement retry logic** for failed requests
4. **Monitor quota usage** regularly

## Support and Resources

### Official Documentation
- **YouTube Data API:** [developers.google.com/youtube/v3](https://developers.google.com/youtube/v3)
- **Google Cloud Console:** [console.cloud.google.com](https://console.cloud.google.com)
- **OAuth 2.0 Guide:** [developers.google.com/identity/protocols/oauth2](https://developers.google.com/identity/protocols/oauth2)

### Community Support
- **GitHub Issues:** Report bugs and request features
- **Stack Overflow:** Search for similar problems
- **Google Cloud Support:** For API-specific issues

### Getting Help
When seeking help, include:
1. **Error messages** from logs
2. **Steps to reproduce** the issue
3. **Your setup** (OS, IotaPlayer version)
4. **API quota status** from Google Cloud Console

---

**Related Pages:**
- [User Guide](User-Guide) - How to use YouTube features
- [Configuration](Configuration) - Settings for Google integration
- [Troubleshooting](Troubleshooting) - Common problems and solutions 
# Troubleshooting Guide

This guide helps you solve common issues with IotaPlayer.

## Common Issues

### Audio Playback Problems

#### No Sound Playing
**Symptoms:** Audio files don't play, no sound output

**Solutions:**
1. **Check Volume Settings:**
   - Ensure volume slider is not at 0%
   - Check system volume is not muted
   - Verify audio device is selected

2. **Check Audio Codecs (Windows):**
   ```cmd
   # Install K-Lite Codec Pack
   # Download from: https://codecguide.com/download_kl.htm
   ```

3. **Check GStreamer (Linux):**
   ```bash
   # Install additional codecs
   sudo apt install gstreamer1.0-plugins-ugly gstreamer1.0-libav
   
   # For Arch Linux
   sudo pacman -S gst-plugins-ugly gst-libav
   ```

4. **Check File Format:**
   - Ensure audio files are in supported formats (.mp3, .flac, .ogg, .wav, .m4a)
   - Try a different audio file to test

#### Audio Cuts Out or Stutters
**Symptoms:** Audio plays but cuts out, stutters, or has gaps

**Solutions:**
1. **Check System Resources:**
   - Close other applications using audio
   - Check CPU and memory usage
   - Restart IotaPlayer

2. **Update Audio Drivers:**
   - Update system audio drivers
   - Check for driver conflicts

3. **Check Audio Settings:**
   - Try different audio output devices
   - Adjust buffer settings if available

### Qt Platform Errors (Linux)

#### "xcb" or Platform Plugin Errors
**Symptoms:** Application fails to start with Qt platform errors

**Solutions:**
1. **Install Required Libraries:**
   ```bash
   # Ubuntu/Debian
   sudo apt install libxcb-xinerama0 libxcb1 libx11-xcb1 libgl1-mesa-glx
   
   # Arch Linux
   sudo pacman -S libxcb xorg-xdpyinfo
   ```

2. **Force XCB Platform (Wayland):**
   ```bash
   export QT_QPA_PLATFORM=xcb
   python main.py
   ```

3. **Check Display Server:**
   ```bash
   echo $XDG_SESSION_TYPE
   # If "wayland", try switching to X11
   ```

### Discord Integration Issues

#### Discord Rich Presence Not Working
**Symptoms:** Discord status doesn't update with current song

**Solutions:**
1. **Check Discord Settings:**
   - Ensure Discord is running
   - Verify Discord has necessary permissions
   - Check if Discord is in focus

2. **Verify Client ID:**
   - Check Settings > Discord tab
   - Ensure Client ID is correct: `1150680286649143356`
   - Try creating your own Discord application

3. **Check Network:**
   - Ensure internet connection is stable
   - Check firewall settings
   - Try restarting Discord

4. **Reset Discord Integration:**
   - Disable Discord integration in Settings
   - Restart IotaPlayer
   - Re-enable Discord integration

#### Discord Disconnects Frequently
**Symptoms:** Discord integration stops working periodically

**Solutions:**
1. **Check Auto-reconnect:**
   - Ensure auto-reconnect is enabled in Settings
   - Check Discord connection status in logs

2. **Network Issues:**
   - Check internet stability
   - Try different network if possible
   - Check for VPN interference

### YouTube Integration Problems

#### YouTube Upload Fails
**Symptoms:** Cannot upload playlists to YouTube

**Solutions:**
1. **Check Google API Setup:**
   - Verify client_secret.json file path in Settings
   - Ensure file exists and is readable
   - Check Google Cloud Console setup

2. **Authentication Issues:**
   - Delete `token.pickle` file to re-authenticate
   - Ensure Google account has YouTube access
   - Check API quotas in Google Cloud Console

3. **File Naming:**
   - Ensure files follow naming convention: `Artist - Title [YouTubeID].mp3`
   - Check that YouTube IDs are valid
   - Verify audio files are accessible

#### YouTube Video Opening Issues
**Symptoms:** Cannot open YouTube videos for current songs

**Solutions:**
1. **Check File Naming:**
   - Ensure YouTube ID is in filename: `[YouTubeID]`
   - Verify ID format is correct
   - Check for special characters in filenames

2. **Browser Issues:**
   - Ensure default browser is set
   - Check browser can open YouTube
   - Try manual URL construction

### Playlist Issues

#### Playlists Not Loading
**Symptoms:** Cannot load or see playlists

**Solutions:**
1. **Check Playlist Directory:**
   - Verify playlist folder path in Settings
   - Ensure folder exists and is accessible
   - Check file permissions

2. **Check Playlist Files:**
   - Ensure .json files are valid
   - Check file encoding (should be UTF-8)
   - Verify JSON syntax is correct

3. **Reset Playlist Settings:**
   - Reset playlist folder to default
   - Restart IotaPlayer
   - Re-add playlists

#### Playlist Maker Not Working
**Symptoms:** Cannot create or edit playlists

**Solutions:**
1. **Check File Permissions:**
   - Ensure write access to playlist directory
   - Check disk space availability
   - Verify folder permissions

2. **Check Audio Files:**
   - Ensure audio files are accessible
   - Check file formats are supported
   - Verify file paths are correct

### Performance Issues

#### Application Runs Slowly
**Symptoms:** IotaPlayer is sluggish or unresponsive

**Solutions:**
1. **Check System Resources:**
   - Monitor CPU and memory usage
   - Close unnecessary applications
   - Restart IotaPlayer

2. **Check Log Files:**
   - Review `combined_app.log` for errors
   - Look for memory leaks or errors
   - Check for infinite loops

3. **Optimize Settings:**
   - Reduce cache sizes
   - Disable unnecessary features
   - Use lighter theme

#### High Memory Usage
**Symptoms:** Application uses excessive memory

**Solutions:**
1. **Clear Caches:**
   - Clear cover art cache
   - Restart application
   - Check for memory leaks

2. **Optimize Playlists:**
   - Reduce playlist sizes
   - Remove unused playlists
   - Check for duplicate entries

### Installation Issues

#### Python Version Problems
**Symptoms:** "Python 3.13+ required" errors

**Solutions:**
1. **Check Python Version:**
   ```bash
   python3 --version
   # Should show 3.13 or higher
   ```

2. **Install Python 3.13+:**
   ```bash
   # Ubuntu/Debian
   sudo apt install python3.13
   
   # Arch Linux
   sudo pacman -S python
   ```

3. **Use Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

#### Missing Dependencies
**Symptoms:** "No module named" errors

**Solutions:**
1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Specific Packages:**
   ```bash
   pip install PyQt6 PyQt6-Qt6 PyQt6-sip
   pip install mutagen pynput pypresence
   ```

3. **Check Virtual Environment:**
   - Ensure virtual environment is activated
   - Verify packages are installed in correct environment

### Update Issues

#### Update Check Fails
**Symptoms:** Cannot check for updates

**Solutions:**
1. **Check Internet Connection:**
   - Ensure stable internet connection
   - Check firewall settings
   - Try different network

2. **Check Version File:**
   - Verify `latest_version.txt` exists on GitHub
   - Check file format is correct
   - Ensure version comparison works

3. **Manual Update:**
   - Download latest release manually
   - Follow installation instructions
   - Check for breaking changes

## Getting Help

### Log Files
Check these log files for detailed error information:
- **`combined_app.log`:** Main application log
- **Console output:** Terminal/command prompt output
- **System logs:** OS-specific error logs

### Reporting Issues
When reporting issues, include:
1. **Operating System:** Windows/Linux version
2. **IotaPlayer Version:** Current version number
3. **Error Messages:** Exact error text
4. **Steps to Reproduce:** How to trigger the issue
5. **Log Files:** Relevant log entries
6. **System Information:** Hardware and software details

### Community Support
- **GitHub Issues:** [Report bugs here](https://github.com/vorlie/IotaPlayer/issues)
- **Discord Server:** Join for community support
- **Documentation:** Check this wiki for solutions

## Prevention Tips

### Regular Maintenance
1. **Keep Updated:** Regularly update IotaPlayer
2. **Clear Caches:** Periodically clear cover art cache
3. **Backup Playlists:** Keep backups of important playlists
4. **Monitor Logs:** Check logs for potential issues

### Best Practices
1. **Use Supported Formats:** Stick to .mp3, .flac, .ogg, .wav, .m4a
2. **Organize Files:** Keep audio files well-organized
3. **Regular Backups:** Backup configuration and playlists
4. **Test Features:** Test integrations after updates

---

**Related Pages:**
- [Installation](Installation) - Installation troubleshooting
- [Configuration](Configuration) - Settings issues
- [User Guide](User-Guide) - Feature usage help 
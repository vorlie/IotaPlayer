#!/usr/bin/env bash
set -e

# Define color codes for better output readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}IotaPlayer Linux Installer/Updater${NC}"
echo -e "${CYAN}--------------------------------${NC}"

# Function to display usage instructions
usage() {
    echo "Usage: $0 [install|update|uninstall]"
    echo "  install: Performs a fresh installation of IotaPlayer."
    echo "  update: Updates an existing IotaPlayer installation (removes old files and installs new)."
    echo "  uninstall: Removes the IotaPlayer installation."
    exit 1
}

# Default action is 'install' if no argument is provided
ACTION="install"

# Parse command-line arguments
if [ "$#" -gt 0 ]; then
    ACTION="$1"
    # Validate the provided action
    if [[ "$ACTION" != "install" && "$ACTION" != "update" && "$ACTION" != "uninstall" ]]; then
        usage # Show usage if an invalid action is given
    fi
fi

# Define a temp path for any temporary repo or files
TMP_REPO_PATH="/tmp/IotaPlayer_update"
REPO_URL="https://github.com/vorlie/IotaPlayer.git"

# Function to clone the repo into TMP_REPO_PATH if not present
clone_repo_if_needed() {
    if [ ! -d "$TMP_REPO_PATH/.git" ]; then
        echo -e "${BLUE}Cloning IotaPlayer repository into $TMP_REPO_PATH...${NC}"
        rm -rf "$TMP_REPO_PATH"
        git clone "$REPO_URL" "$TMP_REPO_PATH"
    else
        echo -e "${GREEN}Found existing repo at $TMP_REPO_PATH. Pulling latest changes...${NC}"
        cd "$TMP_REPO_PATH"
        git pull
        cd - > /dev/null
    fi
}

# Function to perform the core installation/update steps
# This function encapsulates the common logic for both install and update
perform_installation_steps() {
    local install_path="$1" # The target directory for installation

    # 1. Detect Linux distribution and install system dependencies
    echo -e "${BLUE}Detecting distribution and installing system dependencies...${NC}"
    if [ -f /etc/arch-release ]; then
        echo -e "${GREEN}Detected Arch Linux.${NC}"
        echo -e "${BLUE}Installing system dependencies...${NC}"
        sudo pacman -S --needed gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly gst-libav \
            qt6-multimedia
    elif [ -f /etc/debian_version ]; then
        echo -e "${GREEN}Detected Debian/Ubuntu.${NC}"
        echo -e "${BLUE}Installing system dependencies...${NC}"
        sudo apt update
        sudo apt install -y gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
            gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav \
            libxcb-xinerama0
    else
        echo -e "${RED}Unknown distro. Please install Python 3.13+, PyQt6, and GStreamer plugins manually.${NC}"
        # Continue script execution, but user might need to intervene
    fi

    # Clean up old build artifacts (dist, build directories, and virtual environment)
    # This ensures a fresh build for both initial install and update
    echo -e "${BLUE}Cleaning up previous build artifacts (dist, build, .venv)...${NC}"
    rm -rf dist build .venv

    # 2. Set up Python virtual environment and install Python dependencies
    echo -e "${BLUE}Setting up Python virtual environment...${NC}"
    python3 -m venv .venv
    echo -e "${BLUE}Activating venv and installing requirements...${NC}"
    source .venv/bin/activate
    pip install --upgrade pip
    #export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
    pip install -r requirements.txt --ignore-requires-python

    echo -e "${BLUE}Building the executable using PyInstaller...${NC}"
    # 3. Build the executable
    if [ -f IotaPlayerLinux.spec ]; then
        pyinstaller IotaPlayerLinux.spec --noconfirm
    else
        echo -e "${RED}PyInstaller spec file (IotaPlayerLinux.spec) not found! Cannot build executable.${NC}"
        exit 1
    fi

    echo -e "${BLUE}Copying built files to $install_path...${NC}"
    # 4. Copy built files to the specified installation directory
    mkdir -p "$install_path" # Ensure the directory exists
    cp -r dist/IotaPlayer/* "$install_path/" # Copy all contents from dist/IotaPlayer
    if [ -f icon.png ]; then
        cp icon.png "$install_path/icon.png" # Copy the application icon if it exists
    fi
    if [ -f linux_installer.sh ]; then
        cp linux_installer.sh "$install_path/linux_installer.sh" # Copy the update script if it exists
    fi
    if [ -f LICENSE ]; then
        cp LICENSE "$install_path/LICENSE" # Copy the license if it exists
    fi

    # CLEANUP TEMP FILES/REPO
    if [ -d "$TMP_REPO_PATH" ]; then
        echo -e "${BLUE}Cleaning up temporary update files at $TMP_REPO_PATH...${NC}"
        rm -rf "$TMP_REPO_PATH"
    fi

    echo -e "${BLUE}Checking for available Qt6 style plugins...${NC}"
    QT6_PLUGIN_DIR="/usr/lib/qt6/plugins/styles"
    AVAILABLE_PLUGINS=()
    if [ -d "$QT6_PLUGIN_DIR" ]; then
        for f in "$QT6_PLUGIN_DIR"/*.so; do
            [ -e "$f" ] || continue
            plugin_name=$(basename "$f" .so)
            AVAILABLE_PLUGINS+=("$plugin_name")
        done
    fi

    if [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* || "$DESKTOP_SESSION" == *"plasma"* || "$KDE_FULL_SESSION" == "true" ]]; then
        echo -e "${GREEN}KDE Plasma desktop environment detected.${NC}"
        DEFAULT_QT6_THEME="breeze6"
    else
        echo -e "${YELLOW}Non-KDE desktop environment detected. Skipping theme symlink creation.${NC}"
        DEFAULT_QT6_THEME=""
    fi

    if [ ${#AVAILABLE_PLUGINS[@]} -gt 0 ]; then
        echo -e "${CYAN}Available Qt6 style plugins:${NC}"
        select plugin in "${AVAILABLE_PLUGINS[@]}" "Skip"; do
            if [[ "$plugin" == "Skip" ]]; then
                qt6_theme=""
                break
            elif [[ -n "$plugin" ]]; then
                qt6_theme="$plugin"
                break
            else
                echo "Invalid selection."
            fi
        done
        # If nothing selected, fallback to default
        qt6_theme=${qt6_theme:-$DEFAULT_QT6_THEME}
    else
        echo -e "${YELLOW}No Qt6 style plugins found in $QT6_PLUGIN_DIR.${NC}"
        qt6_theme="$DEFAULT_QT6_THEME"
    fi

    if [ -n "$qt6_theme" ]; then
        SYSTEM_QT6_PLUGIN="$QT6_PLUGIN_DIR/${qt6_theme}.so"
        APP_QT6_PLUGIN_DIR="$install_path/_internal/PyQt6/Qt6/plugins/styles"
        APP_QT6_PLUGIN_TARGET="$APP_QT6_PLUGIN_DIR/${qt6_theme}.so"

        mkdir -p "$APP_QT6_PLUGIN_DIR"

        if [ -f "$SYSTEM_QT6_PLUGIN" ]; then
            if [ ! -f "$APP_QT6_PLUGIN_TARGET" ] || [ ! -L "$APP_QT6_PLUGIN_TARGET" ]; then
                echo -e "${BLUE}Creating symlink for Qt6 theme: ${SYSTEM_QT6_PLUGIN} -> ${APP_QT6_PLUGIN_TARGET}${NC}"
                ln -sf "$SYSTEM_QT6_PLUGIN" "$APP_QT6_PLUGIN_TARGET"
                echo -e "${GREEN}Qt6 theme symlink created successfully.${NC}"
            else
                echo -e "${YELLOW}Qt6 theme plugin already exists or is symlinked in the installation directory. Skipping symlink creation.${NC}"
            fi
        else
            echo -e "${YELLOW}Warning: System Qt6 theme plugin not found at ${SYSTEM_QT6_PLUGIN}. Skipping symlink creation.${NC}"
        fi
    else
        echo -e "${YELLOW}No Qt6 theme plugin specified. Skipping symlink creation.${NC}"
    fi

    echo -e "${BLUE}Generating launcher script...${NC}"
    # 5. Generate the run_iotaplayer.sh launcher script
    cat > "$install_path/run_iotaplayer.sh" <<EOF
#!/usr/bin/env bash
# Set GStreamer plugin paths for the executable
export GST_PLUGIN_SCANNER=/usr/lib/gstreamer-1.0/gst-plugin-scanner
export GST_PLUGIN_PATH=/usr/lib/gstreamer-1.0
export GST_PLUGIN_SYSTEM_PATH=/usr/lib/gstreamer-1.0
# Execute the IotaPlayer application
exec "$install_path/IotaPlayer"
EOF
    chmod +x "$install_path/run_iotaplayer.sh" # Make the launcher script executable

    echo -e "${GREEN}Launcher script 'run_iotaplayer.sh' created at $install_path.${NC}"

    # 6. (Optional) Generate .desktop file for desktop integration
    echo -en "${CYAN}Create desktop shortcut? (y/n): ${NC}"
    read create_shortcut
    if [[ "$create_shortcut" =~ ^[Yy]$ ]]; then
        cat > "$install_path/IotaPlayer.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=IotaPlayer
Exec=$install_path/run_iotaplayer.sh
Icon=$install_path/icon.png
Comment=Music player
Categories=AudioVideo;Player;
Terminal=false
EOF
        # Copy the .desktop file to the user's applications directory
        cp "$install_path/IotaPlayer.desktop" ~/.local/share/applications/
        chmod +x ~/.local/share/applications/IotaPlayer.desktop # Make the desktop file executable
        echo -e "${GREEN}Shortcut created. You may need to log out and back in for it to appear.${NC}"
    fi

    echo -e "${GREEN}Operation complete! You can launch IotaPlayer with: $install_path/run_iotaplayer.sh${NC}"
}

# Main logic based on the chosen action (install or update)
if [ "$ACTION" = "install" ] || [ "$ACTION" = "update" ]; then
    clone_repo_if_needed
    PROJECT_ROOT="$TMP_REPO_PATH"
else
    # For uninstall, use the install path as before
    PROJECT_ROOT=""
fi

# Change to the project root directory for subsequent operations
if [ -n "$PROJECT_ROOT" ]; then
    cd "$PROJECT_ROOT"
fi

if [ "$ACTION" = "install" ]; then
    echo -e "${CYAN}Performing fresh installation.${NC}"
    echo -en "${CYAN}Enter installation directory (default: $HOME/Apps/IotaPlayer): ${NC}"
    read -e install_path # Read user input for installation path
    install_path=${install_path:-$HOME/Apps/IotaPlayer} # Use default if input is empty

    # Check if the installation directory already exists
    if [ -d "$install_path" ]; then
        echo -e "${YELLOW}Warning: Installation directory '$install_path' already exists.${NC}"
        echo -en "${CYAN}Do you want to remove its contents before installing? (y/n): ${NC}"
        read confirm_remove
        if [[ "$confirm_remove" =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}Removing existing contents from $install_path...${NC}"
            rm -rf "$install_path"/* # Remove all files and subdirectories
        else
            echo -e "${YELLOW}Installation will proceed into existing directory. Files might be overwritten.${NC}"
        fi
    fi
    # Call the function to perform the installation steps
    perform_installation_steps "$install_path"

elif [ "$ACTION" = "update" ]; then
    echo -e "${CYAN}Performing update.${NC}"
    echo -en "${CYAN}Enter the existing installation directory (default: $HOME/Apps/IotaPlayer): ${NC}"
    read -e install_path # Read user input for the existing installation path
    install_path=${install_path:-$HOME/Apps/IotaPlayer} # Use default if input is empty

    # Check if the specified installation directory exists for an update
    if [ -d "$install_path" ]; then
        echo -e "${YELLOW}Found existing installation at '$install_path'.${NC}"
        echo -en "${CYAN}Are you sure you want to update? This will remove all existing files in this directory and install the new version. (y/n): ${NC}"
        read confirm_update
        if [[ "$confirm_update" =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}Removing old installation from $install_path...${NC}"
            rm -rf "$install_path"/* # Remove all files and subdirectories from the old install
            # Call the function to perform the installation steps
            perform_installation_steps "$install_path"
        else
            echo -e "${YELLOW}Update cancelled.${NC}"
            exit 0 # Exit gracefully if user cancels
        fi
    else
        echo -e "${RED}Error: No existing installation found at '$install_path'. Please run with 'install' first or specify the correct path.${NC}"
        exit 1 # Exit with an error code
    fi
elif [ "$ACTION" = "uninstall" ]; then
    echo -e "${CYAN}Performing uninstallation.${NC}"
    echo -en "${CYAN}Enter the installation directory to remove (default: $HOME/Apps/IotaPlayer): ${NC}"
    read -e install_path # Read user input for the installation path to remove
    install_path=${install_path:-$HOME/Apps/IotaPlayer} # Use default if input is empty

    # Check if the specified installation directory exists for uninstallation
    if [ -d "$install_path" ]; then
        echo -e "${YELLOW}Found existing installation at '$install_path'.${NC}"
        echo -en "${CYAN}Are you sure you want to uninstall? This will remove all existing files in this directory. (y/n): ${NC}"
        read confirm_uninstall
        if [[ "$confirm_uninstall" =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}Removing installation from $install_path...${NC}"
            rm -rf "$install_path" # Remove the entire installation directory
            echo -e "${GREEN}Uninstallation complete. IotaPlayer has been removed from $install_path.${NC}"
            # CLEANUP TEMP FILES/REPO
            if [ -d "$TMP_REPO_PATH" ]; then
                echo -e "${BLUE}Cleaning up temporary update files at $TMP_REPO_PATH...${NC}"
                rm -rf "$TMP_REPO_PATH"
            fi
        else
            echo -e "${YELLOW}Uninstallation cancelled.${NC}"
            exit 0 # Exit gracefully if user cancels
        fi
    else
        echo -e "${RED}Error: No existing installation found at '$install_path'. Please check the path or run with 'install' first.${NC}"
        exit 1 # Exit with an error code
    fi
fi

# Maintainer: vorlie <vorlie0961@gmail.com>
pkgname=iotaplayer-git
_pkgname=IotaPlayer
pkgver=0
pkgrel=1
pkgdesc="A cross-platform music player built with Python and Qt (AUR git version)"
arch=('x86_64')
url="https://github.com/vorlie/IotaPlayer"
license=('MIT')
depends=(
  'gstreamer'
  'gst-plugins-base'
  'gst-plugins-good'
  'gst-plugins-bad'
  'gst-plugins-ugly'
  'gst-libav'
  'qt6-multimedia'
  'python'
)
makedepends=(
  'git'
  'python-pip'
  'python-setuptools'
)
source=("$_pkgname::git+https://github.com/vorlie/IotaPlayer.git")
sha256sums=('SKIP')

pkgver() {
  cd "$srcdir/$_pkgname"
  printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

prepare() {
  cd "$_pkgname"
  echo "Setting up Python virtual environment..."
  python -m venv .venv --clear
  source .venv/bin/activate
  echo "Activating venv and installing requirements..."
  pip install --upgrade pip
  pip install -r requirements.txt --ignore-requires-python
}

build() {
  cd "$_pkgname"
  source .venv/bin/activate
  echo "Building the executable with PyInstaller..."
  if [ -f IotaPlayerLinux.spec ]; then
      pyinstaller IotaPlayerLinux.spec --noconfirm
  else
      echo "Error: PyInstaller spec file not found!"
      exit 1
  fi
}

package() {
  cd "$_pkgname"
  local install_dir="$pkgdir/usr/lib/$pkgname"
  mkdir -p "$install_dir"
  echo "Copying built files to $install_dir..."
  cp -r dist/IotaPlayer/* "$install_dir/"
  if [ -f icon.png ]; then
      echo "Copying icon.png..."
      mkdir -p "$pkgdir/usr/share/icons/hicolor/scalable/apps/"
      install -m644 icon.png "$pkgdir/usr/share/icons/hicolor/scalable/apps/iotaplayer.png"
  fi

  echo "Generating launcher script in /usr/bin/iotaplayer..."
  mkdir -p "$pkgdir/usr/bin/"
  cat > "$pkgdir/usr/bin/iotaplayer" <<EOF
#!/usr/bin/env bash
export GST_PLUGIN_SCANNER=/usr/lib/gstreamer-1.0/gst-plugin-scanner
export GST_PLUGIN_PATH=/usr/lib/gstreamer-1.0
export GST_PLUGIN_SYSTEM_PATH=/usr/lib/gstreamer-1.0
exec "$install_dir/IotaPlayer"
EOF
  chmod +x "$pkgdir/usr/bin/iotaplayer"

  echo "Generating .desktop file..."
  mkdir -p "$pkgdir/usr/share/applications/"
  cat > "$pkgdir/usr/share/applications/iotaplayer.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=IotaPlayer
Exec=/usr/bin/iotaplayer
Icon=iotaplayer
Comment=Music player
Categories=AudioVideo;Player;
Terminal=false
EOF
  chmod +x "$pkgdir/usr/share/applications/iotaplayer.desktop"
}

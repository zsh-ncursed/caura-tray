# Maintainer: Your Name <your.email@example.com>
pkgname=caura-tray
pkgver=1.0.0
pkgrel=1
pkgdesc="Caura Tray - A desktop launcher application for Linux with system tray integration"
arch=('any')
url="https://github.com/yourusername/caura-tray"
license=('MIT')
depends=('python' 'python-gobject' 'python-dbus' 'python-pillow' 'libappindicator-gtk3')
makedepends=('python-setuptools')
source=("caura-tray-$pkgver.tar.gz::https://github.com/yourusername/caura-tray/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')  # Replace with actual checksum or use 'SKIP' for development

prepare() {
    cd "$srcdir/caura-tray-$pkgver"
    # Any preparation steps if needed
}

build() {
    cd "$srcdir/caura-tray-$pkgver"
    # Any build steps if needed
}

package() {
    cd "$srcdir/caura-tray-$pkgver"
    
    # Create necessary directories
    install -dm755 "$pkgdir/usr/bin"
    install -dm755 "$pkgdir/usr/lib/caura-tray"
    install -dm755 "$pkgdir/usr/share/licenses/$pkgname"
    install -dm755 "$pkgdir/usr/share/doc/$pkgname"
    
    # Install application files
    install -m644 launcher.py dbus_integration.py launcher_logic.py import_apps.py "$pkgdir/usr/lib/caura-tray/"
    cp -r gui/ parser/ storage/ tray/ tests/ "$pkgdir/usr/lib/caura-tray/"
    
    # Install run script
    install -Dm755 run_launcher.sh "$pkgdir/usr/bin/caura-tray"
    
    # Install desktop file
    install -Dm644 tray-launcher.desktop "$pkgdir/usr/share/applications/tray-launcher.desktop"
    
    # Install documentation
    install -m644 README.md RUNNING.md "$pkgdir/usr/share/doc/$pkgname/"
    install -m644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/"
    
    # Create symlink for compatibility if needed
    ln -sf /usr/lib/caura-tray/run_launcher.sh "$pkgdir/usr/bin/caura-tray-run"
}

# vim:set ts=2 sw=2 et:
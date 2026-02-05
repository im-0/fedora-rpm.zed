%global source_date_epoch_from_changelog 0
%global __brp_mangle_shebangs_exclude_from ^/usr/src/.*$

%global crate zed
%global app_id dev.zed.Zed


Name:           zed
Version:        0.222.2
Release:        1.im0%{?dist}
Summary:        a high-performance multiplayer code editor

License:        GPL3 AGPL
URL:            https://github.com/zed-industries/zed
Source0:        https://github.com/zed-industries/zed/archive/v%{version}/%{name}-%{version}.tar.gz

# Contains zed-$VERSION/vendor/*.
#     $ cargo vendor
#     $ mkdir zed-X.Y.Z
#     $ mv vendor zed-X.Y.Z/
#     $ tar vcJf zed-X.Y.Z.cargo-vendor.tar.xz zed-X.Y.Z
Source1:    %{name}-%{version}.cargo-vendor.tar.xz
Source2:    config.toml
Source3:    logo_96.svg
Source4:    config-mold.toml

# Version strings are hardcoded in ./vendor/webrtc-sys-build/src/lib.rs
Source401:  https://github.com/livekit/client-sdk-rust/releases/download/webrtc-b99fd2c-6/webrtc-linux-x64-release.zip
Source402:  https://github.com/livekit/client-sdk-rust/releases/download/webrtc-b99fd2c-6/webrtc-linux-arm64-release.zip

Patch0:     0001-Support-enabling-features-by-environment-variable.patch

BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc
BuildRequires:  g++
BuildRequires:  alsa-lib-devel
BuildRequires:  fontconfig-devel
BuildRequires:  wayland-devel
BuildRequires:  libxkbcommon-x11-devel
BuildRequires:  openssl-devel
BuildRequires:  libzstd-devel
BuildRequires:  perl-FindBin
BuildRequires:  perl-IPC-Cmd
BuildRequires:  perl-File-Compare
BuildRequires:  perl-File-Copy
BuildRequires:  perl-lib
BuildRequires:  vulkan-loader
BuildRequires:  libcurl-devel
BuildRequires:  clang
BuildRequires:  cmake
BuildRequires:  mold

### for the desktop file
BuildRequires:  desktop-file-utils

ExclusiveArch:  x86_64 aarch64


%description
Zed is a high-performance, multiplayer code editor from the creators of Atom and Tree-sitter. It's also open source.

%prep
%setup -q -D -T -b0 -n %{crate}-%{version}
%setup -q -D -T -b1 -n %{crate}-%{version}

%patch -P0 -p1

cat %{SOURCE2} >>.cargo/config.toml
cat %{SOURCE4} >>.cargo/config.toml

%ifarch x86_64
%setup -q -D -T -b401 -n %{crate}-%{version}
%endif
%ifarch aarch64
%setup -q -D -T -b402 -n %{crate}-%{version}
%endif

export DO_STARTUP_NOTIFY="true"
export APP_ID="%app_id"
export APP_ICON="%app_id"
export APP_NAME="Zed Editor"
export APP_CLI="zed"
export APP_ARGS="%U"
export ZED_RELEASE_CHANNEL=stable

envsubst < "crates/zed/resources/zed.desktop.in" > $APP_ID.desktop
envsubst < "crates/zed/resources/flatpak/zed.metainfo.xml.in" > $APP_ID.metainfo.xml


%build
export ZED_UPDATE_EXPLANATION="Please use the package manager to update zed."

# Check https://pagure.io/fedora-rust/rust2rpm/blob/main/f/data/macros.rust for
# rust-specific variables.
export RUSTC_BOOTSTRAP=1

# TODO: Generate licenses
#script/generate-licenses
touch assets/licenses.md

%ifarch x86_64
export LK_CUSTOM_WEBRTC="$( pwd )/../linux-x64-release"
%endif
%ifarch aarch64
export LK_CUSTOM_WEBRTC="$( pwd )/../linux-arm64-release"
%endif

export RUSTFLAGS="-Copt-level=3 -Cdebuginfo=2 -Ccodegen-units=16 -Clink-arg=-fuse-ld=mold -Cstrip=none -Cforce-frame-pointers=yes -Clink-arg=-specs=/usr/lib/rpm/redhat/redhat-package-notes --cap-lints=warn"

# Build CLI
cargo build %{__cargo_common_opts} --release --frozen --package cli

# Build Editor
cargo build %{__cargo_common_opts} --release --frozen --package zed

%install
install -Dm755 target/release/zed %{buildroot}%{_libexecdir}/zed-editor
install -Dm755 target/release/cli %{buildroot}%{_bindir}/zed
#install -Dm755 target/release/zed %{buildroot}%{_bindir}/zed

desktop-file-install                                    \
--dir=%{buildroot}%{_datadir}/applications              \
%app_id.desktop

#install -Dm644 %app_id.desktop %{buildroot}%{_datadir}/applications/%app_id.desktop
#install -Dm644 crates/zed/resources/app-icon.png %{buildroot}%{_datadir}/pixmaps/%app_id.png
install -Dm644 %{SOURCE3} %{buildroot}%{_datadir}/pixmaps/%app_id.svg
install -Dm644 %app_id.metainfo.xml %{buildroot}%{_metainfodir}/%app_id.metainfo.xml


%files
%license LICENSE-* assets/licenses.md
%{_bindir}/zed
%{_libexecdir}/zed-editor
%{_datadir}/applications/%app_id.desktop
%{_datadir}/pixmaps/%app_id.svg
%{_metainfodir}/%app_id.metainfo.xml


%changelog

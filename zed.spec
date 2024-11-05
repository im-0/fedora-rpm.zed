%global source_date_epoch_from_changelog 0
%global __brp_mangle_shebangs_exclude_from ^/usr/src/.*$

%global crate zed
%global app_id dev.zed.Zed


Name:           zed
Version:        0.159.10
Release:        1%{?dist}
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

### for the desktop file
BuildRequires:  desktop-file-utils

%description
Zed is a high-performance, multiplayer code editor from the creators of Atom and Tree-sitter. It's also open source.

%prep
%setup -q -D -T -b0 -n %{crate}-%{version}
%setup -q -D -T -b1 -n %{crate}-%{version}

cat %{SOURCE2} >>.cargo/config.toml

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

# Build CLI
pushd crates/cli/
cargo build %{__cargo_common_opts} --release --frozen
popd

# Build Editor
pushd crates/zed/
cargo build %{__cargo_common_opts} --release --frozen
popd

%install
install -Dm755 target/release/zed %{buildroot}%{_libexecdir}/zed-editor
install -Dm755 target/release/cli %{buildroot}%{_bindir}/zed
#install -Dm755 target/release/zed %{buildroot}%{_bindir}/zed

desktop-file-install                                    \
--dir=%{buildroot}%{_datadir}/applications              \
%app_id.desktop

#install -Dm644 %app_id.desktop %{buildroot}%{_datadir}/applications/%app_id.desktop
#install -Dm644 crates/zed/resources/app-icon.png %{buildroot}%{_datadir}/pixmaps/%app_id.png
install -Dm644 assets/icons/logo_96.svg %{buildroot}%{_datadir}/pixmaps/%app_id.svg
install -Dm644 %app_id.metainfo.xml %{buildroot}%{_metainfodir}/%app_id.metainfo.xml


%files
%license LICENSE-* assets/licenses.md
%{_bindir}/zed
%{_libexecdir}/zed-editor
%{_datadir}/applications/%app_id.desktop
%{_datadir}/pixmaps/%app_id.svg
%{_metainfodir}/%app_id.metainfo.xml


%changelog

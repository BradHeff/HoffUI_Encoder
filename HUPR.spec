Name:           HUPR
Version:        1.0.1
Release:        1%{?dist}
Summary:        Horizon Password Reset is uesed to reset AD users
License: GPLv3+
URL: https://github.com/BradHeff/Horizon-Bulkuser-Importer-Canvas
Source0: %{name}-%{version}.tar.gz

BuildRequires: python3
Requires:      python3, python3-tkinter, python3-pillow, python3-pillow-tk, python3-pip


%description
Horizon Password Reset is uesed to reset the password of AD users

%install
mkdir -p %{buildroot}/usr/local/bin/
mkdir -p %{buildroot}/usr/lib/Horizon_Password_Reset/
mkdir -p %{buildroot}/usr/share/pixmaps/
mkdir -p %{buildroot}/usr/share/applications/


cp %{_topdir}/BUILD/HUPR/HUPR %{buildroot}/usr/local/bin/HUPR
cp %{_topdir}/BUILD/HUPR/horizon_password_reset.desktop %{buildroot}/usr/share/applications/horizon_password_reset.desktop
cp %{_topdir}/BUILD/HUPR/hcs.png %{buildroot}/usr/share/pixmaps/hcs.png
cp %{_topdir}/BUILD/HUPR/Functions.py %{buildroot}/usr/lib/Horizon_Password_Reset/Functions.py
cp %{_topdir}/BUILD/HUPR/main.py %{buildroot}/usr/lib/Horizon_Password_Reset/main.py
cp %{_topdir}/BUILD/HUPR/Gui.py %{buildroot}/usr/lib/Horizon_Password_Reset/Gui.py
cp %{_topdir}/BUILD/HUPR/icon.py %{buildroot}/usr/lib/Horizon_Password_Reset/icon.py
cp %{_topdir}/BUILD/HUPR/user.py %{buildroot}/usr/lib/Horizon_Password_Reset/user.py



%post
pip3 install --user pillow ttkbootstrap ldap3 flask pyOpenSSL tkthread git+https://github.com/psf/black
chmod +x /usr/local/bin/HUPR
pwusr=$(logname)
pver=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

config_dir="/home/$pwusr/.local/lib/python$pver/site-packages/ttkbootstrap/themes/"
cp /usr/lib/Horizon_Password_Reset/user.py $config_dir/user.py

%files

/usr/local/bin/HUPR
/usr/share/applications/horizon_password_reset.desktop
/usr/lib/Horizon_Password_Reset/Gui.py
/usr/lib/Horizon_Password_Reset/Functions.py
/usr/lib/Horizon_Password_Reset/main.py
/usr/lib/Horizon_Password_Reset/icon.py
/usr/lib/Horizon_Password_Reset/user.py
/usr/share/pixmaps/hcs.png


%changelog
* Mon Dec 23 2024 Brad Heffernan <brad.heffernan83@outlook.com>
- 

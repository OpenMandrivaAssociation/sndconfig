%define kudzu_version 1.1.40

Name: sndconfig
Version: 0.70
Release: %mkrel 19
License: GPL
Summary: The Red Hat Linux sound configuration tool
Group: System/Configuration/Hardware
BuildRequires: newt-devel pciutils-devel sharutils
BuildRequires: libslang-static-devel
Source: %{name}-%{version}.tar.bz2
Source1: %{name}.po
# (blino) include kudzu here since we don't want to release it
# ugly ? no ...
Source2: kudzu-%{kudzu_version}.tar.bz2
# (blino) use modprobe and be 2.6 aware (.ko modules detection)
Patch0: %{name}-0.70-use-modprobe.patch
Patch1: %{name}-0.64.9-mdkconf.patch
# (blino) get kudzu to build without sysfs patch in pciutils
Patch2: kudzu-1.1.40-comment_domain.patch
# (blino) statically link with included kudzu
Patch3: %{name}-0.70-link_kudzu.patch
Patch4: sndconfig-0.70-es-po.patch
# (blino) fix assembler errors, from kudzu-1.2.24
Patch5: kudzu-1.1.40-movl.patch
# (blino) use u_int8_t instead of byte, from kudzu-1.2.24
Patch6: kudzu-1.1.40-byte.patch
Patch7: kudzu-1.1.40-fix-ifmask.patch
Patch8: mips_buildfix.patch
# (blino) diet is needed to build kudzu
BuildRequires: dietlibc-devel
%ifarch %{ix86} alpha
Requires: isapnptools >= 1.16, sox, playmidi, kernel >= 2.2.0
%endif
Requires: awesfx
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
ExcludeArch: ppc x86_64
Prefix: %{_prefix}
URL: ftp://ftp.redhat.com/pub/linux/redhat/rawhide/SRPMS/SRPMS/

# (blino) use our own ugly find_requires script
# to exclude GLIBC_PRIVATE Requires
%define __find_requires %{_builddir}/%{name}-%{version}/find_requires.sh

%description
Sndconfig is a text based tool which sets up the configuration files you'll
need to use a sound card. Sndconfig can be used to set the proper sound type
for programs which use the /dev/dsp, /dev/audio and /dev/mixer devices. The
sound settings are saved by the aumix and sysV runlevel scripts.

Please use preferably program DrakConf to configure your sound-card. However
some configurations will fail with DrakConf, and you can try sndconfig in that
case.

%prep
%setup -q -a 2
# (blino) add a "kudzu" link so that patches don't depend on kudzu version
ln -s kudzu-%{kudzu_version} kudzu
%patch0 -p1
%patch1 -p1
%patch3 -p1
%patch4 -p0
pushd kudzu
%patch2 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
popd
%patch8 -p1 -b .mips

# (blino) find_requires script to exclude GLIBC_PRIVATE Requires
# (adapted from glibc spec file)
cat > find_requires.sh << EOF
%{_libdir}/rpm/find-requires %{buildroot} %{_target_cpu} | grep -v GLIBC_PRIVATE
exit 0
EOF
chmod +x find_requires.sh

%build
# (blino) first build libkudzu.a in kudzu subdirectory
%make -C kudzu libkudzu.a
%make RPM_OPT_FLAGS="$RPM_OPT_FLAGS"

%install
rm -rf $RPM_BUILD_ROOT

%makeinstall

mv $RPM_BUILD_ROOT%{_sbindir}/%{name}{,.real}
cat > $RPM_BUILD_ROOT%{_sbindir}/%{name} << EOF
#!/bin/sh
%{_sbindir}/%{name}.real && /sbin/generate-modprobe.conf > /etc/modprobe.d/sndconfig.conf
EOF
chmod +x $RPM_BUILD_ROOT%{_sbindir}/%{name}

mkdir -p $RPM_BUILD_ROOT%{_datadir}/locale/zh_TW.Big5/LC_MESSAGES
msgfmt %SOURCE1 -o $RPM_BUILD_ROOT%{_datadir}/locale/zh_TW.Big5/LC_MESSAGES/%{name}.mo

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr (-,root,root)
%{_sbindir}/%{name}
%{_sbindir}/%{name}.real
%dir %{_datadir}/%{name}/
%{_datadir}/%{name}/sample.au
%{_datadir}/%{name}/sample2.au
%{_datadir}/%{name}/sample.midi
%{_mandir}/man8/*.8*

%define kudzu_version 1.1.40

Name:		sndconfig
Version:	0.70
Release:	25
License:	GPL
Summary:	The Red Hat Linux sound configuration tool
Group:		System/Configuration/Hardware
URL: 		ftp://ftp.redhat.com/pub/linux/redhat/rawhide/SRPMS/SRPMS/
BuildRequires:	newt-devel
BuildRequires:	pciutils-devel
BuildRequires:	sharutils
BuildRequires:	slang-static-devel
Source: %{name}-%{version}.tar.bz2
Source1:	%{name}.po
# (blino) include kudzu here since we don't want to release it
# ugly ? no ...
Source2:	kudzu-%{kudzu_version}.tar.bz2
# (blino) use modprobe and be 2.6 aware (.ko modules detection)
Patch0:		%{name}-0.70-use-modprobe.patch
Patch1:		%{name}-0.64.9-mdkconf.patch
# (blino) get kudzu to build without sysfs patch in pciutils
Patch2:		kudzu-1.1.40-comment_domain.patch
# (blino) statically link with included kudzu
Patch3:		%{name}-0.70-link_kudzu.patch
Patch4:		sndconfig-0.70-es-po.patch
# (blino) fix assembler errors, from kudzu-1.2.24
Patch5:		kudzu-1.1.40-movl.patch
# (blino) use u_int8_t instead of byte, from kudzu-1.2.24
Patch6:		kudzu-1.1.40-byte.patch
Patch7:		kudzu-1.1.40-fix-ifmask.patch
Patch8:		mips_buildfix.patch
# (blino) diet is needed to build kudzu
BuildRequires:	dietlibc-devel
%ifarch %{ix86} alpha
Requires:	isapnptools >= 1.16, sox, playmidi, kernel >= 2.2.0
%endif
Requires:	awesfx
ExcludeArch: ppc x86_64

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
%make RPM_OPT_FLAGS="%{optflags}"

%install

%makeinstall

mv %{buildroot}%{_sbindir}/%{name}{,.real}
cat > %{buildroot}%{_sbindir}/%{name} << EOF
#!/bin/sh
%{_sbindir}/%{name}.real && /sbin/generate-modprobe.conf > /etc/modprobe.d/sndconfig.conf
EOF
chmod +x %{buildroot}%{_sbindir}/%{name}

mkdir -p %{buildroot}%{_datadir}/locale/zh_TW.Big5/LC_MESSAGES
msgfmt %SOURCE1 -o %{buildroot}%{_datadir}/locale/zh_TW.Big5/LC_MESSAGES/%{name}.mo

%find_lang %{name}


%files -f %{name}.lang
%{_sbindir}/%{name}
%{_sbindir}/%{name}.real
%dir %{_datadir}/%{name}/
%{_datadir}/%{name}/sample.au
%{_datadir}/%{name}/sample2.au
%{_datadir}/%{name}/sample.midi
%{_mandir}/man8/*.8*


%changelog
* Fri May 06 2011 Oden Eriksson <oeriksson@mandriva.com> 0.70-20mdv2011.0
+ Revision: 669994
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0.70-19mdv2011.0
+ Revision: 607547
- rebuild

* Mon Mar 15 2010 Oden Eriksson <oeriksson@mandriva.com> 0.70-18mdv2010.1
+ Revision: 520220
- rebuilt for 2010.1

* Mon Sep 28 2009 Olivier Blin <oblin@mandriva.com> 0.70-17mdv2010.0
+ Revision: 450363
- fix mips specific build failure (from Arnaud Patard)

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 0.70-16mdv2010.0
+ Revision: 427201
- rebuild

* Sat Apr 11 2009 Funda Wang <fwang@mandriva.org> 0.70-15mdv2009.1
+ Revision: 366321
- fix ifmask defination
- rediff modprobe patch

  + Antoine Ginies <aginies@mandriva.com>
    - rebuild

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild early 2009.0 package (before pixel changes)

* Tue Jun 10 2008 Oden Eriksson <oeriksson@mandriva.com> 0.70-12mdv2009.0
+ Revision: 217580
- rebuilt against dietlibc-devel-0.32

* Wed Mar 05 2008 Oden Eriksson <oeriksson@mandriva.com> 0.70-11mdv2008.1
+ Revision: 179512
- rebuild

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request
    - fix summary-ended-with-dot

* Wed Aug 29 2007 Oden Eriksson <oeriksson@mandriva.com> 0.70-10mdv2008.0
+ Revision: 74423
- fix build deps (libslang-static-devel)


* Wed Mar 07 2007 Michael Scherer <misc@mandriva.org> 0.70-9mdv2007.1
+ Revision: 134166
- there is no isa support on x86_64 motherboard, and it doesn't compile on it
  ,harddrake is doing fine for other card.

  + Pascal Terjan <pterjan@mandriva.org>
    - Import sndconfig

* Thu Feb 02 2006 Olivier Blin <oblin@mandriva.com> 0.70-9mdk
- make the package build (the maintainer of this package should
  really consider upgrading to kudzu-1.2.24):
  o Patch5: fix assembler errors, from kudzu-1.2.24
  o Patch6: use u_int8_t instead of byte, from kudzu-1.2.24

* Tue Jan 31 2006 Olivier Blin <oblin@mandriva.com> 0.70-8mdk
- don't overwrite modprobe.conf, write converted config in
  /etc/modprobe.d/sndconfig.conf (#12876)


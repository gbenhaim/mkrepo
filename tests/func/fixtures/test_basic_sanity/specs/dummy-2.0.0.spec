Name: dummy
Version: 2.0.0
Release:        1%{?dist}
Summary: dummy rpm for testing
License: Apache Software License 2.0

%description

%install
touch %{buildroot}/dummy_file
echo $PWD

%files
/dummy_file

# tlperl-build

This repository provides a build setup for tlperl (Perl for TeX Live).

## `sources` directory

Keep in sync with `Master/sources/tlperl` in the TeX Live Subversion repository.

## Update work

* [Download the latest stable version of Perl](https://www.perl.org/get.html).
* Search for modules in [meta::cpan](https://metacpan.org/) and download the latest version.
* Update the version in the `env:` section of `.github/workflows/main.yml`.
* Update `sources/tlperl.README`.

## Updated Module

### TeX Live 2026

* Perl 5.42.0
* Cpanel::JSON::XS 4.40
* Test::Harness 3.52
* Socket 2.040
* Test::Fatal 0.018
* URI 5.34
* HTTP::Message 7.01
* Net::HTTP 6.24
* ExtUtils-InstallPaths 0.015
* Module::Build::Tiny 0.052
* Mozilla::CA 20250602
* Test::Deep 1.205
* LWP 6.81

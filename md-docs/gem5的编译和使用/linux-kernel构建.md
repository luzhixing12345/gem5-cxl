
# linux-kernel构建

```bash
git clone https://gem5.googlesource.com/public/gem5-resources
git checkout --track origin/develop
```

```
Linux-kernel/
  |
  |___ linux-configs                           # Folder with Linux kernel configuration files
  |
  |___ README.md                               # This README file
```

## Linux Kernels

We have tested this resource compiling the following five LTS (long term support) releases of the Linux kernel:

- 4.4.186
- 4.9.186
- 4.14.134
- 4.19.83
- 5.4.49

To compile the Linux binaries, follow these instructions (assuming that you are in `src/Linux-kernel/` directory):

```bash
# will create a `linux` directory and download the initial kernel files into it.
git clone https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

cd linux
# replace version with any of the above listed version numbers
git checkout v[version]

# copy the appropriate Linux kernel configuration file from linux-configs/
cp ../linux-configs/config.[version] .config

make -j`nproc`
```

The pre-build compiled Linux binaries can be downloaded from the following links:

- [vmlinux-4.4.186](http://dist.gem5.org/dist/v22-0/kernels/x86/static/vmlinux-4.4.186)
- [vmlinux-4.9.186](http://dist.gem5.org/dist/v22-0/kernels/x86/static/vmlinux-4.9.186)
- [vmlinux-4.14.134](http://dist.gem5.org/dist/v22-0/kernels/x86/static/vmlinux-4.14.134)
- [vmlinux-4.19.83](http://dist.gem5.org/dist/v22-0/kernels/x86/static/vmlinux-4.19.83)
- [vmlinux-5.4.49](http://dist.gem5.org/dist/v22-0/kernels/x86/static/vmlinux-5.4.49)
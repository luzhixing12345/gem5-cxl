
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

官方测试并支持了如下几个版本的kernel, 正常来说更高的版本应该都可以很好的支持

- 4.4.186
- 4.9.186
- 4.14.134
- 4.19.83
- 5.4.49

假设目前已处于 `src/Linux-kernel/` 目录下

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

编译完成之后即可得到vmlinux文件,当然您也可以直接通过下面的链接下载编译完成的二进制kernel文件

- [vmlinux-4.4.186](http://dist.gem5.org/dist/v22-0/kernels/x86/static/vmlinux-4.4.186)
- [vmlinux-4.9.186](http://dist.gem5.org/dist/v22-0/kernels/x86/static/vmlinux-4.9.186)
- [vmlinux-4.14.134](http://dist.gem5.org/dist/v22-0/kernels/x86/static/vmlinux-4.14.134)
- [vmlinux-4.19.83](http://dist.gem5.org/dist/v22-0/kernels/x86/static/vmlinux-4.19.83)
- [vmlinux-5.4.49](http://dist.gem5.org/dist/v22-0/kernels/x86/static/vmlinux-5.4.49)

您可将此文件用于全系统构建时使用
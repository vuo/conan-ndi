from conans import ConanFile, tools
import platform

class NdiConan(ConanFile):
    name = 'ndi'

    source_version = '4.1'
    package_version = '0'
    version = '%s-%s' % (source_version, package_version)

    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://www.ndi.tv/sdk/'
    license = 'http://new.tk/ndisdk_license/'
    description = 'IP-based video'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')

    def source(self):
        tools.mkdir('include')
        tools.mkdir('lib')
        if platform.system() == 'Darwin':
            tools.download('http://new.tk/NDISDKAPPLE', 'ndi.pkg', sha256='6181325b0b3938a2023b7ac0002d0543f774711be46a583af5281fc5318a9095')
            self.run('pkgutil --expand ndi.pkg ndi')
            with tools.chdir('ndi/NDI_SDK_Component.pkg'):
                self.run('gzip -dc < Payload | cpio -i')
                with tools.chdir('NDI SDK for Apple'):
                    with tools.chdir('include'):
                        self.run('mv *.h ../../../../include')
                    with tools.chdir('redist'):
                        self.run('pkgutil --expand libNDI_for_Mac.pkg ndi')
                        with tools.chdir('ndi/libNDIComponent.pkg'):
                            self.run('gzip -dc < Payload | cpio -i')
                            self.run('install_name_tool -id @rpath/libndi.dylib libndi.4.dylib')
                            self.run('mv libndi.4.dylib ../../../../../../lib/libndi.dylib')
                            self.run('mv libndi_licenses.txt ../../../../../../%s.txt' % self.name)
        elif platform.system() == 'Linux':
            tools.download('http://new.tk/NDISDKLINUX', 'ndi.tar.gz', sha256='53d74b3864a8ff86ec9c5edffd60f4c9035caa544c2856b8898cc2210b407142')
            tools.untargz('ndi.tar.gz')
            self.run('chmod +x InstallNDISDK_v4_Linux.sh')
            self.run('echo y | ./InstallNDISDK_v4_Linux.sh')
            with tools.chdir('NDI SDK for Linux'):
                with tools.chdir('include'):
                    self.run('mv *.h ../../include')
                with tools.chdir('lib/x86_64-linux-gnu'):
                    self.run('mv libndi.so.4.1.6 ../../../lib/libndi.so')
            with tools.chdir('lib'):
                patchelf = self.deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
                self.run('%s --set-soname libndi.so libndi.so' % patchelf)
        elif platform.system() == 'Windows':
            tools.download('http://new.tk/NDISDK', 'ndi.exe', sha256='3e76db0fa71b13b1e8b7118c6334699d70ea00d6c6943b4dfaf1af2e2d215164')
            # @todo
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'
        elif platform.system() == 'Windows':
            libext = 'dll'

        self.copy('*.h',                src='include', dst='include')
        self.copy('libndi.%s' % libext, src='lib',     dst='lib')
        self.copy('%s.txt' % self.name, src='',        dst='license')

    def package_info(self):
        self.cpp_info.libs = ['ndi']
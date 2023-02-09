from conans import ConanFile, tools
import platform

class NdiConan(ConanFile):
    name = 'ndi'

    source_version = '5.5.3'
    package_version = '0'
    version = '%s-%s' % (source_version, package_version)

    settings = 'os'
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
            tools.download('https://downloads.ndi.tv/SDK/NDI_SDK_Mac/Install_NDI_SDK_v5_Apple.pkg', 'ndi.pkg', sha256='673bd574988719a82f43294dd5cdf5fa75395e3cefc8452d8282f347f6e45903')
            self.run('pkgutil --expand ndi.pkg ndi')
            with tools.chdir('ndi/NDI_SDK_Component.pkg'):
                self.run('gzip -dc < Payload | cpio -i')
                with tools.chdir('NDI SDK for Apple'):
                    with tools.chdir('include'):
                        self.run('mv *.h ../../../../include')
                    with tools.chdir('lib/macOS'):
                        self.run('install_name_tool -id @rpath/libndi.dylib libndi.dylib')
                        self.run('mv libndi.dylib ../../../../../lib/libndi.dylib')
                        self.run('mv libndi_licenses.txt ../../../../../%s.txt' % self.name)
        elif platform.system() == 'Linux':
            # @todo
            tools.download('…', 'ndi.tar.gz', sha256='…')
            tools.untargz('ndi.tar.gz')
            self.run('chmod +x InstallNDISDK_v4_Linux.sh')
            self.run('echo y | ./InstallNDISDK_v4_Linux.sh')
            with tools.chdir('NDI SDK for Linux'):
                with tools.chdir('include'):
                    self.run('mv *.h ../../include')
                with tools.chdir('lib/x86_64-linux-gnu'):
                    self.run('mv libndi.so.%s.* ../../../lib/libndi.so' % self.source_version)
            with tools.chdir('lib'):
                patchelf = self.deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
                self.run('%s --set-soname libndi.so libndi.so' % patchelf)
        elif platform.system() == 'Windows':
            tools.download('…', 'ndi.exe', sha256='…')
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

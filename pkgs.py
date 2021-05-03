import sys
import pkg_resources

def is_package(pkg_name):
    installed_packages = list(pkg_resources.working_set)
    for package in installed_packages:
        if package == pkg_name:
            print("found torch")
        else:
            print("nothing")

# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    is_package("torch 1.6.0+cu92")

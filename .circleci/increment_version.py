import os
import pkg_resources

if __name__ == "__main__":
    version = pkg_resources.get_distribution("argschema").version
    split_version = version.split('.')
    try:
        split_version[-1] = str(int(split_version[-1]) + 1)
    except ValueError:
        # do something about the letters in the last field of version
        pass
    new_version = '.'.join(split_version)
    os.system("sed -i \"s/version='[0-9.]*'/version='{}'/\" setup.py".format(new_version))
    os.system('git config --global user.email "forrest.collman@gmail.com"')
    os.system('git config --global user.name "CircleCi"')
    os.system('git config --global push.default matching')
    os.system("git add -u")
    os.system("git commit -m '[ci skip] Increase version to {}'"
              .format(new_version))

    os.system("git push")
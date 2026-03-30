import os
from pathlib import Path

# Example configuration file for MakeBackups showing all available options for
# reference.  Refer to example_config_simple.py instead for a quick start.
# 
# MakeBackups reads 'config.py' at startup from its current folder by default.
# Use the optional --config <path_to_file> argument to load a specific file.

# Variables may be defined for common paths.
_myname = 'Mister_Anderson'

# Environment variables may be used to create paths.
_onedrive = Path(os.environ.get('OneDrive'))
_userdir = Path(os.environ.get('UserProfile'))
_temp = Path(os.environ.get('Temp'))

# Paths may be concatenated.
_staging =  _temp / _myname
_dest = Path('//NAS/Backups') / _myname

# Optionally, the location of tar and/or age may be specified. If these are
# omitted, MakeBackups will instead look for them in the system's path.
# Typically you'd just want to omit the entry for tar so that the host system's
# default location is used.  Encrypting archives requires age.exe. If no
# encryption is performed during any of the pack steps, it does not need to be
# specified.
paths = {
    'tar': r'C:/Windows/System32/tar.exe',
    'age': _onedrive / 'age/age.exe',
}

# The preparation steps may be optionally used to create folders for staging
# archives, or clearing them. If one step encounters an error, the following
# steps are not executed and the archiving process is aborted. This may be empty
# or omitted.
prepare = [
    {'op': 'rmdir', 'path': _staging},
    {'op': 'mkdir', 'path': _staging},
]

# The finish steps also allow for folder management. These are executed after
# the archival process. If the prepare steps did not succeed, the backups will
# not be created and the finish step will be skipped. The finish steps are still
# executed if one or more archives encounter an error.  This may be empty or
# omitted.
finish = [
    {'op': 'rmdir', 'path': _staging, 'ignore_errors': True},
]

# Each backup is defined as an archive.  An archive has a 1-to-1 relationship
# with a source folder or file and a series of operations may be performed on
# each one. If an error is encountered in a archive step, the remaining steps
# for that individual archive are skipped.
archives = {

    'ExampleFolder1': [

        # The first archive step must be 'pack'. This creates the archive at the
        # location indicated by 'out'.
        {
            'op': 'pack',
            'zip': 'tar.xz', # 'zip', 'tar', 'tgz', 'tar.gz', or 'tar.xz'
            'in': _onedrive / 'ExampleFolder1',
            'out': _staging,

            # An age encryption key file is optional.  If specified, The archive
            # will be encrypted and packed in a single step. Encrypted archives
            # cannot be tested by this tool and will trigger an error if a test
            # step is attempted.
            'encryption_key': _onedrive / 'backups_key.txt',

            # This is optional and will include available stdout and stderr
            # streams from the packing process in the terminal.  This is mostly
            # for debugging a configuration since under normal conditions tar
            # and age work silently.
            'show_output': True,
        },

        # The 'move' step may be used to move the archive to a new location.  If
        # the archive will be stored on slower storage (USB flash or a network
        # share), it may be better to create the archive on a local disk and
        # then move it to the final destination.
        {'op': 'move', 'to': _dest},

        # The 'test' step will validate that the archive can be read at its
        # current location. When 'all_dates' is excluded, only the new archive
        # itself will be tested.  When 'all_dates' is true, all past archives of
        # the same name at the current location will also be tested.
        {'op': 'test'}, # Test only the new archive
        {'op': 'test', 'all_dates': True}, # Test new and past archives

        # 'cull' will remove the oldest sibiling archives at the current
        # archive's location that do not match the specified cutoff.  One or
        # both of the flags 'keep' or 'retention' must be specified.
        #
        # 'keep' specifies the maximum number of archives to leave on disk.
        #
        # 'retention' may be used to indicate a maximum age an archive may reach
        # before it is deleted.
        {'op': 'cull', 'keep': 50}, # maximum 50 archives
        {'op': 'cull', 'retention': '2Y 6M 15D'}, # 2 years, 6 months, 15 days
        {'op': 'cull', 'retention': '3Y'}, # 3 years

        # 'exec' will launch an external tool and wait for it to complete. Three
        # arguments will be passed to the tool's command line.  The first is the
        # full path to the packed archive.  The second is the filename of the
        # archive without the parent path.  The third is the name of the archive
        # as defined by this config file. 
        {
            'op': 'exec',
            'path': _onedrive / 'SFTP_to_remote_host.cmd',

            # This is optional and will include the external tool's stdout and
            # stderr output streams in the terminal.
            'show_output': True,
        },
    ],
}

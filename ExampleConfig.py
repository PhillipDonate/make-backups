import os
from pathlib import Path

# Example configuration file for MakeBackups.
# MakeBackups reads 'Config.py' at startup
# from its current folder by default.
# Use the optional --config <path_to_file>
# argument to override the default behavior.


# Variables may be defined for common paths.
_myname = 'Mister_Anderson'

# Environment variables may be used to create paths.
_onedrive = Path(os.environ.get('OneDrive'))
_userdir = Path(os.environ.get('UserProfile'))
_temp = Path(os.eviron.get('Temp'))

# Paths may be concatenated.
_staging =  _temp / _myname
_dest = Path('//NAS/Backups') / _myname

# Optionally, the locations of 7za.exe and age.exe may be
# specified.  If these are omitted, MakeBackups will instead
# look for them in the same directory that it is located.
# Encrypting archives requires age.exe, and if no encryption
# steps are performed, it does not need to exist.
paths = {
    'zipper': _onedrive / '7za.exe',
    'age': _onedrive / 'age/age.exe',
}

# The preparation steps may be optionally used to
# create folders for staging archives, or clearing them.
# If one step encounters an error, the following steps
# are not executed and the archiving process is aborted.
# This may be empty or omitted.
prepare = [
    {'op': 'rmdir', 'path': _staging},
    {'op': 'mkdir', 'path': _staging},
]

# The finish steps also allow for folder management.
# These are executed after the archival process.
# If the prepare steps did not succeed, the backups
# will not be created and the finish step will be skipped.
# The finish steps are still executed if one or more archives
# encounter an error.  This may be empty or omitted.
finish = [
    {'op': 'rmdir', 'path': _staging, 'ignore_errors': True},
]

# Each backup is defined as an archive.  An archive
# has a 1-to-1 relationship with a source folder or file
# and a series of operations may be performed on each one.
# If an error is encountered in a archive step, the remaining
# steps for that individual archive are skipped.
archives = {

    'ExampleFolder1': [

        # The first archive step must be 'pack'.
        # This creates the archive at the location
        # indicated by 'out'.
        
        {
            'op': 'pack',
            'zip': '7z', # May be 'zip' or '7z'.
            'in': _onedrive / 'ExampleFolder1',
            'out': _staging,
        },

        # The 'move' step may be used to move the
        # archive to a new location.  If the archive
        # will be stored on slower storage (USB flash
        # or a network share), it may be better to
        # create the archive on a local disk and then
        # move it to the final destination.

        {'op': 'move', 'to': _dest},

        # The 'test' step will validate that the archive
        # can be read at its current location.
        # When 'all_dates' is excluded, only the new
        # archive itself will be tested.  When 'all_dates'
        # is true, all past archives of the same name at
        # the current location will also be tested.

        {'op': 'test'}, # Test only the new archive
        {'op': 'test', 'all_dates': True}, # Test new and past archives

        # 'cull' will remove the oldest sibiling archives
        # at the current archive's location that do not
        # match the specified cutoff.
        #
        # 'keep' specifies the maximum number of archives
        # to leave on disk.
        #
        # 'retain' may be used to indicate a maximum age
        # an archive may reach before it is deleted.

        {'op': 'cull', 'keep': 50}, # maximum 50 archives
        {'op': 'cull', 'retain': '2Y 6M 15D'}, # 2 years, 6 months, 15 days
        {'op': 'cull', 'retain': '3Y'}, # 3 years
    ],

}

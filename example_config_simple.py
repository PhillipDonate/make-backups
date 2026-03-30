
# Example configuration file for MakeBackups showing the basics for a quick
# start.  Refer to example_config_full.py for full documenation.
# 
# MakeBackups reads 'config.py' at startup from its current folder by default.
# Use the optional --config <path_to_file> argument to load a specific file.

paths = {
    # age is only required for archive encryption
    'age': r'C:/Tools/age/age.exe',
}

archives = {

    # This archive is created in zip format without encryption
    'hilarious_cat_memes': [
        {
            'op': 'pack',
            'in': r'C:/My Stuff/Cat memes',
            'out': r'D:/Backups',
        },
        {
            'op': 'test',
            'all_dates': True
        },
        {
            'op': 'cull',
            'retention': '1Y'
        },
    ],

    # This archive is created in tar.xz format with asymmetric encryption.
    'super_secret_proof_of_alien_abductions': [
        {
            'op': 'pack',
            'zip': 'tar.xz',
            'in': r'C:/My Stuff/Classified Alien Files',
            'out': r'C:/Temporary Files',
            'encryption_key': r'C:/My Stuff/Classified Alien Files/public_encryption_key.txt'
        },
        {
            'op': 'move',
            'to': r'//remote_machine/Secure Backups'
        },
        {
            'op': 'cull',
            'keep': 10
        },
    ],
}

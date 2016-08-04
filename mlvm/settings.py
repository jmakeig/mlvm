# coding=utf-8

import os
import platform

HOME = os.getenv('MLVM_HOME', os.getenv('HOME') + '/.mlvm')
if HOME.startswith('~'):
    raise Exception(HOME + ': Python doesn’t do shell expansion of paths.')
#logger.debug('HOME ' + HOME)
SYSTEM = platform.system() # 'Darwin'
#logger.debug('SYSTEM ' + SYSTEM)
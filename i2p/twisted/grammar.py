# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

# General I2P grammar
i2pGrammarSource = r"""
b64char = :x ?(x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-~') -> x
b64 = <b64char+>
"""

# General BOB grammar
bobGrammarSource = i2pGrammarSource + r"""
KEYS    = b64:keys
KEY     = b64:pubkey
ERROR   = 'ERROR' ws <(~'\n' anything)*>:desc '\n' -> (False, desc)
OK      = 'OK' ws <(~'\n' anything)*>:info '\n' -> (True, info)
OK_KEY  = 'OK' ws KEY:pubkey '\n' -> (True, pubkey)
OK_KEYS = 'OK' ws KEYS:keys '\n' -> (True, keys)
DATA    = 'DATA' ws <(~'\n' anything)*>:data '\n' -> data

BOB_clear     = (ERROR | OK_KEY)
BOB_getdest   = (ERROR | OK_KEY)
BOB_getkeys   = (ERROR | OK_KEYS)
BOB_getnick   = (ERROR | OK)
BOB_inhost    = (ERROR | OK)
BOB_inport    = (ERROR | OK)
BOB_list      = ((ERROR:(result, info)           -> (result, info, []))
                |((DATA)*:data OK:(result, info) -> (result, info, data)))
BOB_newkeys   = (ERROR | OK_KEY)
BOB_option    = (ERROR | OK)
BOB_outhost   = (ERROR | OK)
BOB_outport   = (ERROR | OK)
BOB_quiet     = (ERROR | OK)
BOB_quit      = (OK)
BOB_setkeys   = (ERROR | OK)
BOB_setnick   = (ERROR | OK)
BOB_show      = (ERROR | OK)
BOB_showprops = (ERROR | OK)
BOB_start     = (ERROR | OK)
BOB_status    = (ERROR | OK)
BOB_stop      = (ERROR | OK)
BOB_verify    = (ERROR | OK)
BOB_visit     = (OK)
"""

# BOB grammar for making an I2P client tunnel
i2pClientTunnelCreatorBOBGrammarSource = bobGrammarSource + r"""
"""

# BOB grammar for making an I2P server tunnel
i2pServerTunnelCreatorBOBGrammarSource = bobGrammarSource + r"""
"""

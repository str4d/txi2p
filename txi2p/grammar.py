# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

# General I2P grammar
i2pGrammarSource = r"""
digit = anything:x ?(x in '0123456789')
number = <digit+>:ds -> int(ds)
b64char = :x ?(x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-~') -> x
b64 = <b64char+>
"""

# BOB grammar
bobGrammarSource = i2pGrammarSource + r"""
KEYS    = b64:keys
KEY     = b64:pubkey
ERROR   = 'ERROR ' <(~'\n' anything)*>:desc '\n' -> (False, desc)
OK      = 'OK ' <(~'\n' anything)*>:info '\n' -> (True, info)
OK_KEY  = 'OK ' KEY:pubkey '\n' -> (True, pubkey)
OK_KEYS = 'OK ' KEYS:keys '\n' -> (True, keys)
DATA    = 'DATA ' <(~'\n' anything)*>:data '\n' -> data

TUNNEL_STATUS = 'NICKNAME: ' <(~' ' anything)*>:nickname ' STARTING: ' <'true'|'false'>:starting ' RUNNING: ' <'true'|'false'>:running ' STOPPING: ' <'true'|'false'>:stopping ' KEYS: ' <'true'|'false'>:keys  ' QUIET: ' <'true'|'false'>:quiet ' INPORT: ' <'not_set'|number>:inport ' INHOST: ' <(~' ' anything)*>:inhost ' OUTPORT: ' <'not_set'|number>:outport ' OUTHOST: ' <(~'\n' anything)*>:outhost '\n' -> {
    'nickname': nickname,
    'starting': starting=='true',
    'running': running=='true',
    'stopping': stopping=='true',
    'keys': keys=='true',
    'quiet': quiet=='true',
    'inport': None if inport=='not_set' else int(inport),
    'inhost': inhost,
    'outport': None if outport=='not_set' else int(outport),
    'outhost': outhost
    }

DATA_TUNNEL_STATUS = 'DATA ' TUNNEL_STATUS:status -> status
OK_TUNNEL_STATUS = 'OK ' TUNNEL_STATUS:status -> (True, status)
OK_DATA_TUNNEL_STATUS = 'OK ' DATA_TUNNEL_STATUS:status -> (True, status)

versionString = <digit+ '.' digit+ '.' digit+>
BOB_init      = 'BOB ' versionString:version '\nOK\n' -> version

BOB_clear     = (ERROR | OK)
BOB_getdest   = (ERROR | OK_KEY)
BOB_getkeys   = (ERROR | OK_KEYS)
BOB_getnick   = (ERROR | OK)
BOB_inhost    = (ERROR | OK)
BOB_inport    = (ERROR | OK)
BOB_list      = ((ERROR:(result, info)                         -> (result, info, []))
                |((DATA_TUNNEL_STATUS)*:data OK:(result, info) -> (result, info, data)))
BOB_newkeys   = (ERROR | OK_KEY)
BOB_option    = (ERROR | OK)
BOB_outhost   = (ERROR | OK)
BOB_outport   = (ERROR | OK)
BOB_quiet     = (ERROR | OK)
BOB_quit      = (OK)
BOB_setkeys   = (ERROR | OK)
BOB_setnick   = (ERROR | OK)
BOB_show      = ((ERROR:(result, info)              -> (result, info, {}))
                |(OK_TUNNEL_STATUS:(result, status) -> (result, '', status)))
BOB_showprops = (ERROR | OK)
BOB_start     = (ERROR | OK)
BOB_status    = ((ERROR:(result, info)                   -> (result, info, {}))
                |(OK_DATA_TUNNEL_STATUS:(result, status) -> (result, '', status)))
BOB_stop      = (ERROR | OK)
BOB_verify    = (ERROR | OK)
BOB_visit     = (OK)

State_init      = BOB_init:version      -> receiver.initBOB(version)

State_clear     = BOB_clear:response     -> receiver.clear(*response)
State_getdest   = BOB_getdest:response   -> receiver.getdest(*response)
State_getkeys   = BOB_getkeys:response   -> receiver.getkeys(*response)
State_getnick   = BOB_getnick:response   -> receiver.getnick(*response)
State_inhost    = BOB_inhost:response    -> receiver.inhost(*response)
State_inport    = BOB_inport:response    -> receiver.inport(*response)
State_list      = BOB_list:response      -> receiver.list(*response)
State_newkeys   = BOB_newkeys:response   -> receiver.newkeys(*response)
State_option    = BOB_option:response    -> receiver.option(*response)
State_outhost   = BOB_outhost:response   -> receiver.outhost(*response)
State_outport   = BOB_outport:response   -> receiver.outport(*response)
State_quiet     = BOB_quiet:response     -> receiver.quiet(*response)
State_quit      = BOB_quit:response      -> receiver.quit(*response)
State_setkeys   = BOB_setkeys:response   -> receiver.setkeys(*response)
State_setnick   = BOB_setnick:response   -> receiver.setnick(*response)
State_show      = BOB_show:response      -> receiver.show(*response)
State_showprops = BOB_showprops:response -> receiver.showprops(*response)
State_start     = BOB_start:response     -> receiver.start(*response)
State_status    = BOB_status:response    -> receiver.status(*response)
State_stop      = BOB_stop:response      -> receiver.stop(*response)
State_verify    = BOB_verify:response    -> receiver.verify(*response)
State_visit     = BOB_visit:response     -> receiver.visit(*response)
"""

# SAM grammar
samGrammarSource = i2pGrammarSource + r"""
KEY = <(~'=' anything)*>
VALUE = (('"' <(~'"' anything)*>:value '"' -> value)
        |(<(~(' '|'\n') anything)*>))
OPTION = KEY:key '=' VALUE:value -> (key.lower(), value)
OPTIONS = (OPTION:first (' ' OPTION)*:rest -> dict([first] + rest))
          | -> {}

SAM_hello          = 'HELLO REPLY '    OPTIONS:options '\n' -> options
SAM_session_status = 'SESSION STATUS ' OPTIONS:options '\n' -> options
SAM_stream_status  = 'STREAM STATUS '  OPTIONS:options '\n' -> options
SAM_naming_reply   = 'NAMING REPLY '   OPTIONS:options '\n' -> options
SAM_dest_reply     = 'DEST REPLY '     OPTIONS:options '\n' -> options

State_hello   = SAM_hello:options          -> receiver.hello(**options)
State_create  = SAM_session_status:options -> receiver.create(**options)
State_connect = SAM_stream_status:options  -> receiver.connect(**options)
State_accept  = SAM_stream_status:options  -> receiver.accept(**options)
State_forward = SAM_stream_status:options  -> receiver.forward(**options)
State_naming  = SAM_naming_reply:options   -> receiver.lookupReply(**options)
State_dest    = SAM_dest_reply:options     -> receiver.destGenerated(**options)
State_readData = anything:data             -> receiver.dataReceived(data)

KEEPALIVE_DATA = (' '+ <(~'\n' anything)+>:data -> data) | -> None
SAM_ping = 'PING' KEEPALIVE_DATA:data '\n' -> data
SAM_pong = 'PONG' KEEPALIVE_DATA:data '\n' -> data

State_keepalive = ((SAM_ping:data -> receiver.ping(data))
                  |(SAM_pong:data -> receiver.pong(data)))
"""

from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from types import ModuleType
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import unittest

# The deployed HTTPS handler imports the on-host source-locked HTTP Handler.
# Supply its directory and bounded-copy contract without duplicating the stage.
# Live server readback separately verifies the real deployed HTTP base.
class StageBase(SimpleHTTPRequestHandler):
 def __init__(self,*args,root,personal_works_landing=False,**kw):
  self._partial_bytes=None
  super().__init__(*args,directory=str(root),**kw)
 def copyfile(self,source,outputfile):
  remaining=getattr(self,"_partial_bytes",None)
  if remaining is None:return super().copyfile(source,outputfile)
  while remaining:
   data=source.read(min(65536,remaining))
   if not data:break
   outputfile.write(data)
   remaining-=len(data)
base=ModuleType("serve_shared_shell_preview")
base.Handler=StageBase
base.inspect=lambda root:{}
sys.modules.setdefault("serve_shared_shell_preview",base)
from serve_shared_shell_preview_https import SecureStageHandler

class VergilRangeTests(unittest.TestCase):
 def test_exact_private_mp3_ranges_and_unrelated_paths(self):
  with TemporaryDirectory() as tmp:
   root=Path(tmp)
   paths=[
    'estate/media/first-readings/teatro-vergil-auto-corrected-v2.mp3',
    'estate/media/first-readings/vergil-prologue-source-aligned.mp3',
    'estate/media/first-readings/unadmitted.mp3']
   for rel in paths:
    p=root/rel
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(bytes(range(256)))
   class Quiet(SecureStageHandler):
    def log_message(self,*args):pass
   server=ThreadingHTTPServer(('127.0.0.1',0),
    partial(Quiet,root=root,personal_works_landing=False))
   worker=Thread(target=server.serve_forever,daemon=True)
   worker.start()
   try:
    base=f'http://127.0.0.1:{server.server_port}/'
    for rel in paths[:2]:
     with urlopen(Request(base+rel,method='HEAD')) as response:
      self.assertEqual(response.status,200)
      self.assertEqual(response.headers.get('Accept-Ranges'),'bytes')
     with urlopen(Request(base+rel,headers={'Range':'bytes=21-45'})) as response:
      self.assertEqual(response.status,206)
      self.assertEqual(response.headers.get('Content-Range'),'bytes 21-45/256')
      self.assertEqual(response.headers.get('Content-Length'),'25')
      self.assertEqual(response.read(),bytes(range(21,46)))
     with self.assertRaises(HTTPError) as refusal:
      urlopen(Request(base+rel,headers={'Range':'bytes=999-1000'}))
     self.assertEqual(refusal.exception.code,416)
    with urlopen(Request(base+paths[2],headers={'Range':'bytes=21-45'})) as response:
     self.assertEqual(response.status,200)
     self.assertEqual(response.read(),bytes(range(256)))
   finally:
    server.shutdown();server.server_close();worker.join(2)

if __name__=='__main__':unittest.main()

import pathlib,sys,json,shutil,subprocess,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class InstallPreflight(unittest.TestCase):
 def fixture(self,d,private=False):
  base=pathlib.Path(d)/'upstream';(base/'updater').mkdir(parents=True)
  text=(ROOT/'tests/fixtures/upstream-agent-0.9.4.cjs').read_text()
  if private:text+='\nfunction installGrokQuotaPet() {}\n'
  (base/'agent.cjs').write_text(text)
  for f in ['core.cjs','worker.cjs']:(base/'updater'/f).write_text('// fixture')
  for f in ['installed-version.json','update-settings.json']:(base/f).write_text('{}')
  return base
 def test_dry_run_does_not_mutate(self):
  with tempfile.TemporaryDirectory() as d:
   base=self.fixture(d);before={str(p.relative_to(base)):p.read_bytes() for p in base.rglob('*') if p.is_file()}
   r=subprocess.run([sys.executable,str(ROOT/'scripts/install.py'),'--base-dir',str(base),'--dry-run'],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stderr);after={str(p.relative_to(base)):p.read_bytes() for p in base.rglob('*') if p.is_file()};self.assertEqual(before,after)
 def test_private_customization_is_preserved(self):
  with tempfile.TemporaryDirectory() as d:
   base=self.fixture(d,True);before=(base/'agent.cjs').read_bytes()
   r=subprocess.run([sys.executable,str(ROOT/'scripts/install.py'),'--base-dir',str(base),'--dry-run'],capture_output=True,text=True)
   self.assertNotEqual(r.returncode,0);self.assertIn('private Grok',r.stderr);self.assertEqual(before,(base/'agent.cjs').read_bytes())
if __name__=='__main__':unittest.main()

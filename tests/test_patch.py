import pathlib,subprocess,tempfile,unittest,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Patching(unittest.TestCase):
 def test_patch_and_idempotence(self):
  with tempfile.TemporaryDirectory() as d:
   first=pathlib.Path(d)/'first.cjs';second=pathlib.Path(d)/'second.cjs'
   args=[sys.executable,str(ROOT/'guardian/patch-agent.py')]
   subprocess.run(args+[str(ROOT/'tests/fixtures/upstream-agent-0.9.4.cjs'),str(first)],check=True)
   subprocess.run(['node','--check',str(first)],check=True)
   subprocess.run(args+[str(first),str(second)],check=True)
   self.assertEqual(first.read_bytes(),second.read_bytes());self.assertIn('installStatusQuotaPet',first.read_text())
 def test_incompatible_input_is_not_written(self):
  with tempfile.TemporaryDirectory() as d:
   src=pathlib.Path(d)/'unknown.cjs';out=pathlib.Path(d)/'out.cjs';src.write_text('// changed upstream layout')
   r=subprocess.run([sys.executable,str(ROOT/'guardian/patch-agent.py'),str(src),str(out)],capture_output=True)
   self.assertNotEqual(r.returncode,0);self.assertFalse(out.exists());self.assertEqual(src.read_text(),'// changed upstream layout')
if __name__=='__main__':unittest.main()

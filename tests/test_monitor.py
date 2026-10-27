import importlib.util,pathlib,unittest
p=pathlib.Path(__file__).resolve().parents[1]/'runtime/monitor.py'
s=importlib.util.spec_from_file_location('monitor',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Events(unittest.TestCase):
 def event(self,p,typ='event_msg'):return m.classify({'type':typ,'payload':p})
 def test_real_events(self):
  for event,expected in [('task_started','thinking'),('task_complete','happy'),('turn_aborted','sad'),('error','alerting'),('request_user_input','listening')]:self.assertEqual(self.event({'type':event})[0],expected)
 def test_tools(self):
  for tool,state in [('web__run','searching'),('request_user_input_async','listening'),('image_gen__imagegen','spawning'),('apply_patch','writing'),('spawn_agent','orbit'),('wait_threads','humming'),('exec_command','working')]:self.assertEqual(self.event({'type':'custom_tool_call','name':'exec','input':'await tools.'+tool+'({})'},'response_item')[0],state)
 def test_arguments_not_content_classified(self):self.assertEqual(self.event({'type':'custom_tool_call','name':'exec','input':'await tools.exec_command({cmd:"echo request_user_input"})'},'response_item')[0],'working')
 def test_tool_error(self):self.assertEqual(self.event({'type':'function_call_output','output':{'exit_code':2}},'response_item')[0],'alerting')
 def test_string_tool_error(self):self.assertEqual(self.event({'type':'function_call_output','output':'{"exit_code":1}'},'response_item')[0],'alerting')
 def test_unknown_is_not_failure(self):self.assertIsNone(self.event({'type':'token_count'}))
 def test_normalized_names_only(self):self.assertNotIn('SELECT id,title',p.read_text())
 def test_final(self):self.assertEqual(self.event({'type':'message','role':'assistant','phase':'final_answer'},'response_item')[0],'happy')
if __name__=='__main__':unittest.main()

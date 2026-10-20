import sys,unittest,tempfile,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import prepare
import knowledge

class InputTests(unittest.TestCase):
 def test_plain_text_no_fabricated_time(self):
  rows=prepare.parse_text('面试官：介绍一下项目。\n候选人：我负责报名接口。','.txt')
  self.assertEqual(len(rows),2);self.assertIsNone(rows[0]['start_seconds']);self.assertEqual(rows[1]['speaker'],'candidate')
 def test_timestamp_and_unknown_speaker(self):
  rows=prepare.parse_text('[01:02] 面试官：有数据吗？\n[01:05] 没测过。','.txt')
  self.assertEqual(rows[0]['start_seconds'],62);self.assertEqual(rows[1]['speaker'],'unknown')
 def test_srt_multiline(self):
  rows=prepare.parse_text('1\n00:00:05,500 --> 00:00:08,000\n候选人：用了缓存，\n没测效果。\n\n2\n00:00:09,000 --> 00:00:10,000\n面试官：为什么？\n','.srt')
  self.assertEqual(len(rows),2);self.assertEqual(rows[0]['start_seconds'],5.5);self.assertIn('没测效果',rows[0]['text'])
 def test_tsv_from_transcriber(self):
  rows=prepare.parse_text('start\tend\ttext\n1.20\t2.30\t数据库唯一约束\n','.tsv')
  self.assertEqual(rows[0]['start_seconds'],1.2);self.assertEqual(rows[0]['speaker'],'unknown')
 def test_empty_rejected(self):
  with self.assertRaises(ValueError):prepare.parse_text(' \n','.txt')
 def test_prepare_without_external_account(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'input.txt').write_text('面试官：效果？\n候选人：没有测试。')
   result=prepare.build_bundle(p/'input.txt',p/'out')
   data=json.loads((p/'out/review-input.json').read_text());self.assertEqual(len(data['segments']),2);self.assertEqual(data['references'],[]);self.assertTrue((p/'out/review-brief.md').exists())
 def test_no_overwrite(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'in.txt').write_text('测试');prepare.build_bundle(p/'in.txt',p/'out')
   with self.assertRaises(FileExistsError):prepare.build_bundle(p/'in.txt',p/'out')

class KnowledgeTests(unittest.TestCase):
 def test_local_context_relative_and_traceable(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'notes.md').write_text('练习项目：实现报名，不含性能实测。')
   docs,warnings=knowledge.collect({'sources':[{'type':'local','path':'notes.md','purpose':'personal_facts'}]},p)
   self.assertEqual(len(docs),1);self.assertEqual(docs[0]['purpose'],'personal_facts');self.assertIn('notes.md',docs[0]['locator']);self.assertEqual(warnings,[])
 def test_optional_failure_is_explicit(self):
  docs,warnings=knowledge.collect({'sources':[{'type':'local','path':'missing.md'}]},ROOT)
  self.assertEqual(docs,[]);self.assertEqual(warnings[0]['status'],'unavailable')
 def test_disabled_source_never_executes(self):
  docs,warnings=knowledge.collect({'sources':[{'type':'feishu_cli','enabled':False,'doc':'x'}]},ROOT)
  self.assertEqual(docs,[]);self.assertEqual(warnings,[])
 def test_cli_error_json_not_read_as_content(self):
  with self.assertRaises(ValueError):knowledge.parse_cli_document('{"ok":false,"error":{"message":"login required"}}')
 def test_real_cli_response_shape(self):
  s=knowledge.parse_cli_document(json.dumps({'ok':True,'data':{'document':{'content':'# 本人的项目\n未做压测'}}}))
  self.assertIn('未做压测',s)
 def test_mcp_error_not_read_as_document(self):
  with self.assertRaises(ValueError):knowledge.parse_mcp_document({'isError':True,'content':[{'type':'text','text':'401'}]})
 def test_mcp_doc_body(self):
  s=knowledge.parse_mcp_document({'content':[{'type':'text','text':json.dumps({'title':'示例','body':'用户自己的项目说明'})}]})
  self.assertEqual(s,'用户自己的项目说明')
 def test_mcp_write_tool_rejected(self):
  with self.assertRaises(ValueError):knowledge.validate_mcp_call('yuque_update_doc',{'repo_id':'x','doc_id':1})
 def test_token_not_expanded_in_saved_source(self):
  import os
  os.environ['TEST_RECAP_SECRET']='test-secret-never-save'
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)
   docs,warnings=knowledge.collect({'sources':[{'type':'mcp','command':'no-such-program-recap','env':{'YUQUE_TOKEN_ENV':'TEST_RECAP_SECRET'},'tool':'yuque_get_doc','arguments':{'repo_id':'demo/book','doc_id':1}}]},p)
   self.assertNotIn('test-secret-never-save',json.dumps([docs,warnings]))

if __name__=='__main__':unittest.main()

class RegressionTests(unittest.TestCase):
 def test_transcriber_quotes_roundtrip(self):
  import io,csv,transcribe
  txt,srt,tsv=io.StringIO(),io.StringIO(),io.StringIO();writer=csv.writer(tsv,delimiter='\t',lineterminator='\n');writer.writerow(['start','end','text'])
  transcribe.write_segment(txt,writer,srt,1,0,1,'"first unclosed quote')
  transcribe.write_segment(txt,writer,srt,2,1,2,'second segment')
  rows=prepare.parse_text(tsv.getvalue(),'.tsv');self.assertEqual(len(rows),2);self.assertEqual(rows[0]['text'],'"first unclosed quote')
 def test_partially_broken_srt_rejected(self):
  with self.assertRaises(ValueError):prepare.parse_text('1\n00:00:00,000 --> 00:00:01,000\n面试官：问题？\n\n2\n00:00:02,000 -- 00:00:03,000\n候选人：回答。\n','.srt')
 @unittest.skipIf(__import__('os').name=='nt','POSIX permission test')
 def test_knowledge_export_private_permissions(self):
  import os
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'notes.md').write_text('模拟个人材料');(p/'config.json').write_text(json.dumps({'sources':[{'type':'local','path':'notes.md'}]}))
   result=subprocess.run([sys.executable,str(ROOT/'scripts/knowledge.py'),'--config',str(p/'config.json'),'--output',str(p/'out.json')],capture_output=True,text=True)
   self.assertEqual(result.returncode,0);self.assertEqual((p/'out.json').stat().st_mode&0o777,0o600)

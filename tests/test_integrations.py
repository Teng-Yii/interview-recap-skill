import importlib.util,json,os,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import knowledge

class CliTransportTests(unittest.TestCase):
 @unittest.skipIf(os.name=='nt','Executable test fixture uses a POSIX shebang; production invokes lark-cli normally')
 def test_feishu_runs_fixed_read_command_without_shell(self):
  with tempfile.TemporaryDirectory() as t:
   cli=Path(t)/'lark-cli';cli.write_text('#!'+sys.executable+'\nimport sys,json\nassert sys.argv[1:]==["docs","+fetch","--doc","https://demo.feishu.cn/docx/mock","--doc-format","markdown","--as","user"]\nprint(json.dumps({"ok":True,"data":{"document":{"content":"模拟个人笔记"}}}))\n');cli.chmod(0o700)
   s=knowledge.feishu_read({'command':str(cli),'doc':'https://demo.feishu.cn/docx/mock'})
   self.assertEqual(s,'模拟个人笔记')
 def test_dry_run_is_not_document(self):
  with self.assertRaises(ValueError):knowledge.parse_cli_document('{"ok":true,"dry_run":true,"data":{"api":[]}}')

@unittest.skipUnless(importlib.util.find_spec('mcp'),'Install requirements-mcp.txt to exercise actual MCP transport')
class McpTransportTests(unittest.TestCase):
 def source(self):return {'type':'mcp','command':sys.executable,'args':[str(ROOT/'tests/fixtures/read_only_mcp.py')],'tool':'yuque_get_doc','arguments':{'repo_id':'demo/book','doc_id':'one'},'purpose':'personal_facts','timeout_seconds':10}
 def test_real_stdio_handshake_discovery_and_read(self):
  s=self.source();docs,warnings=knowledge.collect({'sources':[s]},ROOT)
  self.assertEqual(warnings,[]);self.assertEqual(len(docs),1);self.assertIn('没有性能数据',docs[0]['text']);self.assertNotIn('command',docs[0])
 def test_probe_reads_schema_not_documents(self):
  result=knowledge.mcp_read(self.source(),probe=True)
  self.assertEqual(result[0]['name'],'yuque_get_doc');self.assertIn('doc_id',result[0]['inputSchema']['properties'])
 def test_unadvertised_tool_falls_back(self):
  s=self.source();s['tool']='yuque_get_document';docs,warnings=knowledge.collect({'sources':[s]},ROOT)
  self.assertEqual(docs,[]);self.assertEqual(len(warnings),1)

if __name__=='__main__':unittest.main()

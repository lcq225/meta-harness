# PyPI/GitHub 安全发布流程

## 严重安全事件处理

### 已发生：PyPI Token 泄漏

**泄漏文件：** `.pypirc`

**风险：** 攻击者可能使用该 token 发布恶意包

**必须操作：**

1. **立即撤销 PyPI token**
   - 登录 https://pypi.org/manage/account/
   - 进入 "API tokens" 页面
   - 删除泄漏的 token

2. **检查已发布的包**
   - 确认 meta-harness 版本未被篡改
   - 如有异常，联系 PyPI 支持

---

## 安全发布流程（必须遵守）

### 发布前检查清单

```bash
# 1. 检查是否有敏感文件
git status

# 2. 确认没有以下文件被追踪
# - .pypirc
# - .env
# - *.pem, *.key
# - credentials.json
# - secrets/

# 3. 使用 grep 搜索敏感关键词
grep -r "pypi-AgEI" . --include="*"
grep -r "password" . --include="*.json" --include="*.yml"
```

### PyPI Token 管理

**正确方式：**

1. **使用 CI/CD 环境变量**
   - 在 GitHub Secrets 中添加 `PYPI_API_TOKEN`
   - 在 GitHub Actions 中使用 `${{ secrets.PYPI_API_TOKEN }}`

2. **本地测试时使用 token 文件**
   ```bash
   # 创建 ~/.pypirc (用户主目录)
   # 注意：不要提交到仓库！
   ```

**禁止：**
- [FAIL] 禁止将 `.pypirc` 提交到仓库
- [FAIL] 禁止在 GitHub Actions workflow 中硬编码 token
- [FAIL] 禁止在任何配置文件中包含真实 token

### GitHub Actions 发布模板

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

---

## 验证步骤

发布后执行：
```bash
# 1. 检查 GitHub secrets
gh api repos/OWNER/REPO/actions/secrets

# 2. 确认 token 未在代码中
grep -r "pypi-AgEI" . --include="*.py" --include="*.yml"

# 3. 检查最近提交
git log --oneline -5
git show --stat HEAD
```

---

**最后更新：** 2026-04-01
**原因：** PyPI Token 泄漏事件